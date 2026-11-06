"""
OpenNebula Driver for Linstor
Copyright 2026 LINBIT USA LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Backups of VMs with LINSTOR disks.

Non-interactive backups are done by OpenNebula's shared TM driver. Interactive backups (BACKUP_CONFIG/INTERACTIVE)
are exported through OneBEX with the linstor exporter (onebex/exporters/linstor.rb):
- a changed block tracking (CBT) snapshot of all disks, taken together
- a CBT session per disk: the snapshot restored into a temporary resource that is readable (read-only) on the VM's
  host, its DRBD device is the source of the export
- the exports get the extents of the snapshot in a file, as ovirt-imageio reports them (they cover the disk without
  gaps): incremental exports the changed ones, if the snapshot's changes start at the snapshot of the previous backup
  of the chain, else (and for full backups) the whole disk is exported, without the never written (zero) extents
- the sessions and snapshots are removed once OneBEX finished

Without CBT (python-linstor, controller or DRBD/storage too old for it) the backup takes a plain snapshot, restores
it into a temporary resource that is available on the VM's host and always exports the whole disk (also as an
increment of a chain).
"""
import base64
import contextlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from typing import IO, Any, Dict, Iterator, List, Optional, Tuple, Union

import linstor.sharedconsts as apiconsts
from linstor import ApiCallResponse, LinstorError, MultiLinstor

from one import consts, util
from one.datastore import Datastore
from one.extender import connect, get_device_path, get_rsc_name, make_resource, wait_resource_ready
from one.vm import Vm

# OneBEX's TM client, the hosts get it with the other remotes (onehost sync)
ONEBEX_CLIENT = os.path.join(util.REMOTES_DIR, "tm", "lib", "onebex.rb")
DEFAULT_REMOTE_TM_LIB_DIR = "/var/tmp/one/tm/lib"
ONEBEX_START = "TransferManager::OneBEX.start(:vm_id => ARGV[0], :ds_id => ARGV[1], :backup_dir => ARGV[2])"
DATASTORE_CONF = os.path.join(util.REMOTES_DIR, "etc", "datastore", "datastore.conf")
VIRSH = "virsh -c qemu:///system"

EXPORTER = "linstor"
# resource definition property with the last successful interactive backup of the resource (JSON)
BACKUP_STATE_PROP = "Aux/one/backup-cbt"
EXTENTS_PAGE_SIZE = 50000
# REST API version of the controllers with CBT snapshots and sessions
CBT_REST_API_VERSION = "1.30.0"
# starting a CBT session on a thick LVM pool copies the whole snapshot before the request returns
SESSION_START_TIMEOUT = 4 * 3600


class BackupArgs(object):
    """Arguments of the TM backup actions: host:remote_dir DISK_ID:...:DISK_ID deploy_id bjid vmid dsid"""

    def __init__(self, argv: List[str]) -> None:
        self.host = util.arg_host(argv[1]).strip()
        self.vm_dir = util.arg_path(argv[1]).strip()
        self.disk_ids = [x for x in argv[2].split(":") if x]
        self.deploy_id = argv[3]
        self.vm_id = int(argv[5])
        self.system_ds_id = os.path.basename(os.path.dirname(self.vm_dir))

        base_path = backup_base_path()
        self.base_dir = "{}/{}".format(base_path, self.vm_id) if base_path else None
        self.backup_dir = "{}/backup".format(self.base_dir or self.vm_dir)


class _Disk(object):
    def __init__(self, disk_id: str, rsc_name: str, datastore: Datastore, vm_id: int) -> None:
        """
        :param disk_id: OpenNebula disk id
        :param rsc_name: LINSTOR resource of the disk
        :param datastore: datastore with the LINSTOR controllers of the resource
        :param vm_id: VM of the backup
        """
        self.disk_id = disk_id
        self.rsc_name = rsc_name
        self.datastore = datastore
        self.cbt = False  # True once a CBT snapshot was taken
        self.session = None  # CbtSession, once started
        # temporary resource the snapshot is restored into without CBT
        self.backup_rsc_name = "{}-vm{}-disk{}".format(consts.BACKUP_PREFIX, vm_id, disk_id)

    @property
    def cluster(self) -> Tuple[str, Optional[str]]:
        return self.datastore.linstor_controllers, self.datastore.linstor_controller_auth_token


