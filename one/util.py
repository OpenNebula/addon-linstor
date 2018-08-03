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

import os
import subprocess

REMOTES_DIR = "/var/lib/one/remotes/"

ONE_LOCATION = os.getenv("ONE_LOCATION")
if ONE_LOCATION:
    REMOTES_DIR = os.path.join(ONE_LOCATION, "var/remotes")

SCRIPTS_COMMON = REMOTES_DIR+"/scripts_common.sh"
LIBFS = os.path.join(REMOTES_DIR, "/datastore/") + "libfs.sh"


def _source(file, command, args=None):
    sourced_cmd = "source {} && {}".format(file, command)
    if args:
        sourced_cmd = sourced_cmd + " {}".format(" ".join(args))

    exec_string = ["bash", "-c", sourced_cmd]

    return exec_string


def _wait_for_subp(cmd):
    return subprocess.Popen(cmd).wait()


def ssh_exec_and_log(*args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "ssh_exec_and_log", args))


def exec_and_log(*args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "exec_and_log", args))


def error_message(*args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "error_message", args))


def log_info(*args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "log_info", args))


def mkfs_command(*args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "mkfs_command", args))


def set_up_datastore(*args):
    return _wait_for_subp(_source(SCRIPTS_COMMON, "set_up_datastore", args))
