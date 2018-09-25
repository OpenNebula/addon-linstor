#!/usr/bin/env python
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


import base64
import sys

from linstor_helper import resource
from one import util, vm

SRC_HOST = sys.argv[1]
DST_HOST = sys.argv[2]
DST_PATH = sys.argv[3]
VM_ID = sys.argv[4]
DS_ID = sys.argv[5]
TEMPLATE = sys.argv[6]
SYSTEM_DATASTORE_TM = sys.argv[7]


def main():
    util.log_info("Entering tm/postmigrate")

    target_vm = vm.Vm(base64.b64decode(TEMPLATE))
    src_host = util.arg_host(SRC_HOST).strip()
    dst_dir = util.arg_path(DST_PATH).strip()
    system_datastore_tm = SYSTEM_DATASTORE_TM.strip()

    for disk in target_vm.disk_IDs:
        res_name = target_vm.disk_source(disk)

        if target_vm.disk_is_clone(disk) == "YES":
            res_name = "{}-vm{}-disk{}".format(res_name, VM_ID, disk)

        res = resource.Resource(name=res_name)

        if res.is_client(SRC_HOST):
            res.unassign(SRC_HOST)

        res.disable_dual_primary()

    args = ""
    for arg in sys.argv[1:]:
        args += ' "{}" '.format(arg)

    util.migrate_other(args)

    # [phil] when ssh on system DS we should clean up the symlinks. Since
    # linstor/DRBD assignment might got unassigned some symlinks might
    # be dangling. I think it is cleaner to remove it all if it is a
    # ssh system datastore. This also ceans up the context disk image and
    # other files that happened to be in that directory!

    if system_datastore_tm == "ssh":
        unlink_command = " ".join(["set -e;", "rm -rf {};".format(dst_dir)])
        util.ssh_exec_and_log(
            " ".join(
                [
                    '"{}"'.format(src_host),
                    '"{}"'.format(unlink_command),
                    '"{}"'.format(
                        "Error: Unable to remove directory {} on {}".format(
                            dst_dir, src_host
                        )
                    ),
                ]
            )
        )

    util.log_info("Exiting tm/postmigrate")


if __name__ == "__main__":
    main()