def backup_base_path() -> Optional[str]:
    """
    Returns BACKUP_BASE_PATH as OpenNebula's TM drivers see it (Datastore.load_env: datastore.conf, else the
    environment). If set, the backup directory on the host is <BACKUP_BASE_PATH>/<vm id>/backup instead of
    <vm dir>/backup.
    """
    try:
        with open(DATASTORE_CONF) as conf:
            for line in conf:
                match = re.match(r'\s*(?:export\s+)?BACKUP_BASE_PATH="?([^"\n]+)"?\s*$', line)
                if match:
                    return match.group(1)
    except OSError:
        pass
    return os.environ.get("BACKUP_BASE_PATH") or None


def remote_tm_lib_dir() -> str:
    """
    Returns the directory of the TM driver libraries on the hosts, OneBEX's TM client is started from there.
    OpenNebula moved it (/var/tmp/one/tm/lib in 7.4, /var/lib/one-remotes/tm/lib later), the client knows the
    directory of its version (REMOTE_LIB_DIR).
    """
    try:
        with open(ONEBEX_CLIENT) as client:
            match = re.search(r"REMOTE_LIB_DIR\s*=\s*['\"]([^'\"]+)['\"]", client.read())
            if match:
                return match.group(1)
    except OSError:
        pass
    return DEFAULT_REMOTE_TM_LIB_DIR


def forward_to_shared(action: str, vm_xml: str) -> None:
    """Runs the action of OpenNebula's shared TM driver, which does the non-interactive backups."""
    shared_action = os.path.join(util.REMOTES_DIR, "tm", "shared", action)
    rc = subprocess.run([shared_action] + sys.argv[1:], input=vm_xml.encode()).returncode
    if rc != 0:
        sys.exit(rc)


def incremental_base(state_value: Optional[str], vm_id: int, last_increment_id: int) -> Optional[str]:
    """
    Returns the CBT id the changes of an incremental backup have to start at: the id of the snapshot of the last
    successful backup of the resource, if that backup is the last increment of the VM's chain.

    :param state_value: value of the resource definition property BACKUP_STATE_PROP
    :param vm_id: VM of the backup
    :param last_increment_id: last increment of the VM's backup chain (BACKUP_CONFIG/LAST_INCREMENT_ID)
    :return: CBT id or None if an incremental backup isn't possible
    """
    try:
        state = json.loads(state_value) if state_value else {}
    except ValueError:
        return None
    if not isinstance(state, dict):
        return None
    if state.get("vm") != vm_id or state.get("increment") != last_increment_id:
        return None
    return state.get("cbt_id") or None


def _by_cluster(disks: List[_Disk]) -> Dict[Tuple[str, Optional[str]], List[_Disk]]:
    clusters = {}
    for disk in disks:
        clusters.setdefault(disk.cluster, []).append(disk)
    return clusters


def _raise_if_error(replies: list, msg: str) -> None:
    errors = [str(x) for x in replies if isinstance(x, ApiCallResponse) and x.is_error()]
    if errors:
        raise LinstorError("{}: {}".format(msg, "; ".join(errors)))


def _result(replies: list, msg: str) -> Any:
    """Returns the reply that isn't an ApiCallResponse (the requested object), raises the errors otherwise."""
    for reply in replies:
        if not isinstance(reply, ApiCallResponse):
            return reply
    _raise_if_error(replies, msg)
    raise LinstorError("{}: no response".format(msg))


def _linstor_disks(target_vm: Vm, args: BackupArgs) -> List[_Disk]:
    disks = []
    datastores = {}
    for disk_id in args.disk_ids:
        if target_vm.disk_source(disk_id):
            if target_vm.tm_mad(disk_id) != "linstor":
                raise RuntimeError(
                    "Disk {} of VM {} is not a LINSTOR disk ({}), interactive backups need LINSTOR disks".format(
                        disk_id, args.vm_id, target_vm.tm_mad(disk_id)))
            ds_id = target_vm.disk_datastore_id(disk_id)
        else:
            ds_id = args.system_ds_id  # volatile disk
        if ds_id not in datastores:
            datastores[ds_id] = Datastore(util.show_ds(ds_id))
        disks.append(_Disk(disk_id, get_rsc_name(target_vm, disk_id), datastores[ds_id], args.vm_id))
    return disks


def _virsh(host: str, command: str, deploy_id: str) -> bool:
    rc, _, _ = util.ssh_run(host, "{} {} {}".format(VIRSH, command, shlex.quote(deploy_id)))
    return rc == 0


