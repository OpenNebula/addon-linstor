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


import os
import subprocess
from setuptools import setup
from glob import glob

REMOTES_DIR = "/var/lib/one/remotes"
DRIVER_NAME = "linstor"
VERSION_FILE = ".version"

ONE_LOCATION = os.getenv("ONE_LOCATION")
if ONE_LOCATION:
    REMOTES_DIR = os.path.join(ONE_LOCATION, "var/remotes")


def version():
    """Returns project version based on git tags"""
    output = None
    if os.path.isdir(".git"):
        process = subprocess.Popen(
            ["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE
        )
        output, _ = process.communicate()
        if output:
            output = output.decode()
            with open(VERSION_FILE, "w") as f:
                f.write(output)
    elif os.path.isfile(VERSION_FILE):
        with open(VERSION_FILE) as f:
            output = f.readlines()[0]

    if not output:
        output = "v0.0.0"
    output = output.strip()
    if output.startswith("v"):
        output = output[1:]
    return output


setup(
    name="linstor-opennebula",
    version=version(),
    data_files=[
        (os.path.join(REMOTES_DIR, "tm", DRIVER_NAME), glob("tm/*")),
        (os.path.join(REMOTES_DIR, "datastore", DRIVER_NAME), glob("datastore/*")),
    ],
    license="Apache-2.0",
    description="Linstor addon for OpenNebula",
    packages=["one", "linstor_helper"],
    install_requires=[
        "python-linstor>=1.0.11"
    ],
    author="Rene Peinthor <rene.peinthor@linbit.com>",
    author_email="rene.peinthor@linbit.com",
    url="https://github.com/LINBIT/addon-linstor",
    long_description=(
        "A driver for OpenNebula to consume storage from LINSTOR. It supports"
        "volume creation, deletion, resizing, snapshotting."
        "Live-migration of VMs using linstor volumes, with ssh system datastore"
        "and shared system datastore."
    ),
    test_suite="one.tests"
)
