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
    util.log_info("Entering tm/postmigrate")

    target_vm = vm.Vm(base64.b64decode(TEMPLATE))

    for disk in target_vm.disk_IDs:
        res_name = target_vm.disk_source(disk)

        if target_vm.disk_is_clone(disk) == "YES":
            res_name = "{}-vm{}-disk{}".format(res_name, VM_ID, disk)

        res = resource.Resource(name=res_name)

        if res.is_client(SRC_HOST):
            res.unassign(SRC_HOST)

        res.disable_dual_primary()

    util.log_info("Exiting tm/postmigrate")


if __name__ == "__main__":
    main()