@contextlib.contextmanager
def _frozen(host: str, deploy_id: str, mode: str) -> Iterator[None]:
    """
    Freezes the VM's file systems (AGENT) or suspends the VM (SUSPEND), TRY tries both, NONE does nothing.
    """
    thaw = None
    if mode in ("AGENT", "TRY"):
        if _virsh(host, "domfsfreeze", deploy_id):
            thaw = "domfsthaw"
        elif mode == "AGENT":
            raise RuntimeError("Could not freeze the file systems of VM {}".format(deploy_id))
    if thaw is None and mode in ("SUSPEND", "TRY"):
        if not _virsh(host, "suspend", deploy_id):
            raise RuntimeError("Could not suspend VM {}".format(deploy_id))
        thaw = "resume"
    try:
        yield
    finally:
        if thaw and not _virsh(host, thaw, deploy_id):
            raise RuntimeError("Could not {} VM {}".format(thaw, deploy_id))


def _remove_snapshot(lin: MultiLinstor, rsc_name: str, snap_name: str, cbt_session: bool) -> None:
    """Finishes the snapshot's CBT session (if it may have one) and deletes the snapshot, errors are logged."""
    util.log_info("Removing backup snapshot {}/{}".format(rsc_name, snap_name))
    if cbt_session and hasattr(lin, "snapshot_cbt_session_finish"):
        replies = lin.snapshot_cbt_session_finish(rsc_name, snap_name)
        if not lin.all_api_responses_no_error(replies):
            util.log_info("No CBT session closed for {}/{}: {}".format(rsc_name, snap_name, replies[0]))
    replies = lin.snapshot_delete(rsc_name, snap_name)
    if not lin.all_api_responses_no_error(replies):
        util.log_error("Could not delete backup snapshot {}/{}: {}".format(rsc_name, snap_name, replies[0]))


def _remove_backup_resources(lin: MultiLinstor, disks: List[_Disk]) -> None:
    """Deletes the temporary resources (backups without CBT) of the disks that exist, errors are logged."""
    names = {x.backup_rsc_name for x in disks}
    if not names:
        return  # an empty filter would list all resource definitions
    rsc_dfns = lin.resource_dfn_list_raise(
        query_volume_definitions=False, filter_by_resource_definitions=sorted(names)).resource_definitions
    # old controllers ignore the filter
    for rsc_dfn in [x for x in rsc_dfns if x.name in names]:
        util.log_info("Deleting temporary backup resource {}".format(rsc_dfn.name))
        replies = lin.resource_dfn_delete(rsc_dfn.name)
        if not lin.all_api_responses_no_error(replies):
            util.log_error("Could not delete temporary backup resource {}: {}".format(rsc_dfn.name, replies[0]))


def _remove_stale(disks: List[_Disk]) -> None:
    """
    Removes what a failed or killed earlier backup left: temporary resources (first, a ZFS clone keeps its
    snapshot) and backup snapshots with their CBT sessions.
    """
    for cluster, group in _by_cluster(disks).items():
        with connect(*cluster) as lin:
            _remove_backup_resources(lin, group)
            rsc_names = {x.rsc_name for x in group}
            snapshots = lin.snapshot_dfn_list_raise(filter_by_resources=sorted(rsc_names)).snapshots
            for snap in snapshots:
                # old controllers ignore the filter
                if snap.rsc_name in rsc_names and snap.snapshot_name.startswith(consts.BACKUP_PREFIX + "-"):
                    _remove_snapshot(lin, snap.rsc_name, snap.snapshot_name, cbt_session=True)


def _cbt_supported(lin: MultiLinstor) -> bool:
    """
    :return: True if the client and the controllers support CBT snapshots (DRBD and storage are checked by the
             snapshot itself)
    """
    if not hasattr(lin, "snapshot_cbt_session_start"):
        util.log_info("python-linstor without CBT support, interactive backups export whole disks")
        return False
    if lin.api_version_smaller(CBT_REST_API_VERSION):
        util.log_info("LINSTOR controller without CBT support (REST API < {}), interactive backups export whole "
                      "disks".format(CBT_REST_API_VERSION))
        return False
    return True


