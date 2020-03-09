# -*- coding: utf-8 -*-
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


from __future__ import print_function

import os
import subprocess
import syslog

REMOTES_DIR = "/var/lib/one/remotes/"

ONE_LOCATION = os.getenv("ONE_LOCATION")
if ONE_LOCATION:
    REMOTES_DIR = os.path.join(ONE_LOCATION, "var/remotes")

SCRIPTS_COMMON = REMOTES_DIR + "/scripts_common.sh"
UTILS_DIR = REMOTES_DIR + "/datastore/"
LIBFS = UTILS_DIR + "libfs.sh"
DOWNLOADER = UTILS_DIR + "downloader.sh"
TM_COMMON = REMOTES_DIR + "/tm/tm_common.sh"


def _source(file, command, string_args=None):
    sourced_cmd = "source {} && {}".format(file, command)
    if string_args:
        sourced_cmd = sourced_cmd + " {}".format(string_args)

    exec_string = ["bash", "-c", sourced_cmd]

    return exec_string


def error_message(msg):
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
        error_message("command {} failed: {}".format(cmd, err))

    return proc.returncode


def _get_subp_out(cmd):
    log_info("running shell command: {}".format(" ".join(cmd)))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if proc.returncode != 0:
        error_message("command {} failed: {}".format(cmd, err.decode()))
        raise subprocess.CalledProcessError

    return out.decode()


def ssh_exec_and_log(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "ssh_exec_and_log", string_args))


def ssh_monitor_and_log(string_args):
    return _get_subp_out(_source(SCRIPTS_COMMON, "ssh_monitor_and_log", string_args))


def exec_and_log(cmd, message):
    rc = _wait_for_subp(["bash", "-c", cmd])

    if int(rc) != 0:
        error_message(message)

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
    link_command = " ; ".join(
        [
            "set -e",
            "mkdir -p {}".format(dst_dir),
            "ln -fs {} {}".format(device_path, dst_path),
        ]
    )
    rc = ssh_exec_and_log(
        " ".join(
            [
                '"{}"'.format(dst_host),
                '"{}"'.format(link_command),
                '"Error: Unable to link {} to {} on {}"'.format(resource_name, dst_path, dst_host),
            ]
        )
    )
    if rc != 0:
        raise RuntimeError("Error: Unable to link {} to {} on {}".format(resource_name, dst_path, dst_host))

    return True


def mkfs_command(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "mkfs_command", string_args))


def mkiso_command(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "$MKISOFS", string_args))


def ssh_make_path(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "ssh_make_path", string_args))


def set_up_datastore(string_args):
    return _wait_for_subp(_source(LIBFS, "set_up_datastore", string_args))


def set_downloader_args(string_args):
    return _get_subp_out(_source(LIBFS, "set_downloader_args", string_args))


def check_restricted(string_args):
    return _get_subp_out(_source(LIBFS, "check_restricted", string_args))


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


def migrate_other(string_args):
    # We're turning off logging here because this gets called with a huge
    # base64 image dump and it's too noisy.
    return _wait_for_subp(_source(TM_COMMON, "migrate_other", string_args), log=False)


def show_vm(vm_id):
    return _get_subp_out(["onevm", "show", "-x", str(vm_id)])


def show_image(image_id):
    return _get_subp_out(["oneimage", "show", "--xml", str(image_id)])


def show_ds(ds_id):
    return _get_subp_out(["onedatastore", "show", "--xml", str(ds_id)])


def fs_size(string_args):
    return _get_subp_out(
        _source(LIBFS, 'UTILS_PATH="{}" fs_size'.format(UTILS_DIR), string_args)
    )


def get_copy_command(string_args):
    return DOWNLOADER + " " + string_args
