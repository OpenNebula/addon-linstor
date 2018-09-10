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


from one import util


def test__source():

    assert util._source("foo.sh", "foo_cmd") == [
        "bash",
        "-c",
        "source foo.sh && foo_cmd",
    ]

    assert util._source("bar.sh", "bar_cmd", "args") == [
        "bash",
        "-c",
        "source bar.sh && bar_cmd args",
    ]

    assert util._source("bar.sh", "bar_cmd", "multi args") == [
        "bash",
        "-c",
        "source bar.sh && bar_cmd multi args",
    ]

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

    assert util._source(
        "/var/lib/one/remotes//scripts_common.sh", "ssh_exec_and_log", args
    ) == [
        "bash",
        "-c",
        'source /var/lib/one/remotes//scripts_common.sh && ssh_exec_and_log "help.computah" "set -e ; mkdir -p /var/lib/one/datastores/115/34 ; ln -fs /dev/drbd1007 /var/lib/one/datastores/115/34/disk.0" "Error: Unable to link OpenNebula-Image-165 to /var/lib/one/datastores/115/34/disk.0 on help.computah"',
    ]
