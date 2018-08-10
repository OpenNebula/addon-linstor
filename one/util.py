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
import shlex
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
    syslog.syslog(syslog.LOG_ERR, msg)


def log_info(msg):
    syslog.syslog(syslog.LOG_INFO, "INFO {}".format(msg))


def _wait_for_subp(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, err = proc.communicate()

    if proc.returncode != 0:
        error_message("command {} failed: {}".format(cmd, err))

    return proc.returncode


def _get_subp_out(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if proc.returncode != 0:
        error_message("command {} failed: {}".format(cmd, err))
        raise subprocess.CalledProcessError

    return out


def ssh_exec_and_log(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "ssh_exec_and_log", string_args))


def exec_and_log(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "exec_and_log", string_args))


def mkfs_command(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "mkfs_command", string_args))


def ssh_make_path(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "ssh_make_path", string_args))


def set_up_datastore(string_args):
    return _wait_for_subp(_source(LIBFS, "set_up_datastore", string_args))


def set_downloader_args(string_args):
    return _get_subp_out(_source(LIBFS, "set_downloader_args", string_args))


def check_restricted(string_args):
    return _get_subp_out(_source(LIBFS, "check_restricted", string_args))


def arg_host(string_args):
    return _get_subp_out(_source(TM_COMMON, "arg_host", string_args))


def arg_path(string_args):
    return _get_subp_out(_source(TM_COMMON, "arg_path", string_args))


def show_vm(vm_ID):
    return _get_subp_out(shlex.split("onevm show -x {}".format(vm_ID)))


def fs_size(string_args):
    return _get_subp_out(
        _source(LIBFS, 'UTILS_PATH="{}" fs_size'.format(UTILS_DIR), string_args)
    )


def get_copy_command(string_args):
    return DOWNLOADER + " " + string_args
