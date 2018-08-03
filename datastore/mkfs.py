#!/usr/bin/env python
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

import base64
import random
import sys

from linstor import resource
from one import driver_action, util

DRIVER_ACTION = sys.argv[1]
IMAGE_ID = sys.argv[2]


def main():
    util.log_info("Entering datastore mkfs.")

    driver = driver_action.DriverAction(base64.b64decode(DRIVER_ACTION))

    res = resource.Resource(
        name="OpenNebula-Image-{}".format(IMAGE_ID),
        sizeMiB=driver.image.size,
        auto_place=driver.datastore.auto_place,
        nodes=driver.datastore.deployment_nodes,
        storage_pool=driver.datastore.storage_pool,
    )

    if driver.image.FS_type == "save_as":
        util.log_info("No need to create new image, exiting.")
        print(res.name)
        sys.exit(0)

    util.set_up_datastore(
        [
            driver.datastore.base_path,
            driver.datastore.restricted_dirs,
            driver.datastore.safe_dirs,
        ].join(" ")
    )

    util.log_info("Creation a new resource: {}".format(res))
    res.deploy()

    register_command = """
    (cat << EOF
      set -e

      export PATH=/usr/sbin:/sbin:\$PATH

      if [ -z "{0}" ] || [ "{0}" == "raw" ]; then
        exit 0
      fi

      $SUDO $(mkfs_command "{1}" "{0}" "{2}")

    EOF
    ) """.format(
        driver.image.FS_type, res.path, res.sizeMiB
    )

    res_host = random.choice(res.deployed_nodes)

    rc = util.ssh_exec_and_log(
        [
            res_host,
            register_command,
            "Error registering {}, on {}".format(res, res_host),
        ].join(" ")
    )

    if int(rc) != 0:
        res.delete()

    util.log_info("Created {} on {}".format(res, res_host))
    util.log_info("Exiting datastore mkfs.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        util.error_message("Failed to mfks: {}".format(e))
        sys.exit(1)
