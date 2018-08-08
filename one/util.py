# -*- coding: utf-8 -*-
"""
Linstor addon for OpenNebula
Copyright © 2018 LINBIT USA, LLC

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
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


def _wait_for_subp(cmd):
    return subprocess.Popen(cmd).wait()


def _get_subp_out(cmd):
    out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
    return out


def ssh_exec_and_log(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "ssh_exec_and_log", string_args))


def exec_and_log(string_args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "exec_and_log", string_args))


def error_message(msg):
    syslog.syslog(syslog.LOG_ERR, msg)


def log_info(msg):
    syslog.syslog(syslog.LOG_INFO, "INFO {}".format(msg))


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
