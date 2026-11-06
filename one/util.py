"""
OpenNebula Driver for Linstor
Copyright 2018 LINBIT USA LLC

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

import sys
import os
import subprocess
import syslog
import traceback
import json
import re
import io
import shlex
import base64
import signal
import xml.etree.ElementTree as ET
from types import FrameType
from typing import IO, Any, Dict, Optional, Tuple, Union

REMOTES_DIR = "/var/lib/one/remotes/"

ONE_LOCATION = os.getenv("ONE_LOCATION")
if ONE_LOCATION:
    REMOTES_DIR = os.path.join(ONE_LOCATION, "var/remotes")

SCRIPTS_COMMON = REMOTES_DIR + "/scripts_common.sh"
UTILS_DIR = REMOTES_DIR + "/datastore/"
LIBFS = UTILS_DIR + "libfs.sh"
DOWNLOADER = UTILS_DIR + "downloader.sh"
TM_COMMON = REMOTES_DIR + "/tm/tm_common.sh"


def _source(file, command, string_args=None, forward_agent=False):
    sourced_cmd = "source {}".format(file)
    command_call = "{}".format(command)
    if string_args:
        command_call = command_call + " {}".format(string_args)

    if forward_agent:
        sourced_cmd = sourced_cmd + \
            ' && if declare -F ssh_forward >/dev/null; then ssh_forward {command}; ' \
            'else SSH="${{SSH_FWD:-${{SSH}} -o ForwardAgent=yes -o ControlMaster=no -o ControlPath=none}}" ' \
            '{command}; fi'.format(command=command_call)
    else:
        sourced_cmd = sourced_cmd + " && {}".format(command_call)

    exec_string = ["bash", "-c", sourced_cmd]

    return exec_string


def log_error(msg):
    syslog.syslog(syslog.LOG_ERR, "ERROR {}".format(msg))


def log_info(msg):
    syslog.syslog(syslog.LOG_INFO, "INFO {}".format(msg))


def _wait_for_subp(cmd, log=True):
    """
    Executes the given command and waits until finished.

    :param list[str] cmd: command to execute
    :param bool log: command should be logged to opennebula
    :return: process return code
    :rtype: int
    """
    if log:
        log_info("running shell command: {}".format(" ".join(cmd)))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, err = proc.communicate()

    if proc.returncode != 0:
        log_error("command {} failed: {}".format(cmd, err))

    return proc.returncode


def _get_subp_out_base(cmd, log=True):
    """
    Runs cmd and logs into syslog and returns output
    :param list[str] cmd: shell command to run
    :param bool log: if cmdn should be logged as INFO
    :return: Tuple of [returncode, stdout, stderr]
    :rtype: (int, str, str)
    """
    if log:
        log_info("running shell command: {}".format(" ".join(cmd)))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    return proc.returncode, out.decode(), err.decode()


def _get_subp_out(cmd):
    rc, out, err = _get_subp_out_base(cmd)

    if rc != 0:
        log_error("command {} failed: {}".format(cmd, err))
        raise subprocess.CalledProcessError(returncode=rc, cmd=cmd, output=out, stderr=err)

    return out


def exec_local_with_out(cmd):
    """
    :param str cmd:
    :return:
    """
    return _get_subp_out(_source(SCRIPTS_COMMON, cmd))


def ssh_direct(host, cmd):
    """
    Executes the given cmd on the host and returns the output of the command.

    :param str host: host to execute the command
    :param str cmd: Command to execute
    :return: stdout of the executed command
    :rtype: str
    """
    return _get_subp_out(_source(SCRIPTS_COMMON, "$SSH", '"{h}" "{c}"'.format(h=host, c=cmd)))


def ssh_direct_ignore_errors(host, cmd):
    """
    Executes the given cmd on the host and returns the std output of the command, ignoring any command errors.

    :param str host: host to execute the command
    :param str cmd: Command to execute
    :return: stdout of the executed command
    :rtype: str
    """
    rc, out, err = _get_subp_out_base(_source(SCRIPTS_COMMON, "$SSH", '"{h}" "{c}"'.format(h=host, c=cmd)))

    return out


def ssh_exec_and_log(host, cmd, error_msg, forward_agent=False):
    """

    :param str host: hostname to ssh to
    :param str cmd: cmd to execute
    :param str error_msg: error message if cmd fails
    :param bool forward_agent: enable SSH agent forwarding
    :return:
    """
    log_info("ssh '{h}' cmd: {c}".format(h=host, c=cmd))
    ssh_cmd = [
        '"{}"'.format(host),
        '"{}"'.format(cmd),
        '"{}"'.format(error_msg)
    ]
    return _wait_for_subp(
        _source(SCRIPTS_COMMON, "ssh_exec_and_log", " ".join(ssh_cmd), forward_agent=forward_agent),
        log=False)


def ssh_exec_and_log_with_err(host, cmd, error_msg, forward_agent=False):
    """
    Runs cmd and logs into syslog and returns return code and stderr
    :param str host: Where ssh should connect to
    :param str cmd: command to run on host
    :param str error_msg: log message if error occurs
    :param bool forward_agent: enable SSH agent forwarding
    :return: Tuple of [returncode, stderr]
    :rtype: (int, str)
    """
    log_info("ssh '{h}' cmd: {c}".format(h=host, c=cmd))
    ssh_cmd = [
        '"{}"'.format(host),
        '"{}"'.format(cmd),
        '"{}"'.format(error_msg)
    ]
    # ssh_exec_and_log doesn't return stdout
    rc, _, err = _get_subp_out_base(
        _source(SCRIPTS_COMMON, "ssh_exec_and_log", " ".join(ssh_cmd), forward_agent=forward_agent),
        log=False)
    return rc, err


def ssh_monitor_and_log(host, cmd, error_msg, forward_agent=False):
    """
    Runs cmd and logs into syslog and returns return code, output and stderr
    :param str host: Where ssh should connect to
    :param str cmd: command to run on host
    :param str error_msg: log message if error occurs
    :param bool forward_agent: enable SSH agent forwarding
    :return: Tuple of [returncode, stdout, stderr]
    :rtype: (int, str, str)
    """
    log_info("ssh '{h}' cmd: {c}".format(h=host, c=cmd))
    ssh_cmd = [
        '"{}"'.format(host),
        '"{}"'.format(cmd),
        '"{}"'.format(error_msg)
    ]
    return _get_subp_out_base(
        _source(SCRIPTS_COMMON, "ssh_monitor_and_log", " ".join(ssh_cmd), forward_agent=forward_agent),
        log=False)


def ssh_run(host: str, cmd: str, stdin: Optional[Union[bytes, IO[bytes]]] = None) -> Tuple[int, str, str]:
    """
    Runs cmd on host with OpenNebula's $SSH and returns return code, stdout and stderr.

    Unlike the other ssh helpers, host and cmd are passed to bash as arguments instead of being inserted
    into the bash command string, so cmd only has to be quoted for the remote shell (shlex.quote).

    :param host: host to execute the command
    :param cmd: command line for the remote shell
    :param stdin: data or open binary file passed to the remote command's stdin
    :return: Tuple of [returncode, stdout, stderr]
    """
    log_info("ssh '{h}' cmd: {c}".format(h=host, c=cmd))
    exec_string = ["bash", "-c", 'source {} && $SSH "$1" "$2"'.format(SCRIPTS_COMMON), "ssh_run", host, cmd]
    if stdin is None:
        proc = subprocess.run(exec_string, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif isinstance(stdin, bytes):
        proc = subprocess.run(exec_string, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.run(exec_string, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    if proc.returncode != 0:
        log_error("ssh '{h}' cmd {c} failed ({rc}): {e}".format(h=host, c=cmd, rc=proc.returncode, e=err))
    return proc.returncode, out, err


def exec_and_log(cmd, message):
    rc = _wait_for_subp(["bash", "-c", cmd])

    if int(rc) != 0:
        log_error(message)

    return rc


def link_file(dst_host, dst_dir, dst_path, device_path, resource_name):
    """
    Calls the ln command on the dst_host

    :param str dst_host:
    :param str dst_dir:
    :param str dst_path:
    :param str device_path:
    :param str resource_name: Resource name for error output
    :return: True if run, else throws exception
    """
    link_command = 'mkdir -p {dstdir} && ln -fs {devp} {dstp}'.format(
        dstdir=dst_dir, devp=device_path, dstp=dst_path)

    rc = ssh_exec_and_log(
        host=dst_host,
        cmd=link_command,
        error_msg='Error: Unable to link {} to {} on {}'.format(resource_name, dst_path, dst_host))
    if rc != 0:
        raise RuntimeError("Error: Unable to link {} to {} on {}".format(resource_name, dst_path, dst_host))

    return True


def unlink_file(host, path):
    """
    Deletes a file or path.

    :param str host: host computer
    :param str path: path on the host to delete
    :return: True, or raises RuntimeError()
    """
    unlink_command = 'set -e;if [ -d "{dst}" ]; then rm -rf "{dst}"; else rm -f "{dst}"; fi'.format(dst=path)

    rc = ssh_exec_and_log(
        host=host,
        cmd=unlink_command,
        error_msg="Error: Unable to remove symbolic link {} on {}".format(path, host))
    if rc != 0:
        raise RuntimeError("Error: Unable to remove symbolic link {} on {}".format(path, host))
    return True

def is_shared_fs(host, path):
    """
    Check if path on host is a shared filesystem(nfs)

    :param str host: host computer
    :param str path: path on the host to delete
    :return: True, or raises RuntimeError()
    """
    fstype = ssh_direct(host, 'stat --file-system --format=%T "{dst}"'.format(dst=path)).strip()
    return fstype and fstype in ['nfs', 'fuseblk']


def rm_shared_safe(host, path):
    """
    Deletes a file or path if it isn't on a network filesystem.

    :param str host: host computer
    :param str path: path on the host to delete
    :return: True, or raises RuntimeError()
    """
    if not is_shared_fs(host, path):
        unlink_file(host, path)
    else:
        log_info("filesystem is shared, not deleting: {p}".format(p=path))

    return True


def mkfs_command(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "mkfs_command", string_args))


def mkiso_command(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "$MKISOFS", string_args))


def ssh_make_path(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "ssh_make_path", string_args))


def set_up_datastore(string_args):
    return _wait_for_subp(_source(LIBFS, "set_up_datastore", string_args))


def check_restricted(path, base_path, restricted_dirs, safe_dirs):
    """
    Checks if path is in a restricted dir of the datastore, using OpenNebula's libfs.sh.

    set_up_datastore and check_restricted have to run in the same shell, as
    check_restricted reads the dirs set up by set_up_datastore.

    :param str path: image path to check
    :param Optional[str] base_path: datastore BASE_PATH
    :param Optional[str] restricted_dirs: datastore RESTRICTED_DIRS
    :param Optional[str] safe_dirs: datastore SAFE_DIRS
    :return: True if path is restricted
    :rtype: bool
    """
    cmd = "set_up_datastore {b} {r} {s} && check_restricted".format(
        b=shlex.quote(base_path or ""),
        r=shlex.quote(restricted_dirs or ""),
        s=shlex.quote(safe_dirs or ""))
    return _get_subp_out(_source(LIBFS, cmd, shlex.quote(path))).strip() == "1"


def arg_host(string_args):
    """
    Returns the host part of string_args e.g.:
        example.com:/tmp/file -> example.com
    :param str string_args: opennebula string args
    :return: the host path of string_args
    """
    split = string_args.split(":", 1)
    return split[0]


def arg_path(string_args):
    """
    Returns the path part of an opennebula path arg and also normalizes the path.
    :param str string_args: opennebula string args
    :return: the normalized path arg
    """
    split = string_args.split(":", 1)
    path = split[1] if len(split) > 1 else split[0]
    return os.path.normpath(path)


def one_path_ds_id(one_path):
    """
    Return the datastore id of the given opennebula path e.g.: /var/lib/datastores/100/32/disk.0
    :param str one_path: opennebula /var/lib/datastores... path
    :return: int id of the datastore
    :rtype: int
    """
    m = re.search(r".*/(\d+)/\d+/?.*$", one_path)
    if m:
        return int(m.group(1))
    return None


def migrate_other(string_args):
    # We're turning off logging here because this gets called with a huge
    # base64 image dump and it's too noisy.
    return _wait_for_subp(_source(TM_COMMON, "migrate_other", string_args), log=False)


def show_vm(vm_id):
    """
    Executes the onevm show command and returns the xml output.

    :param int vm_id: vm id number
    :return: XML output from onevm show command
    """
    return _get_subp_out(["onevm", "show", "-x", str(vm_id)])


def show_image(image_id):
    return _get_subp_out(["oneimage", "show", "--xml", str(image_id)])


def image_is_locked(image_id: int) -> Optional[bool]:
    """
    Returns whether OpenNebula is still creating the image (state LOCKED), e.g. datastore/cp is running for it.

    :param image_id: OpenNebula image id
    :return: True if locked, False if not or if the image doesn't exist, None if OpenNebula didn't tell
    """
    rc, out, err = _get_subp_out_base(["oneimage", "show", "--xml", str(image_id)], log=False)
    if rc != 0:
        return False if "Error getting image" in err else None
    try:
        return ET.fromstring(out).find("STATE").text == "4"
    except (ET.ParseError, AttributeError):
        return None


def show_ds(ds_id):
    return _get_subp_out(["onedatastore", "show", "--xml", str(ds_id)])


def fs_size(string_args):
    return _get_subp_out(
        _source(LIBFS, 'UTILS_PATH="{}" fs_size'.format(UTILS_DIR), string_args)
    )


def detect_image_format(host, path):
    cmd = "$QEMU_IMG info --output json {p}".format(p=path)
    rc, stdout, stderr = ssh_monitor_and_log(host, cmd, "qemu-img info failed for " + path)

    if rc != 0:
        raise RuntimeError("Error: qemu-img info failed for {}; Message {}".format(path, stdout + stderr))

    img_data = json.loads(stdout)
    return img_data["format"]


def image_info(host: str, path: str) -> Dict[str, Any]:
    """
    Returns qemu-img info of the image file at path on host.

    :param host: host to run qemu-img on
    :param path: image file
    :return: qemu-img info
    """
    rc, out, err = ssh_run(host, "qemu-img info --output json {}".format(shlex.quote(path)))
    if rc != 0:
        raise RuntimeError("qemu-img info failed for {} on {}: {}".format(path, host, err.strip()))
    return json.loads(out)


def raw_conversion_source(info: Dict[str, Any], path: str) -> Tuple[str, int]:
    """
    Checks that qemu-img can convert the image file at path to raw on its own and returns its format and virtual
    size.

    Images can refer to other files (backing files, qcow2 external data files, VMDK extents), qemu-img would read
    them with the driver's permissions on the host. These and encrypted images are rejected.

    :param info: qemu-img info of the image
    :param path: image file
    :return: image format and virtual size in bytes
    """
    backing_file = info.get("full-backing-filename") or info.get("backing-filename")
    if backing_file:
        raise RuntimeError("Image {} has the backing file {}, it can't be converted to raw".format(path, backing_file))

    if info.get("encrypted"):
        raise RuntimeError("Image {} is encrypted, it can't be converted to raw".format(path))

    data = (info.get("format-specific") or {}).get("data") or {}
    if data.get("data-file"):
        raise RuntimeError("Image {} has the external data file {}, it can't be converted to raw".format(
            path, data["data-file"]))

    for extent in data.get("extents") or []:
        if extent.get("filename") != path:
            raise RuntimeError("Image {} refers to the extent {}, it can't be converted to raw".format(
                path, extent.get("filename")))

    return info["format"], int(info["virtual-size"])


def image_range_is_zero(host: str, path: str, image_format: str, offset: int, length: int) -> bool:
    """
    Returns whether a range of the image reads as zeros.

    qemu-img compares the range with a zero image, it only reads the allocated parts of it. qemu-img map isn't exact
    enough: it reports whole clusters as data (qcow2: 64 KiB), e.g. a GPT backup header and the zeros after it.

    :param host: host with the image file
    :param path: image file
    :param image_format: format of the image file, as qemu-img info reports it
    :param offset: start of the range in bytes, a multiple of 512
    :param length: length of the range in bytes, a multiple of 512
    :return: True if the range only has zeros
    """
    args = [
        "qemu-img", "compare", "-q",
        "--image-opts", raw_source_image_opts(path, image_format, length, offset=offset),
        "--image-opts", "driver=null-co,size={},read-zeroes=on".format(length),
    ]
    # compare exits with 1 if the range differs, which ssh_run would log as a failure
    rc, out, err = ssh_run(host, " ".join(shlex.quote(arg) for arg in args) + "; echo $?")
    result = out.strip().splitlines()[-1] if rc == 0 and out.strip() else None
    if result not in ("0", "1"):
        raise RuntimeError("qemu-img compare failed for {} on {}: {}".format(path, host, err.strip()))
    return result == "0"


def block_device_size(host: str, device_path: str) -> int:
    """
    :param host: host with the device
    :param device_path: block device
    :return: size of the device in bytes
    """
    rc, out, err = ssh_run(host, "blockdev --getsize64 {}".format(shlex.quote(device_path)))
    if rc != 0:
        raise RuntimeError("Could not get the size of {} on {}: {}".format(device_path, host, err.strip()))
    return int(out.strip())


def copy_to_device(copy_command: str, host: str, device_path: str, sparse: bool = False) -> int:
    """
    Writes the output of copy_command to the block device on host and returns the number of bytes.

    :param copy_command: local command writing the data to stdout
    :param host: host with the device
    :param device_path: block device
    :param sparse: don't write zero blocks, the device has to read as zeros (a new thin volume)
    :return: bytes written
    """
    conv = "fsync,sparse" if sparse else "fsync"
    remote_cmd = "LC_ALL=C dd of={d} bs=2M iflag=fullblock oflag=direct conv={c}".format(
        d=shlex.quote(device_path), c=conv)
    cmd = "set -o pipefail; {c} | ssh {h} {r}".format(c=copy_command, h=shlex.quote(host), r=shlex.quote(remote_cmd))
    log_info("Copying to {d} on {h}: {c}".format(d=device_path, h=host, c=cmd))
    proc = subprocess.run(["bash", "-c", cmd], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)
    err = proc.stderr.decode(errors="replace")
    if proc.returncode != 0:
        raise RuntimeError("Error copying data to {} on {}: {}".format(device_path, host, err.strip()))
    # dd's statistics: "<bytes> bytes (...) copied, ..."
    copied = re.findall(r"^(\d+) bytes", err, re.MULTILINE)
    if not copied:
        raise RuntimeError("No size of the data copied to {} on {}: {}".format(device_path, host, err.strip()))
    return int(copied[-1])


def raw_source_image_opts(path: str, image_format: str, size: int, offset: int = 0) -> str:
    """
    Returns qemu-img --image-opts for size bytes of the image on the block device at path, starting at offset.

    :param path: block device with the image
    :param image_format: format of the image file, as qemu-img info reports it
    :param size: bytes to read, a multiple of 512
    :param offset: first byte to read, a multiple of 512
    :return: image options
    """
    filename = path.replace(",", ",,")
    raw = "driver=raw,{o}size={s}".format(o="offset={},".format(offset) if offset else "", s=size)
    if image_format == "raw":
        return "{r},file.driver=host_device,file.filename={f}".format(r=raw, f=filename)
    return "{r},file.driver={d},file.file.driver=host_device,file.file.filename={f}".format(
        r=raw, d=image_format, f=filename)


def convert_to_raw(
        host: str, path: str, image_format: str, device_path: str, target_is_zero: bool = False,
        size: Optional[int] = None) -> None:
    """
    Writes the image file at path as raw data to the block device on host.

    :param host: host with the image file and the device
    :param path: image file
    :param image_format: format of the image file, as qemu-img info reports it
    :param device_path: block device, at least as large as the image's virtual size or size
    :param target_is_zero: the device reads as zeros (a new thin volume), the zero areas are not written
    :param size: write only the first size bytes of the image, the rest must read as zeros
    """
    # -W, -m: several writes at once and out of order. DRBD's peers flush after each group of writes that were in
    # flight together, one write at a time makes thin pools commit their metadata for nearly every write
    args = ["qemu-img", "convert", "-q", "-n", "-t", "none", "-O", "raw", "-W", "-m", "16"]
    if target_is_zero:
        args.append("--target-is-zero")
    if size is None:
        args += ["-f", image_format, path, device_path]
    else:
        args += ["--image-opts", raw_source_image_opts(path, image_format, size), device_path]

    rc, _, err = ssh_run(host, " ".join(shlex.quote(arg) for arg in args))
    if rc != 0:
        raise RuntimeError("Converting {} to raw on {} failed: {}".format(path, host, err.strip()))


def _get_one_version_str():
    with open(REMOTES_DIR + "VERSION") as version_file:
        return version_file.readline().strip()


def _one_version_parse(version_info_str=None):
    """
    Returns the opennebula version as tuple.

    :param str version_info_str: string with OpenNebula version info
    :return: Tuple with major, minor, patch version
    :rtype: (int, int, int)
    """
    output = _get_one_version_str() if version_info_str is None else version_info_str
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", output)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return 0, 0, 0


def one_version_larger(major=5, minor=0, patch=None, version_info_str=None):
    inst_major, inst_minor, inst_patch = _one_version_parse(version_info_str)
    if inst_major > major:
        return True
    elif major == inst_major:
        if inst_minor > minor:
            return True
        if patch is not None and inst_minor == minor and inst_patch > patch:
            return True
    return False


def get_copy_command(path, md5="", sha1="", no_decompress="", limit_transfer_bw=""):
    """
    Returns the shell command that writes the image at path to stdout using OpenNebula's downloader.sh.

    Builds the same arguments as set_downloader_args from libfs.sh, but quotes every one of them,
    as they come from the user controlled image template.

    :param str path: image path or URL
    :param str md5: expected md5 checksum
    :param str sha1: expected sha1 checksum
    :param str no_decompress: "yes" to skip decompression
    :param str limit_transfer_bw: transfer bandwidth limit
    :return: shell command string
    :rtype: str
    """
    args = [DOWNLOADER]
    if md5:
        args += ["--md5", md5]
    if sha1:
        args += ["--sha1", sha1]
    if no_decompress.lower() == "yes":
        args.append("--nodecomp")
    if limit_transfer_bw:
        args += ["--limit", limit_transfer_bw]
    args += [path, "-"]
    return " ".join(shlex.quote(arg) for arg in args)


class Terminated(Exception):
    """The driver action got SIGTERM, OpenNebula sends it when the action runs into its timeout"""


def _raise_terminated(signum: int, frame: Optional[FrameType]) -> None:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)  # let the cleanup finish
    raise Terminated("Terminated by signal {}".format(signum))


def run_main(main_func):
    # the default action ends the process right away: no finally or except block would clean up
    signal.signal(signal.SIGTERM, _raise_terminated)
    try:
        main_func()
    except subprocess.CalledProcessError as cpe:
        log_error(traceback.format_exc())
        traceback.print_exc(file=sys.stderr)
        print("ERROR: Command {c} returned error: {o}".format(c=cpe.cmd, o=cpe.stdout + cpe.stderr), file=sys.stderr)
        sys.exit(2)
    except Exception as err:
        log_error(traceback.format_exc())
        traceback.print_exc(file=sys.stderr)
        print("ERROR: " + str(err), file=sys.stderr)
        sys.exit(1)


def get_datastore_args(expected_arg_count=2):
    arg_image_id = None
    if one_version_larger(6, 6):
        outstr = io.BytesIO()
        base64.decode(sys.stdin, outstr)
        arg_driver_action = outstr.getvalue().decode()
        if expected_arg_count > 1:
            arg_image_id = sys.argv[1]
    else:
        arg_driver_action = base64.b64decode(sys.argv[1])
        if expected_arg_count > 1:
            arg_image_id = sys.argv[2]
    return arg_driver_action, arg_image_id
