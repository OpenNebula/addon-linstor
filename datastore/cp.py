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
import shlex
import sys

from linstor_helper import resource
from one import driver_action, util

DRIVER_ACTION = sys.argv[1]
IMAGE_ID = sys.argv[2]


def main():
    util.log_info("Entering datastore cp")

    driver = driver_action.DriverAction(base64.b64decode(DRIVER_ACTION))

    res = resource.Resource(
        name="OpenNebula-Image-{}".format(IMAGE_ID),
        sizeMiB=driver.image.size,
        auto_place=driver.datastore.auto_place,
        nodes=driver.datastore.deployment_nodes,
        storage_pool=driver.datastore.storage_pool,
    )

    res.deploy()

    util.set_up_datastore(
        " ".join(
            [
                driver.datastore.base_path,
                driver.datastore.restricted_dirs,
                driver.datastore.safe_dirs,
            ]
        )
    )

    downloader_args = util.set_downloader_args(
        " ".join(
            [
                driver.image.md5,
                driver.image.sha1,
                driver.image.no_decompress,
                driver.image.limit_transfer_bw,
                driver.image.path,
                "-",
            ]
        )
    )

    copy_command = util.get_copy_command(downloader_args)

    if driver.image.path.startswith("http"):
        util.log_info(
            "Downloading {} to the image repository".format(driver.image.path)
        )

        if int(util.check_restricted(driver.image.path)) == 1:
            util.error_message(
                "Not allowed to copy images from {}".format(
                    driver.datastore.restricted_dirs
                )
            )
            util.error_message(
                "Not allowed to copy image file {}".format(driver.image.path)
            )

            res.delete()

        util.log_info(
            "Copying local image {} to the image repository".format(driver.image.path)
        )

    hosts = res.deployed_nodes()

    rc = util.ssh_exec_and_log(
        [
            "eval",
            copy_command,
            "|",
            "ssh",
            res.get_node_interface(hosts[0]),
            "dd",
            "of={}".format(res.path),
            "bs=2M",
            "Error registering {}, on {}".format(res, hosts[0]),
        ]
    )

    if int(rc) != 0:
        res.delete()
        sys.exit(1)

    util.log_info("Exiting datastore cp")


if __name__ == "__main__":
    main()