def _create_snapshots(disks: List[_Disk], snap_name: str) -> None:
    """
    Creates one snapshot of all disks of a LINSTOR cluster (I/O of all of them suspended together): a CBT snapshot
    if the cluster supports it, else a plain one.
    """
    for cluster, group in _by_cluster(disks).items():
        with connect(*cluster) as lin:
            rsc_names = [x.rsc_name for x in group]
            cbt = _cbt_supported(lin)
            if cbt:
                util.log_info("Creating CBT snapshot {} of {}".format(snap_name, ", ".join(rsc_names)))
                replies = lin.snapshot_create_multi(None, rsc_names, snap_name, cbt=True)
                not_supported = getattr(apiconsts, "FAIL_CBT_NOT_SUPPORTED", None)
                if not_supported and any(
                        isinstance(x, ApiCallResponse) and x.is_error(not_supported) for x in replies):
                    util.log_info("CBT not supported for {} ({}), interactive backups export whole disks".format(
                        ", ".join(rsc_names), "; ".join(str(x) for x in replies if x.is_error())))
                    cbt = False
                else:
                    _raise_if_error(replies, "Could not create CBT snapshot {} of {}".format(
                        snap_name, ", ".join(rsc_names)))
            if not cbt:
                util.log_info("Creating snapshot {} of {}".format(snap_name, ", ".join(rsc_names)))
                _raise_if_error(
                    lin.snapshot_create_multi(None, rsc_names, snap_name),
                    "Could not create snapshot {} of {}".format(snap_name, ", ".join(rsc_names)))
            for disk in group:
                disk.cbt = cbt


def _write_extents(
        lin: MultiLinstor, rsc_name: str, snap_name: str, volume_number: int, base_cbt_id: Optional[str],
        path: str) -> bool:
    """
    Writes the extents of the CBT snapshot's volume to path, one "<start> <length> <dirty> <zero>" line (bytes, flags 0
    or 1) per extent. They cover the volume without gaps, as the extents of ovirt-imageio do. With base_cbt_id (an
    incremental backup) the dirty extents changed since that CBT snapshot. Without it (a full backup) all extents are
    dirty and the zero ones were never written.

    :return: False if the extents are of no use: the snapshot's changes don't start at base_cbt_id (an incremental
             backup isn't possible then), or LINSTOR does not know the never written extents (a full backup reads the
             whole disk then)
    """
    full = base_cbt_id is None
    if full and not hasattr(lin, "CBT_EXTENTS_MODE_ZERO"):
        util.log_info("python-linstor without zero extents, {}/{} is exported whole".format(rsc_name, snap_name))
        return False
    offset = 0
    with open(path, "w") as out:
        while True:
            if full:
                replies = lin.snapshot_cbt_extents(rsc_name, snap_name, volume_number, offset, EXTENTS_PAGE_SIZE,
                                                   mode=lin.CBT_EXTENTS_MODE_ZERO)
            else:
                replies = lin.snapshot_cbt_extents(rsc_name, snap_name, volume_number, offset, EXTENTS_PAGE_SIZE)
            if any(isinstance(x, ApiCallResponse) and x.is_error(apiconsts.FAIL_CBT_FULL_BACKUP_REQUIRED)
                   for x in replies):
                if full:
                    util.log_info("{}/{} does not tell its never written extents".format(rsc_name, snap_name))
                else:
                    util.log_info("{}/{} has no changes to base an incremental backup on".format(rsc_name, snap_name))
                return False
            page = _result(replies, "Could not get the extents of {}/{}".format(rsc_name, snap_name))
            if not full and page.base_cbt_id != base_cbt_id:
                util.log_info("Changes of {}/{} start at CBT id {}, the last backup is {}".format(
                    rsc_name, snap_name, page.base_cbt_id, base_cbt_id))
                return False
            for extent in page.extents:
                out.write("{} {} {:d} {:d}\n".format(extent.start, extent.length, full or extent.dirty, extent.zero))
            if page.next_offset is None:
                return True
            offset = page.next_offset


def _restore_export(disk: _Disk, snap_name: str, args: BackupArgs, target_vm: Vm) -> Dict[str, Any]:
    """
    Without CBT: restores the snapshot into the temporary resource disk.backup_rsc_name, makes it available on the
    VM's host and returns the interactive_exports.json entry, the whole disk.
    """
    util.log_info("Restoring {}/{} into {} for the backup".format(disk.rsc_name, snap_name, disk.backup_rsc_name))
    backup_res = make_resource(disk.rsc_name, *disk.cluster).restore_from_snapshot(snap_name, disk.backup_rsc_name)
    backup_res.activate(args.host)
    wait_resource_ready(backup_res)
    export = {
        "exporter": EXPORTER,
        "source": get_device_path(backup_res),
        "format": (target_vm.disk_format(disk.disk_id) or "raw").lower(),
        "mode": "full",
        # the exporter reads the device size
        "resource": disk.rsc_name,
        "snapshot": snap_name,
    }
    return export


