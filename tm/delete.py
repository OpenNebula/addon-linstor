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

from __future__ import print_function

import os
import sys

from linstor_helper import resource
from one import util, vm

DST = sys.argv[1]
VM_ID = sys.argv[2]
DS_ID = sys.argv[3]


def main():
    util.log_info("Entering tm delete")

    dst_host = util.arg_host(DST).strip()
    dst_path = util.arg_path(DST).strip()
    os.path.dirname(dst_path).strip()

    disk_ID = dst_path.split(".")[1].strip()

    unlink_command = """cat << EOF
      set -e

      rm -f "{}"
    EOF""".format(
        dst_path
    )

    util.ssh_exec_and_log(
        " ".join(
            [
                dst_host,
                unlink_command,
                "Error: Unable to remove symbloic link {} on {}".format(
                    dst_path, dst_host
                ),
            ]
        )
    )

    target_vm = vm.Vm(util.show_vm(VM_ID), disk_ID)

    res_name = target_vm.disk_source

    if not target_vm.disk_persistent:
        if target_vm.disk_type == "CDROM":
            util.log_info("{} is a non-persistent CDROM image".format(res_name))
        else:
            res_name = "{}-vm{}-disk{}".format(res_name, VM_ID, disk_ID)
            util.log_info(
                "{} is a non-persistent OS or DATABLOCK image".format(res_name)
            )
    else:
        util.log_info("{} is a persistent OS or DATABLOCK image".format(res_name))

    res = resource.Resource(name=res_name)

    res.unassign(dst_host)

    util.log_info("Exiting tm delete")


if __name__ == "__main__":
    main()
