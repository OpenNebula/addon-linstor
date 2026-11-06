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
"""
import base64
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HAS_LINSTOR = importlib.util.find_spec("linstor") is not None

if HAS_LINSTOR:
    import linstor.sharedconsts as apiconsts
    from linstor import ApiCallResponse, LinstorError

    from one import backup

MIB = 1024 * 1024
GIB = 1024 * MIB

VM_XML = """
<VM>
  <ID>7</ID>
  <TEMPLATE>
    <DISK>
      <DATASTORE_ID><![CDATA[100]]></DATASTORE_ID>
      <DISK_ID><![CDATA[0]]></DISK_ID>
      <FORMAT><![CDATA[qcow2]]></FORMAT>
      <PERSISTENT><![CDATA[YES]]></PERSISTENT>
      <SIZE><![CDATA[{disk_size}]]></SIZE>
      <SOURCE><![CDATA[OpenNebula-Image-10]]></SOURCE>
      <TM_MAD><![CDATA[linstor]]></TM_MAD>
      <TYPE><![CDATA[BLOCK]]></TYPE>
    </DISK>
    <DISK>
      <DISK_ID><![CDATA[1]]></DISK_ID>
      <TYPE><![CDATA[fs]]></TYPE>
    </DISK>
  </TEMPLATE>
  <BACKUPS>
    <BACKUP_CONFIG>
      <FS_FREEZE><![CDATA[AGENT]]></FS_FREEZE>
      <INTERACTIVE><![CDATA[YES]]></INTERACTIVE>
      <LAST_INCREMENT_ID><![CDATA[{last_increment}]]></LAST_INCREMENT_ID>
      <MODE><![CDATA[INCREMENT]]></MODE>
    </BACKUP_CONFIG>
  </BACKUPS>
</VM>
"""

ARGV = ["prebackup_live", "node1:/var/lib/one/datastores/0/7", "0:1", "one-7", "-1", "7", "0"]


def _ok():
    return ApiCallResponse({"ret_code": apiconsts.MASK_SUCCESS, "message": "ok"})


def _error(ret_code):
    return ApiCallResponse({"ret_code": ret_code, "message": "failed"})


class FakeLinstor(object):
    """
    Records the LINSTOR calls of a backup, a python-linstor without CBT. Responses are SimpleNamespace stand-ins.
    The resource definitions are the keys of props and backup_rscs (temporary backup resources).
    """

    def __init__(self, props=None, pages=None, stale_snapshots=(), backup_rscs=(), old_api=False, cbt_reply=None,
                 ignore_filters=False):
        self.calls = []
        self.props = props or {}
        self.pages = pages or {}
        self.stale_snapshots = stale_snapshots
        self.backup_rscs = set(backup_rscs)
        self.old_api = old_api
        self.cbt_reply = cbt_reply
        self.ignore_filters = ignore_filters

    @staticmethod
    def all_api_responses_no_error(replies):
        return all(not x.is_error() for x in replies)

    def api_version_smaller(self, version):
        return self.old_api

    def snapshot_dfn_list_raise(self, filter_by_resources=None):
        snaps = [SimpleNamespace(rsc_name=r, snapshot_name=s) for r, s in self.stale_snapshots
                 if self.ignore_filters or r in filter_by_resources]
        return SimpleNamespace(snapshots=snaps)

    def snapshot_create_multi(self, node_names, rsc_names, snapshot_name, **kwargs):
        cbt = kwargs.get("cbt", False)
        self.calls.append(("snapshot_create_multi", tuple(rsc_names), snapshot_name, cbt))
        return self.cbt_reply if cbt and self.cbt_reply else [_ok()]

    def resource_dfn_list_raise(self, query_volume_definitions=True, filter_by_resource_definitions=None):
        assert filter_by_resource_definitions, "an empty filter lists all resource definitions"
        names = sorted(set(self.props) | self.backup_rscs)
        if not self.ignore_filters:
            names = [x for x in names if x in filter_by_resource_definitions]
        return SimpleNamespace(resource_definitions=[
            SimpleNamespace(name=x, properties=self.props.get(x, {})) for x in names])

    def resource_dfn_delete(self, name):
        self.calls.append(("rd_delete", name))
        self.backup_rscs.discard(name)
        return [_ok()]

    def resource_dfn_modify(self, name, property_dict):
        self.calls.append(("modify", name, property_dict))
        return [_ok()]

    def snapshot_delete(self, rsc_name, snapshot_name):
        self.calls.append(("snapshot_delete", rsc_name, snapshot_name))
        return [_ok()]


class FakeCbtLinstor(FakeLinstor):
    """A python-linstor with CBT."""

    def snapshot_cbt_session_start(self, rsc_name, snapshot_name, node_name):
        self.calls.append(("session_start", rsc_name, node_name))
        volume = SimpleNamespace(volume_number=0, device_path="/dev/drbd1{}".format(len(self.calls)),
                                 volume_size=GIB + 1)
        return [SimpleNamespace(cbt_id="ID-" + rsc_name, volumes=[volume])]

    def snapshot_cbt_extents(self, rsc_name, snapshot_name, volume_number=0, start_offset=0, max_extents=None,
                             mode=None):
        if mode is None:
            self.calls.append(("extents", rsc_name, start_offset))
            return self.pages[(rsc_name, start_offset)]
        self.calls.append(("extents", rsc_name, start_offset, mode))
        return self.pages[(rsc_name, start_offset, mode)]

    def snapshot_cbt_session_finish(self, rsc_name, snapshot_name):
        self.calls.append(("session_finish", rsc_name, snapshot_name))
        return [_ok()]


class FakeZeroCbtLinstor(FakeCbtLinstor):
    """A python-linstor with the never written (zero) extents of CBT snapshots."""
    CBT_EXTENTS_MODE_ZERO = "zero"


class FakeResource(object):
    """python-linstor's Resource, as far as the backup without CBT uses it."""

    def __init__(self, lin, name):
        self._lin = lin
        self.name = name

    def restore_from_snapshot(self, snapshot_name, resource_name_to):
        self._lin.calls.append(("restore", self.name, snapshot_name, resource_name_to))
        self._lin.backup_rscs.add(resource_name_to)
        return FakeResource(self._lin, resource_name_to)

    def activate(self, node_name):
        self._lin.calls.append(("activate", self.name, node_name))