def _start_exports(
        disks: List[_Disk], snap_name: str, args: BackupArgs, target_vm: Vm,
        work_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    Makes each disk's snapshot readable on the VM's host (CBT session, else a restored temporary resource) and
    returns the interactive_exports.json entries. Exports of CBT sessions get their extents (see _write_extents) in
    <work_dir>/disk.<id>.extents, if LINSTOR knows them.
    """
    incremental = target_vm.backup_incremental_mode and target_vm.backup_last_increment_id >= 0
    exports = {}
    for cluster, group in _by_cluster(disks).items():
        with connect(*cluster, timeout=SESSION_START_TIMEOUT) as lin:
            for disk in group:
                if not disk.cbt:
                    exports[disk.disk_id] = _restore_export(disk, snap_name, args, target_vm)
                    continue

                disk.session = _result(
                    lin.snapshot_cbt_session_start(disk.rsc_name, snap_name, args.host),
                    "Could not start the CBT session of {}/{} on {}".format(disk.rsc_name, snap_name, args.host))
                volume = disk.session.volumes[0]
                export = {
                    "exporter": EXPORTER,
                    "source": volume.device_path,
                    # the device holds the disk's image as is (raw, or e.g. a qcow2 image on the block device)
                    "format": (target_vm.disk_format(disk.disk_id) or "raw").lower(),
                    "mode": "full",
                    # the export has the device's size, it can be larger than the disk size OpenNebula shows
                    "size_bytes": volume.volume_size,
                    "resource": disk.rsc_name,
                    "snapshot": snap_name,
                }

                extents_name = "disk.{}.extents".format(disk.disk_id)
                extents_path = os.path.join(work_dir, extents_name)
                if incremental:
                    rsc_dfns = lin.resource_dfn_list_raise(
                        query_volume_definitions=False,
                        filter_by_resource_definitions=[disk.rsc_name]).resource_definitions
                    state_value = next((x.properties.get(BACKUP_STATE_PROP) for x in rsc_dfns
                                        if x.name == disk.rsc_name), None)
                    base_cbt_id = incremental_base(state_value, args.vm_id, target_vm.backup_last_increment_id)
                    if base_cbt_id and _write_extents(lin, disk.rsc_name, snap_name, volume.volume_number,
                                                      base_cbt_id, extents_path):
                        export["mode"] = "incremental"
                    else:
                        util.log_info("Disk {} of VM {}: exporting all blocks, the last backup of {} isn't the "
                                      "base of this increment".format(disk.disk_id, args.vm_id, disk.rsc_name))
                if export["mode"] == "full" and not _write_extents(lin, disk.rsc_name, snap_name,
                                                                   volume.volume_number, None, extents_path):
                    # the whole disk
                    with contextlib.suppress(FileNotFoundError):
                        os.unlink(extents_path)
                if os.path.exists(extents_path):
                    export["extents"] = "{}/{}".format(args.backup_dir, extents_name)

                exports[disk.disk_id] = export
    return exports


def _upload(host: str, data: Union[bytes, IO[bytes]], remote_path: str) -> None:
    """
    :param data: data or open binary file
    """
    rc, _, err = util.ssh_run(host, "cat > {}".format(shlex.quote(remote_path)), stdin=data)
    if rc != 0:
        raise RuntimeError("Could not write {} on {}: {}".format(remote_path, host, err.strip()))


def _prepare_backup_dir(args: BackupArgs, vm_xml: str, exports: Dict[str, Dict[str, Any]], work_dir: str) -> None:
    """Writes vm.xml, the extents files and interactive_exports.json to the backup directory on the VM's host."""
    rc, _, err = util.ssh_run(args.host, "rm -rf {d} && mkdir -p {d}".format(d=shlex.quote(args.backup_dir)))
    if rc != 0:
        raise RuntimeError("Could not create {} on {}: {}".format(args.backup_dir, args.host, err.strip()))

    _upload(args.host, base64.encodebytes(vm_xml.encode()), "{}/vm.xml".format(args.backup_dir))
    for name in sorted(os.listdir(work_dir)):
        with open(os.path.join(work_dir, name), "rb") as extents:
            _upload(args.host, extents, "{}/{}".format(args.backup_dir, name))
    _upload(args.host, json.dumps(exports, indent=4, sort_keys=True).encode(),
            "{}/interactive_exports.json".format(args.backup_dir))


def _run_onebex(args: BackupArgs) -> None:
    """Starts the exports in OneBEX on the VM's host and waits until the backup application finished them."""
    cmd = " ".join(shlex.quote(x) for x in [
        "ruby", "-I", remote_tm_lib_dir(), "-r", "onebex", "-e", ONEBEX_START,
        str(args.vm_id), args.system_ds_id, args.backup_dir])
    util.log_info("Waiting for the interactive backup of VM {} on {}".format(args.vm_id, args.host))
    rc, out, err = util.ssh_run(args.host, cmd)
    if rc != 0:
        # the first line has the reason, the rest is the Ruby backtrace (ssh_run logged all of it)
        reason = ((err or out).strip().splitlines() or ["exit code {}".format(rc)])[0]
        raise RuntimeError("Interactive backup of VM {} failed: {}".format(args.vm_id, reason))


def _save_backup_state(disks: List[_Disk], vm_id: int, increment_id: int) -> None:
    """
    Records the backup as the last successful backup of the disks' resources. A failure is only logged: the next
    backup then doesn't find this backup as its base and exports all blocks.
    """
    for cluster, group in _by_cluster([x for x in disks if x.session]).items():
        with connect(*cluster) as lin:
            for disk in group:
                state = json.dumps({"vm": vm_id, "increment": increment_id, "cbt_id": disk.session.cbt_id},
                                   sort_keys=True)
                replies = lin.resource_dfn_modify(disk.rsc_name, {BACKUP_STATE_PROP: state})
                if not lin.all_api_responses_no_error(replies):
                    util.log_error("Could not record the backup of {}: {}".format(disk.rsc_name, replies[0]))


def _finish(disks: List[_Disk], snap_name: str) -> None:
    """
    Deletes the temporary resources, finishes the CBT sessions and deletes the snapshots of this backup, errors are
    logged.
    """
    for cluster, group in _by_cluster(disks).items():
        try:
            with connect(*cluster) as lin:
                _remove_backup_resources(lin, [x for x in group if not x.cbt])
                for disk in group:
                    _remove_snapshot(lin, disk.rsc_name, snap_name, cbt_session=disk.cbt)
        except Exception as err:  # keep the error of the backup
            util.log_error("Could not remove backup snapshot {}: {}".format(snap_name, err))


def prebackup(action: str) -> None:
    """
    TM prebackup/prebackup_live: interactive backups are exported here through OneBEX (the action ends after the
    backup application finished), the others are done by the shared TM driver.

    :param action: prebackup or prebackup_live
    """
    vm_xml = sys.stdin.read()
    target_vm = Vm(vm_xml)
    if not target_vm.backup_interactive:
        forward_to_shared(action, vm_xml)
        return

    args = BackupArgs(sys.argv)
    if not args.disk_ids:
        raise RuntimeError("No disks to back up for VM {}".format(args.vm_id))
    disks = _linstor_disks(target_vm, args)
    snap_name = "{}-{}".format(consts.BACKUP_PREFIX, int(time.time()))
    freeze_mode = target_vm.backup_fs_freeze if action.endswith("_live") else "NONE"

    _remove_stale(disks)
    work_dir = tempfile.mkdtemp(prefix="linstor-backup-")
    try:
        with _frozen(args.host, args.deploy_id, freeze_mode):
            _create_snapshots(disks, snap_name)
        exports = _start_exports(disks, snap_name, args, target_vm, work_dir)
        _prepare_backup_dir(args, vm_xml, exports, work_dir)
        _run_onebex(args)
        if target_vm.backup_incremental_mode:
            _save_backup_state(disks, args.vm_id, target_vm.backup_last_increment_id + 1)
    finally:
        _finish(disks, snap_name)
        shutil.rmtree(work_dir, ignore_errors=True)


def postbackup(action: str) -> None:
    """
    TM postbackup/postbackup_live: removes the backup directory of interactive backups (the interactive datastore's
    backup action read it), the shared TM driver cleans up the others.

    :param action: postbackup or postbackup_live
    """
    vm_xml = sys.stdin.read()
    if not Vm(vm_xml).backup_interactive:
        forward_to_shared(action, vm_xml)
        return

    args = BackupArgs(sys.argv)
    rc, _, err = util.ssh_run(args.host, "rm -rf {}".format(shlex.quote(args.base_dir or args.backup_dir)))
    if rc != 0:
        # the next backup or the VM's termination removes it
        util.log_error("Could not remove the backup directory of VM {}: {}".format(args.vm_id, err.strip()))
