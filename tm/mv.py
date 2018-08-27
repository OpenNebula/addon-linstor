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

SRC = sys.argv[1]
DST = sys.argv[2]
VM_ID = sys.argv[3]
DS_ID = sys.argv[4]


def main():
    util.log_info("Entering tm mv")

    if SRC == DST:
        util.log_info(
            "source ({}) and destination ({}) are the same, exiting.".format(SRC, DST)
        )
        sys.exit(0)

    src_host = util.arg_host(SRC).strip()
    src_path = util.arg_path(SRC).strip()

    disk_ID = SRC.split(".")[1].strip()

    dst_host = util.arg_host(DST).strip()
    dst_path = util.arg_path(DST).strip()
    dst_dir = os.path.dirname(dst_path).strip()

    # Make a new path for the dst_host, remove the src_host's path.
    util.ssh_make_path(" ".join([dst_host, dst_dir]))
    util.ssh_exec_and_log(
        " ".join(
            [
                src_host,
                "rm -rf",
                src_path,
                "Error removing {} on {}".format(src_path, src_host),
            ]
        )
    )

    target_vm = vm.Vm(util.show_vm(VM_ID), disk_ID)

    res_name = target_vm.disk_source

    util.log_info("Moving {}".format(target_vm.disk_target))

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

    res.assign(dst_host)
    # TODO: we should check the bridge list from the datastore to see if src_host is in that list and is therefore a storage node that we shouldn't be unassigning volumes from.
    res.unassign(src_host)

    link_command = " ; ".join(["set -e", "ln -fs {} {}".format(res.path, dst_path)])

    util.ssh_exec_and_log(
        " ".join(
            [
                '"{}"'.format(dst_host),
                '"{}"'.format(link_command),
                '"{}"'.format(
                    "Error: Unable to link {} to {} on {}".format(
                        res_name, dst_path, dst_host
                    )
                ),
            ]
        )
    )

    util.log_info("Exiting tm mv")


if __name__ == "__main__":
    main()
