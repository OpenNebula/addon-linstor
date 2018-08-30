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

import sys

from linstor_helper import resource
from one import util, vm

SRC = sys.argv[1]
DST = sys.argv[2]
VM_ID = sys.argv[4]
DS_ID = sys.argv[5]


def main():
    util.log_info("Entering tm cpds")

    disk_ID = SRC.split(".")[-1].strip()

    target_vm = vm.Vm(util.show_vm(VM_ID), disk_ID)

    res_name = target_vm.disk_source
    if not target_vm.disk_persistent:
        res_name = "{}-vm{}-disk{}".format(res_name, VM_ID, disk_ID)

    res = resource.Resource(name=res_name)
    clone = resource.Resource(name=DST)

    res.clone(clone.name)

    util.log_info("Exiting tm cpds")


if __name__ == "__main__":
    main()
