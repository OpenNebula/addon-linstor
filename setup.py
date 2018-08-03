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

import os
import pwd
import subprocess
from distutils.core import setup
from glob import glob

from setuptools.command.install import install

REMOTES_DIR = "/var/lib/one/remotes"
DRIVER_NAME = "linstor"

ONE_LOCATION = os.getenv("ONE_LOCATION")
if ONE_LOCATION:
    REMOTES_DIR = os.path.join(ONE_LOCATION, "var/remotes")

ONE_USER = os.getenv("ONE_USER", pwd.getpwuid(os.getuid()).pw_name)


def version():
    """Returns project version based on git tags"""
    process = subprocess.Popen(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    output, _ = process.communicate()
    if not output:
        return "v0.0.0"
    return output


class OverrideInstall(install):
    def run(self):
        install.run(self)

        usr = pwd.getpwnam(ONE_USER)
        mode = 0o755

        for filepath in self.get_outputs():
            if REMOTES_DIR in filepath:
                endpoint = filepath.strip(".py")
                os.rename(filepath, endpoint)
                os.chown(endpoint, usr.pw_uid, usr.pw_gid)
                os.chmod(endpoint, mode)


setup(
    name="addon-linstor",
    version=version(),
    data_files=[
        (os.path.join(REMOTES_DIR, "tm", DRIVER_NAME), glob("tm/*")),
        (os.path.join(REMOTES_DIR, "datastore", DRIVER_NAME), glob("datastore/*")),
    ],
    license="GLP2",
    description="Linstor addon for OpenNebula",
    packages=["one", "linstor"],
    author="Hayley Swimelar",
    author_email="hayley@linbit.com",
    url="https://github.com/LINBIT/addon-linstor",
    cmdclass={"install": OverrideInstall},
)
