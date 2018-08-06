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
import os
import sys
import xml.etree.ElementTree as ET

from one import util

DRIVER_ACTION = sys.argv[1]
IMAGE_ID = sys.argv[2]


def main():
    util.log_info("Entering datastore stat")

    path = (
        ET.fromstring(base64.b64decode(DRIVER_ACTION)).find("IMAGE").find("PATH").text
    )

    size_MiB = os.path.getsize(path) / 1024 / 1024
    if not size_MiB:
        size_MiB = 4
    print(size_MiB)

    util.log_info("Entering datastore stat")


if __name__ == "__main__":
    main()
