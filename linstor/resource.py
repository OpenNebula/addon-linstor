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

import json
import subprocess

import one


class Resource(object):

    """Interface for interacting with Linstor"""

    def __init__(
        self,
        name=None,
        controllers=None,
        nodes=None,
        auto_place=None,
        sizeMiB=1024,
        storage_pool="DfltStorPool",
    ):
        self._name = name
        self._controllers = controllers
        self._nodes = nodes
        self._storage_pool = storage_pool
        if not auto_place or nodes:
            self._auto_place = 1
        self._path = None
        self._sizeMib = sizeMiB

    def deploy(self):
        self._run_command(["rd", "c", self.name])
        self._run_command(["vd", "c", self.sizeMiB + "MiB"])

        if self.nodes:
            self._run_command(
                ["r", "c", " ".join(self.nodes), self.name, "-s", self.storage_pool],
                clean_on_failure=True,
            )

        if self.auto_place:
            self._run_command(
                [
                    "r",
                    "c",
                    self.name,
                    "--auto-place",
                    self.auto_place,
                    "-s",
                    self._storage_pool,
                ],
                clean_on_failure=True,
            )

        self.path = self.list()
        return

    def delete(self):
        self._run_command(["rd", "d", self.name])

    def list(self):
        self._run_command(["r", "l"])

    def deployed_nodes(self):
        return self._deployed_nodes(json.loads(self.list())[0]["resources"])

    def _deployed_nodes(self, res_states):
        return list(
            map(lambda x: x["node_name"], filter(self._match_nodes, res_states))
        )

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, list_output):
        res_states = json.loads(list_output)[0]["resources"]
        self._path = list(
            filter(
                lambda x: x["vlm_nr"] == 0,
                list(map(lambda x: x["vlms"], filter(self._match_nodes, res_states)))[
                    0
                ],
            )
        )[0]["device_path"]

    @property
    def nodes(self):
        return self._nodes

    @property
    def name(self):
        return self._name

    @property
    def storage_pool(self):
        return self._storage_pool

    @property
    def sizeMiB(self):
        return self._sizeMib

    @property
    def auto_place(self):
        return self._auto_place

    def _run_command(self, command, clean_on_failure=False):
        command = ["linstor", "-m", "--controllers", self._controllers].extend(command)

        one.util.log_info("({}) {}".format(self.name, command))

        try:
            return subprocess.check_output(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            one.util.error_message(e.output)
            if clean_on_failure:
                self.delete()
            raise

    def _match_nodes(self, res_states):
        return self._name == res_states["name"]