class _Connect(object):
    def __init__(self, lin):
        self._lin = lin

    def __call__(self, uri_list, auth_token=None, timeout=300):
        return self

    def __enter__(self):
        return self._lin

    def __exit__(self, *args):
        return False


def _page(base_cbt_id, extents, next_offset=None):
    """extents: (start, length, dirty, zero), dirty None in zero mode"""
    return [SimpleNamespace(base_cbt_id=base_cbt_id, next_offset=next_offset,
                            extents=[SimpleNamespace(start=s, length=n, dirty=d, zero=z) for s, n, d, z in extents])]


def _state(vm_id, increment, cbt_id):
    return {backup.BACKUP_STATE_PROP: json.dumps({"vm": vm_id, "increment": increment, "cbt_id": cbt_id})}


@unittest.skipUnless(HAS_LINSTOR, "python-linstor not installed")
class TestBackup(unittest.TestCase):
    def setUp(self):
        conf = tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False)
        conf.close()
        self.addCleanup(os.unlink, conf.name)
        patcher = patch.object(backup, "DATASTORE_CONF", conf.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.conf = conf.name

        client = tempfile.NamedTemporaryFile("w", suffix=".rb", delete=False)
        client.write("module TransferManager\n    class OneBEX\n        REMOTE_LIB_DIR = '/var/tmp/one/tm/lib'\n")
        client.close()
        self.addCleanup(os.unlink, client.name)
        patcher = patch.object(backup, "ONEBEX_CLIENT", client.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = client.name

    def test_incremental_base(self):
        value = json.dumps({"vm": 7, "increment": 3, "cbt_id": "ABC"})
        self.assertEqual(backup.incremental_base(value, 7, 3), "ABC")
        self.assertIsNone(backup.incremental_base(value, 8, 3))  # another VM used the disk
        self.assertIsNone(backup.incremental_base(value, 7, 4))  # OpenNebula didn't record that backup
        self.assertIsNone(backup.incremental_base(None, 7, 3))
        self.assertIsNone(backup.incremental_base("garbage", 7, 3))
        self.assertIsNone(backup.incremental_base("[1]", 7, 3))

    def test_remote_tm_lib_dir(self):
        self.assertEqual(backup.remote_tm_lib_dir(), "/var/tmp/one/tm/lib")
        with open(self.client, "w") as client:
            client.write("REMOTE_LIB_DIR = '/var/lib/one-remotes/tm/lib'\n")
        self.assertEqual(backup.remote_tm_lib_dir(), "/var/lib/one-remotes/tm/lib")
        with patch.object(backup, "ONEBEX_CLIENT", "/nonexistent/onebex.rb"):
            self.assertEqual(backup.remote_tm_lib_dir(), backup.DEFAULT_REMOTE_TM_LIB_DIR)

    def test_backup_base_path(self):
        with open(self.conf, "w") as conf:
            conf.write('#BACKUP_BASE_PATH="/commented"\nexport BACKUP_BASE_PATH="/srv/backups"\n')
        args = backup.BackupArgs(ARGV)
        self.assertEqual(args.host, "node1")
        self.assertEqual(args.disk_ids, ["0", "1"])
        self.assertEqual(args.vm_id, 7)
        self.assertEqual(args.system_ds_id, "0")
        self.assertEqual(args.base_dir, "/srv/backups/7")
        self.assertEqual(args.backup_dir, "/srv/backups/7/backup")

    def test_backup_dir_in_vm_dir(self):
        with patch.dict(os.environ, {}, clear=True):
            args = backup.BackupArgs(ARGV)
        self.assertIsNone(args.base_dir)
        self.assertEqual(args.backup_dir, "/var/lib/one/datastores/0/7/backup")

    def test_write_extents_pages(self):
        lin = FakeCbtLinstor(pages={
            ("r", 0): _page("BASE", [(0, 4096, True, False), (4096, 61440, False, False)], next_offset=65536),
            ("r", 65536): _page("BASE", [(65536, 1048576, True, False), (1114112, 4096, False, True)]),
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "extents")
            self.assertTrue(backup._write_extents(lin, "r", "s", 0, "BASE", path))
            with open(path) as extents:
                self.assertEqual(extents.read(), "0 4096 1 0\n4096 61440 0 0\n65536 1048576 1 0\n1114112 4096 0 1\n")

    def test_write_extents_full(self):
        # all extents are dirty, the never written ones zero
        lin = FakeZeroCbtLinstor(pages={
            ("r", 0, "zero"): _page(None, [(0, 4096, None, False), (4096, 61440, None, True)]),
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "extents")
            self.assertTrue(backup._write_extents(lin, "r", "s", 0, None, path))
            with open(path) as extents:
                self.assertEqual(extents.read(), "0 4096 1 0\n4096 61440 1 1\n")

    def test_write_extents_full_without_zero_extents(self):
        lin = FakeCbtLinstor()
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(backup._write_extents(lin, "r", "s", 0, None, os.path.join(tmp, "extents")))
        self.assertEqual(lin.calls, [])

    def test_write_extents_other_base(self):
        lin = FakeCbtLinstor(pages={("r", 0): _page("OTHER", [(0, 4096, True, False)])})
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(backup._write_extents(lin, "r", "s", 0, "BASE", os.path.join(tmp, "extents")))

    @unittest.skipUnless(HAS_LINSTOR and hasattr(apiconsts, "FAIL_CBT_FULL_BACKUP_REQUIRED"),
                         "python-linstor without CBT")
    def test_write_extents_full_backup_required(self):
        lin = FakeCbtLinstor(pages={("r", 0): [_error(apiconsts.FAIL_CBT_FULL_BACKUP_REQUIRED)]})
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(backup._write_extents(lin, "r", "s", 0, "BASE", os.path.join(tmp, "extents")))

    def _prebackup(self, lin, last_increment, onebex_rc=0, disk_size=1025):
        """Runs an interactive prebackup_live against lin, returns the ssh commands and the uploaded files."""
        ssh = []
        uploads = {}

        def ssh_run(host, cmd, stdin=None):
            ssh.append((host, cmd))
            if cmd.startswith("cat > "):
                uploads[cmd[len("cat > "):].strip("'")] = stdin if isinstance(stdin, bytes) else stdin.read()
            if cmd.startswith("ruby "):
                return onebex_rc, "", "Backup failed\n\tfrom onebex.rb:156:in 'start'\n" if onebex_rc else ""
            return 0, "", ""

        datastore = SimpleNamespace(linstor_controllers="linstor://ctrl", linstor_controller_auth_token=None)
        with patch.object(sys, "argv", ARGV), \
                patch.object(sys, "stdin", io.StringIO(VM_XML.format(last_increment=last_increment, disk_size=disk_size))), \
                patch.object(backup, "connect", _Connect(lin)), \
                patch.object(backup, "make_resource", lambda name, *cluster: FakeResource(lin, name)), \
                patch.object(backup, "wait_resource_ready", lambda res: lin.calls.append(("ready", res.name))), \
                patch.object(backup, "Datastore", lambda xml: datastore), \
                patch.object(backup.util, "show_ds", lambda ds_id: ds_id), \
                patch.object(backup.util, "ssh_run", ssh_run), \
                patch.object(backup.time, "time", lambda: 1700000000):
            backup.prebackup("prebackup_live")
        return ssh, uploads

    def test_prebackup_incremental(self):
        snap = "OpenNebula-Backup-1700000000"
        lin = FakeCbtLinstor(
            props={
                "OpenNebula-Image-10": _state(7, 3, "PREV-10"),
                "OpenNebula-Volatile-vm7-disk1": _state(7, 2, "PREV-1"),  # not the last increment
            },
            pages={("OpenNebula-Image-10", 0): _page("PREV-10", [(0, 4096, True, False)])},
            stale_snapshots=[("OpenNebula-Image-10", "OpenNebula-Backup-1600000000"),
                             ("OpenNebula-Image-10", "user-snapshot")])
        ssh, uploads = self._prebackup(lin, last_increment=3)

        self.assertEqual(lin.calls, [
            ("session_finish", "OpenNebula-Image-10", "OpenNebula-Backup-1600000000"),
            ("snapshot_delete", "OpenNebula-Image-10", "OpenNebula-Backup-1600000000"),
            ("snapshot_create_multi", ("OpenNebula-Image-10", "OpenNebula-Volatile-vm7-disk1"), snap, True),
            ("session_start", "OpenNebula-Image-10", "node1"),
            ("extents", "OpenNebula-Image-10", 0),
            ("session_start", "OpenNebula-Volatile-vm7-disk1", "node1"),
            ("modify", "OpenNebula-Image-10",
             {backup.BACKUP_STATE_PROP: '{"cbt_id": "ID-OpenNebula-Image-10", "increment": 4, "vm": 7}'}),
            ("modify", "OpenNebula-Volatile-vm7-disk1",
             {backup.BACKUP_STATE_PROP: '{"cbt_id": "ID-OpenNebula-Volatile-vm7-disk1", "increment": 4, "vm": 7}'}),
            ("session_finish", "OpenNebula-Image-10", snap),
            ("snapshot_delete", "OpenNebula-Image-10", snap),
            ("session_finish", "OpenNebula-Volatile-vm7-disk1", snap),
            ("snapshot_delete", "OpenNebula-Volatile-vm7-disk1", snap),
        ])

        bck = "/var/lib/one/datastores/0/7/backup"
        cmds = [cmd for _, cmd in ssh]
        self.assertEqual(cmds[0], "virsh -c qemu:///system domfsfreeze one-7")
        self.assertEqual(cmds[1], "virsh -c qemu:///system domfsthaw one-7")
        self.assertEqual(cmds[2], "rm -rf {d} && mkdir -p {d}".format(d=bck))
        self.assertTrue(cmds[-1].startswith("ruby -I /var/tmp/one/tm/lib -r onebex -e "))
        self.assertTrue(cmds[-1].endswith(" 7 0 " + bck))
        self.assertTrue(all(host == "node1" for host, _ in ssh))

        self.assertEqual(base64.decodebytes(uploads[bck + "/vm.xml"]).decode(), VM_XML.format(last_increment=3, disk_size=1025))
        self.assertEqual(uploads[bck + "/disk.0.extents"], b"0 4096 1 0\n")
        exports = json.loads(uploads[bck + "/interactive_exports.json"].decode())
        self.assertEqual(exports["0"]["exporter"], "linstor")
        self.assertEqual(exports["0"]["mode"], "incremental")
        self.assertEqual(exports["0"]["extents"], bck + "/disk.0.extents")
        self.assertEqual(exports["0"]["size_bytes"], GIB + 1)
        self.assertEqual(exports["0"]["format"], "qcow2")
        self.assertEqual(exports["1"]["format"], "raw")
        self.assertEqual(exports["1"]["mode"], "full")
        self.assertNotIn("extents", exports["1"])

    @unittest.skipUnless(HAS_LINSTOR and hasattr(apiconsts, "FAIL_CBT_FULL_BACKUP_REQUIRED"),
                         "python-linstor without CBT")
    def test_prebackup_full_zero_extents(self):
        # full backups skip the never written extents, if LINSTOR knows them
        lin = FakeZeroCbtLinstor(pages={
            ("OpenNebula-Image-10", 0, "zero"): _page(None, [(0, 4096, None, False), (4096, GIB - 4095, None, True)]),
            ("OpenNebula-Volatile-vm7-disk1", 0, "zero"): [_error(apiconsts.FAIL_CBT_FULL_BACKUP_REQUIRED)],
        })
        ssh, uploads = self._prebackup(lin, last_increment=-1)

        self.assertEqual([call for call in lin.calls if call[0] == "extents"], [
            ("extents", "OpenNebula-Image-10", 0, "zero"),
            ("extents", "OpenNebula-Volatile-vm7-disk1", 0, "zero"),
        ])
        bck = "/var/lib/one/datastores/0/7/backup"
        self.assertEqual(uploads[bck + "/disk.0.extents"], b"0 4096 1 0\n4096 1073737729 1 1\n")
        self.assertNotIn(bck + "/disk.1.extents", uploads)
        exports = json.loads(uploads[bck + "/interactive_exports.json"].decode())
        self.assertEqual(exports["0"]["mode"], "full")
        self.assertEqual(exports["0"]["extents"], bck + "/disk.0.extents")
        self.assertEqual(exports["1"]["mode"], "full")
        self.assertNotIn("extents", exports["1"])

    def test_prebackup_failed_backup_keeps_state(self):
        snap = "OpenNebula-Backup-1700000000"
        lin = FakeCbtLinstor()
        with self.assertRaisesRegex(RuntimeError, "^Interactive backup of VM 7 failed: Backup failed$"):
            self._prebackup(lin, last_increment=-1, onebex_rc=1)

        self.assertNotIn("modify", [call[0] for call in lin.calls])
        self.assertEqual(lin.calls[-4:], [
            ("session_finish", "OpenNebula-Image-10", snap),
            ("snapshot_delete", "OpenNebula-Image-10", snap),
            ("session_finish", "OpenNebula-Volatile-vm7-disk1", snap),
            ("snapshot_delete", "OpenNebula-Volatile-vm7-disk1", snap),
        ])

    def test_prebackup_device_larger_than_disk(self):
        # LINSTOR devices are up to one allocation granule larger than the disk, the export has the device's size
        ssh, uploads = self._prebackup(FakeCbtLinstor(), last_increment=-1, disk_size=1024)

        exports = json.loads(uploads["/var/lib/one/datastores/0/7/backup/interactive_exports.json"].decode())
        self.assertEqual(exports["0"]["size_bytes"], GIB + 1)
        self.assertNotIn("size", exports["0"])

    def _assert_backup_without_cbt(self, lin, cbt_tried):
        """Checks a backup of VM_XML (increment 4 of a chain) that fell back to exporting whole disks."""
        snap = "OpenNebula-Backup-1700000000"
        rscs = ("OpenNebula-Image-10", "OpenNebula-Volatile-vm7-disk1")
        tmp0, tmp1 = "OpenNebula-Backup-vm7-disk0", "OpenNebula-Backup-vm7-disk1"
        ssh, uploads = self._prebackup(lin, last_increment=3)

        creates = [("snapshot_create_multi", rscs, snap, True)] if cbt_tried else []
        self.assertEqual(lin.calls, [
            ("rd_delete", tmp0),  # left by an earlier backup
        ] + creates + [
            ("snapshot_create_multi", rscs, snap, False),
            ("restore", "OpenNebula-Image-10", snap, tmp0),
            ("activate", tmp0, "node1"),
            ("ready", tmp0),
            ("restore", "OpenNebula-Volatile-vm7-disk1", snap, tmp1),
            ("activate", tmp1, "node1"),
            ("ready", tmp1),
            # no CBT state, temporary resources before the snapshots, no CBT sessions
            ("rd_delete", tmp0),
            ("rd_delete", tmp1),
            ("snapshot_delete", "OpenNebula-Image-10", snap),
            ("snapshot_delete", "OpenNebula-Volatile-vm7-disk1", snap),
        ])
        self.assertEqual(lin.backup_rscs, set())

        bck = "/var/lib/one/datastores/0/7/backup"
        self.assertTrue(ssh[-1][1].startswith("ruby -I /var/tmp/one/tm/lib -r onebex -e "))
        exports = json.loads(uploads[bck + "/interactive_exports.json"].decode())
        self.assertEqual(sorted(exports), ["0", "1"])
        self.assertEqual(exports["0"], {
            "exporter": "linstor", "source": "/dev/drbd/by-res/{}/0".format(tmp0), "format": "qcow2",
            "mode": "full", "resource": "OpenNebula-Image-10",
            "snapshot": snap})
        self.assertEqual(exports["1"]["source"], "/dev/drbd/by-res/{}/0".format(tmp1))
        self.assertEqual(exports["1"]["mode"], "full")
        self.assertNotIn(bck + "/disk.0.extents", uploads)

    def test_prebackup_python_linstor_without_cbt(self):
        lin = FakeLinstor(props={"OpenNebula-Image-10": _state(7, 3, "PREV-10")},
                          backup_rscs=["OpenNebula-Backup-vm7-disk0"])
        self._assert_backup_without_cbt(lin, cbt_tried=False)

    def test_prebackup_controller_without_cbt(self):
        lin = FakeCbtLinstor(props={"OpenNebula-Image-10": _state(7, 3, "PREV-10")},
                             backup_rscs=["OpenNebula-Backup-vm7-disk0"], old_api=True)
        self._assert_backup_without_cbt(lin, cbt_tried=False)

    @unittest.skipUnless(HAS_LINSTOR and hasattr(apiconsts, "FAIL_CBT_NOT_SUPPORTED"), "python-linstor without CBT")
    def test_prebackup_drbd_without_cbt(self):
        lin = FakeCbtLinstor(props={"OpenNebula-Image-10": _state(7, 3, "PREV-10")},
                             backup_rscs=["OpenNebula-Backup-vm7-disk0"],
                             cbt_reply=[_error(apiconsts.FAIL_CBT_NOT_SUPPORTED)])
        self._assert_backup_without_cbt(lin, cbt_tried=True)

    def test_prebackup_cbt_snapshot_error(self):
        lin = FakeCbtLinstor(cbt_reply=[_error(apiconsts.MASK_ERROR | 1)])
        with self.assertRaisesRegex(LinstorError, "Could not create CBT snapshot"):
            self._prebackup(lin, last_increment=3)
        self.assertNotIn("restore", [call[0] for call in lin.calls])

    def test_remove_backup_resources_only_deletes_them(self):
        disk = backup._Disk("0", "OpenNebula-Image-10", None, 7)
        # an empty list must not list (and delete) all resource definitions
        lin = FakeLinstor(props={"OpenNebula-Image-10": {}}, backup_rscs=["OpenNebula-Backup-vm7-disk0"])
        backup._remove_backup_resources(lin, [])
        self.assertEqual(lin.calls, [])
        # a controller that ignores the filter
        lin = FakeLinstor(props={"OpenNebula-Image-10": {}, "other": {}},
                          backup_rscs=["OpenNebula-Backup-vm7-disk0", "OpenNebula-Backup-vm8-disk0"],
                          ignore_filters=True)
        backup._remove_backup_resources(lin, [disk])
        self.assertEqual(lin.calls, [("rd_delete", "OpenNebula-Backup-vm7-disk0")])

    def test_remove_stale_ignores_other_resources(self):
        lin = FakeCbtLinstor(stale_snapshots=[("OpenNebula-Image-10", "OpenNebula-Backup-1"),
                                              ("OpenNebula-Image-99", "OpenNebula-Backup-2")],
                             ignore_filters=True)
        disk = backup._Disk("0", "OpenNebula-Image-10", None, 7)
        with patch.object(backup, "connect", _Connect(lin)), \
                patch.object(backup._Disk, "cluster", ("linstor://ctrl", None)):
            backup._remove_stale([disk])
        self.assertEqual(lin.calls, [
            ("session_finish", "OpenNebula-Image-10", "OpenNebula-Backup-1"),
            ("snapshot_delete", "OpenNebula-Image-10", "OpenNebula-Backup-1"),
        ])

    def test_prebackup_not_interactive(self):
        vm_xml = VM_XML.format(last_increment=3, disk_size=1025).replace("<![CDATA[YES]]></INTERACTIVE>",
                                                         "<![CDATA[NO]]></INTERACTIVE>")
        with patch.object(sys, "stdin", io.StringIO(vm_xml)), \
                patch.object(backup, "forward_to_shared") as forward:
            backup.prebackup("prebackup")
        forward.assert_called_once_with("prebackup", vm_xml)


if __name__ == "__main__":
    unittest.main()
