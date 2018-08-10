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
from one import util

SRC = sys.argv[1]
DST = sys.argv[2]
VM_ID = sys.argv[3]
DS_ID = sys.argv[4]


def main():
    util.log_info("Entering tm ln")

    src_path = util.arg_path(SRC).strip()

    dst_host = util.arg_host(DST).strip()
    dst_path = util.arg_path(DST).strip()
    dst_dir = os.path.dirname(dst_path).strip()

    res = resource.Resource(name=src_path)
    res.assign(dst_host)

    link_command = """cat << EOF
      set -e

      mkdir -p "{}"

      ln -fs "{}" "{}"
    EOF""".format(
        dst_dir, res.path, dst_path
    )

    util.ssh_exec_and_log(
        " ".join(
            [
                "'",
                dst_host,
                link_command,
                "'",
                "'",
                "Error: Unable to link {} to {} on {}".format(
                    res.name, dst_path, dst_host
                ),
                "'",
            ]
        )
    )

    util.log_info("Exiting tm ln")


if __name__ == "__main__":
    main()
