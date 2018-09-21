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


def main():
    util.log_info("Entering tm/premigrate")

    target_vm = vm.Vm(base64.b64decode(TEMPLATE))
    dst_host = util.arg_host(DST_HOST).strip()
    dst_dir = util.arg_path(DST_PATH).strip()

    for disk in target_vm.disk_IDs:
        res_name = target_vm.disk_source(disk)
        if target_vm.disk_persistent(disk) != "YES":
            res_name = "{}-vm{}-disk{}".format(res_name, VM_ID, disk)
        res = resource.Resource(name=res_name)
        res.assign(DST_HOST)
        res.enable_dual_primary()
        dst_path = "{}/disk.{}".format(dst_dir, disk)

        link_command = " ; ".join(
            [
                "set -e",
                "mkdir -p {}".format(dst_dir),
                "ln -fs {} {}".format(res.path, dst_path),
            ]
        )

        util.ssh_exec_and_log(
            " ".join(
                [
                    '"{}"'.format(dst_host),
                    '"{}"'.format(link_command),
                    '"Error: Unable to link {} to {} on {}"'.format(
                        res.name, dst_path, dst_host
                    ),
                ]
            )
        )

    util.log_info("Exiting tm/premigrate")


if __name__ == "__main__":
    main()
