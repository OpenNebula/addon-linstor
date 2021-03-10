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

import unittest

from one import util


class TestUtils(unittest.TestCase):
    VERSION_INFO_5_12_0 = """OpenNebula 5.12.0.3
    Copyright 2002-2020, OpenNebula Project, OpenNebula Systems"""

    VERSION_INFO_5_13_80 = """OpenNebula 5.13.80
Copyright 2002-2021, OpenNebula Project, OpenNebula Systems"""

    VERSION_INFO_6_0_0 = """OpenNebula 6.0.0
    Copyright 2002-2021, OpenNebula Project, OpenNebula Systems"""

    def test__source(self):

        self.assertEqual(util._source("foo.sh", "foo_cmd"), [
                "bash",
                "-c",
                "source foo.sh && foo_cmd",
            ])

        self.assertEqual(util._source("bar.sh", "bar_cmd", "args"), [
                "bash",
                "-c",
                "source bar.sh && bar_cmd args",
            ])

        self.assertEqual(util._source("bar.sh", "bar_cmd", "multi args"), [
                "bash",
                "-c",
                "source bar.sh && bar_cmd multi args",
            ])

        dst_dir = "/var/lib/one/datastores/115/34"
        res_path = "/dev/drbd1007"
        dst_path = "/var/lib/one/datastores/115/34/disk.0"
        dst_host = "help.computah"
        res_name = "OpenNebula-Image-165"

        link_command = " ; ".join(
            [
                "set -e",
                "mkdir -p {}".format(dst_dir),
                "ln -fs {} {}".format(res_path, dst_path),
            ]
        )

        args = " ".join(
            [
                '"{}"'.format(dst_host),
                '"{}"'.format(link_command),
                '"Error: Unable to link {} to {} on {}"'.format(
                    res_name, dst_path, dst_host
                ),
            ]
        )

        self.assertEqual(util._source("/var/lib/one/remotes//scripts_common.sh", "ssh_exec_and_log", args),
                         [
                "bash",
                "-c",
                'source /var/lib/one/remotes//scripts_common.sh && ssh_exec_and_log '
                '"help.computah" "set -e ; mkdir -p /var/lib/one/datastores/115/34 ; '
                'ln -fs /dev/drbd1007 /var/lib/one/datastores/115/34/disk.0" '
                '"Error: Unable to link OpenNebula-Image-165 to /var/lib/one/datastores/115/34/disk.0 on help.computah"'
            ])

    def test_arg_host(self):
        self.assertEqual(util.arg_host("oneb200.linbit:OpenNebula-Image-814"), "oneb200.linbit")
        self.assertEqual(util.arg_host(
            "oneb200.linbit:/var/lib/one//datastores/112/372/disk.0"),
            "oneb200.linbit")
        self.assertEqual(util.arg_host(
            "oneb200.linbit"),
            "oneb200.linbit")
        self.assertEqual(util.arg_host(
            "oneb203.linbit:/var/lib/one//datastores/112/372/disk.1"),
            "oneb203.linbit")
        self.assertEqual(util.arg_host("0"), "0")

    def test_arg_path(self):
        self.assertEqual(util.arg_path("oneb200.linbit:OpenNebula-Image-814"), "OpenNebula-Image-814")
        self.assertEqual(util.arg_path(
            "oneb200.linbit:/var/lib/one//datastores/112/372/disk.0"),
            "/var/lib/one/datastores/112/372/disk.0")
        self.assertEqual(util.arg_path(
            "/var/lib/one//datastores/112/372"),
            "/var/lib/one/datastores/112/372")
        self.assertEqual(util.arg_path(
            "oneb203.linbit:/var/lib/one//datastores/112/372/disk.0"),
            "/var/lib/one/datastores/112/372/disk.0")

    def test_version_checks(self):
        self.assertFalse(util.one_version_larger(5, 12, 0, self.VERSION_INFO_5_12_0))
        self.assertFalse(util.one_version_larger(5, 12, 1, self.VERSION_INFO_5_12_0))
        self.assertFalse(util.one_version_larger(5, 13, 0, self.VERSION_INFO_5_12_0))
        self.assertTrue(util.one_version_larger(5, 11, 0, self.VERSION_INFO_5_12_0))

        self.assertTrue(util.one_version_larger(5, 12, 0, self.VERSION_INFO_5_13_80))
        self.assertTrue(util.one_version_larger(5, 12, 0, self.VERSION_INFO_6_0_0))
