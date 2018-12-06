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

import json
import subprocess
import time
from contextlib import contextmanager

from one import util


class CloneMode(object):
    SNAPSHOT = 1
    COPY = 2

    __STR_MAP = {
        "snapshot": SNAPSHOT,
        "copy": COPY
    }

    @classmethod
    def from_str(cls, clone_mode):
        return cls.__STR_MAP.get(clone_mode)


class Resource(object):
    """Interface for interacting with Linstor"""

    def __init__(
        self,
        name=None,
        controllers=None,
        nodes=None,
        auto_place=None,
        sizeMiB=4,
        storage_pool="DfltStorPool",
    ):
        self._name = name
        self._controllers = controllers
        self._nodes = nodes
        self._storage_pool = storage_pool
        self._auto_place = auto_place
        if not auto_place or nodes:
            self._auto_place = 1
        self._path = None
        self._sizeMiB = sizeMiB
        self._storage_pool_free_MiB = None
        self._storage_pool_used_MiB = None
        self._storage_pool_total_MiB = None

    def __str__(self):
        return "resource name: {}, size in MiB: {}, storage_pool: {}, auto_place: {}, nodes: {}".format(
            self.name, self.sizeMiB, self.storage_pool, self.auto_place, self.nodes
        )

    def deploy(self):
        with self._autoclean(Autocleaner(res_name=self.name)):
            self._run_command(["resource-definition", "create", self.name])
            self._run_command(
                ["volume-definition", "create", self.name, self.sizeMiB + "MiB"]
            )

            if self.nodes:
                self._run_command(
                    [
                        "resource",
                        "create",
                        " ".join(self.nodes),
                        self.name,
                        "-s",
                        self.storage_pool,
                    ]
                )

            if self.auto_place:
                self._run_command(
                    [
                        "resource",
                        "create",
                        self.name,
                        "--auto-place",
                        self.auto_place,
                        "-s",
                        self._storage_pool,
                    ]
                )

    def snap_create(self, snap_name):
        with self._autoclean(Autocleaner(res_name=self.name, snap_name=snap_name)):
            self._run_command(["snapshot", "create", self.name, snap_name])

    def snap_delete(self, snap_name):
        self._run_command(["snapshot", "delete", self.name, snap_name])

    def clone(self, clone_name, mode=CloneMode.SNAPSHOT):
        return_code = 0
        if mode == CloneMode.SNAPSHOT:
            snap_name = "for-" + clone_name
            with self._autoclean(Autocleaner(res_name=self.name, snap_name=snap_name)):
                self.snap_create(snap_name)
                with self._autoclean(Autocleaner(res_name=clone_name)):
                    self._res_from_snap(snap_name, clone_name)
                    time.sleep(1)  # wait a second for deletion, here is a potential race condition
            self.snap_delete(snap_name)
        elif mode == CloneMode.COPY:
            clone_res = Resource(
                name=clone_name,
                controllers=self._controllers,
                nodes=self.nodes,
                auto_place=self._auto_place,
                sizeMiB=self._sizeMiB,
                storage_pool=self.storage_pool
            )
            clone_res.deploy()
            nodes = self.deployed_nodes()
            cloned_nodes = clone_res.deployed_nodes()
            copy_node = nodes[0]
            was_already_assigned = copy_node in cloned_nodes
            clone_res.assign(copy_node)

            from_dev_path = self.path
            to_dev_path = clone_res.path
            block_count = int(self._sizeMiB) * 1024 / 64 + 1

            conv_opts = ["sync"]
            if self.is_thin(self.storage_pool):
                conv_opts.append("sparse")

            dd_cmd = '"dd if={_if} of={_of} bs=64K count={c} conv={conv}"'.format(
                _if=from_dev_path,
                _of=to_dev_path,
                c=block_count,
                conv=",".join(conv_opts)
            )
            # dd on the node
            return_code = util.ssh_exec_and_log(
                " ".join([
                    '"{}"'.format(copy_node),
                    dd_cmd,
                    '"error copying image data from {_if} to {_of}"'.format(_if=from_dev_path, _of=to_dev_path)
                ])
            )

            if not was_already_assigned:
                clone_res.unassign(copy_node)

        return return_code == 0

    def snap_flatten(self, snap_name):
        tmp_res_name = self.name + "-flatten"

        # Create a tmp resource created from snapshot data and delete
        # the original.
        with self._autoclean(Autocleaner(res_name=tmp_res_name)):
            tmp = self._res_from_snap(snap_name, tmp_res_name)
        self.delete()

        # Clone the tmp data into a new resource using the previous
        # resource's name and delete the tmp resource.
        tmp.clone(self.name)
        tmp.delete()

    def _res_from_snap(self, snap_name, res_name):
        self._run_command(["resource-definition", "create", res_name])
        self._run_command(
            [
                "snapshot",
                "volume-definition",
                "restore",
                "--from-resource",
                self.name,
                "--from-snapshot",
                snap_name,
                "--to-resource",
                res_name,
            ]
        )
        self._run_command(
            [
                "snapshot",
                "resource",
                "restore",
                "--from-resource",
                self.name,
                "--from-snapshot",
                snap_name,
                "--to-resource",
                res_name,
            ]
        )

        return Resource(name=res_name)

    def delete(self):
        # Resource definitions cannot be removed if they contain snapshots.
        for snap in self.snapshots():
            self.snap_delete(snap)

        # Looks like deleting snapshots is actually async, poll to give it
        # time to clear.
        for _ in range(10):
            snaps = self.snapshots()
            if snaps:
                util.log_info(
                    "snapshots still remaining on {}: {}".format(self.name, snaps)
                )
                time.sleep(1)
            else:
                break
        else:
            raise RuntimeError(
                "Failed to remove snapshots from image after 10 tries. Unable to delete"
            )

        self._run_command(["resource-definition", "delete", self.name])

    def list(self):
        return self._run_command(["-m", "resource", "list"])

    def deployed_nodes(self):
        return self._deployed_nodes(json.loads(self.list())[0].get("resources", {}))

    def assign(self, node):
        if node in self.deployed_nodes():
            return "0"
        return self._run_command(["resource", "create", node, self.name, "--diskless"])

    def unassign(self, node):
        return self._run_command(["resource", "delete", node, self.name])

    def enable_dual_primary(self):
        self._run_command(
            [
                "resource-definition",
                "drbd-options",
                self.name,
                "--allow-two-primaries",
                "yes",
            ]
        )

    def disable_dual_primary(self):
        self._run_command(
            [
                "resource-definition",
                "drbd-options",
                self.name,
                "--allow-two-primaries",
                "no",
            ]
        )

    def snapshots(self):
        return self._snapshots(
            json.loads(self._run_command(["-m", "snapshot", "list"]))[0].get(
                "snapshot_dfns", {}
            )
        )

    def _snapshots(self, snap_list):
        return list(
            map(
                lambda x: x["snapshot_name"],
                filter(lambda x: x["rsc_name"] == self.name, snap_list),
            )
        )

    def _deployed_nodes(self, res_states):
        return list(
            map(lambda x: x["node_name"], filter(self._match_nodes, res_states))
        )

    def get_node_interface(self, node):
        return self._get_node_interface(
            self._run_command(["-m", "node", "interface", "list", node]), node
        )

    @staticmethod
    def _get_node_interface(interface_list, node):
        interface_data = json.loads(interface_list)[0].get("nodes", {})
        return list(filter(lambda x: x["name"] == node, interface_data))[0][
            "net_interfaces"
        ][0]["address"]

    @property
    def path(self):
        if self._path is None:
            self.path = self.list()
        return self._path

    @path.setter
    def path(self, list_output):
        res_states = json.loads(list_output)[0].get("resources", {})
        try:
            self._path = list(
                filter(
                    lambda x: x["vlm_nr"] == 0 and "device_path" in x,
                    list(
                        map(lambda x: x["vlms"], filter(self._match_nodes, res_states))
                    )[0],
                )
            )[0]["device_path"]
        except (KeyError, IndexError):
            util.error_message(
                "Unable to locate device path for {}, please ensure the health of this reource".format(
                    self.name
                )
            )
            raise

    def is_client(self, target_node):
        return self._is_client(self.list(), target_node)

    def _is_client(self, list_output, target_node):
        res_states = json.loads(list_output)[0].get("resources", {})

        deployment_state = list(
            filter(
                lambda x: x["node_name"] == target_node and x["name"] == self.name,
                res_states,
            )
        )
        try:
            return "DISKLESS" in deployment_state[0].get("rsc_flags", [])
        except IndexError:
            util.error_message(
                "Unable to find {} or {} in {}".format(
                    self.name, target_node, res_states
                )
            )
            raise

    def is_thin(self, stor_pool_name):
        sp_list_out = self._run_command(["-m", "storage-pool", "list", "-s", stor_pool_name])
        storpools = json.loads(sp_list_out)[0]["stor_pools"]
        return storpools[0]["driver"] in ["LvmThinDriver", "ZfsThinDriver"]

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
        if int(self._sizeMiB) < 4:
            return "4"
        return str(self._sizeMiB)

    def update_size(self):
        """
        Update the resource size by querying linstor
        :return: True if update was successful, else False
        :rtype: bool
        """
        list_data = json.loads(self._run_command(["-m", "volume-definition", "list"]))[0]
        rsc_dfns = list_data.get('rsc_dfns', [])
        rsc_dfn = [x for x in rsc_dfns if x['rsc_name'].lower() == self._name.lower()]
        if rsc_dfn:
            if 'vlm_dfns' in rsc_dfn[0]:
                self._sizeMiB = rsc_dfn[0]['vlm_dfns'][0]['vlm_size'] / 1024
                return True
        return False

    @property
    def auto_place(self):
        if self._auto_place is None:
            return None
        return str(self._auto_place)

    @property
    def storage_pool_free_MiB(self):
        if self._storage_pool_free_MiB is None:
            self.update_storage_info()
        return self._storage_pool_free_MiB

    @property
    def storage_pool_used_MiB(self):
        if self._storage_pool_used_MiB is None:
            self.update_storage_info()
        return self._storage_pool_used_MiB

    @property
    def storage_pool_total_MiB(self):
        if self._storage_pool_total_MiB is None:
            self.update_storage_info()
        return self._storage_pool_total_MiB

    def update_storage_info(self):
        self._update_storage_info(self._run_command(["-m", "storage-pool", "list"]))

    def _update_storage_info(self, sp_info):
        pool_data = json.loads(sp_info)[0].get("stor_pools", {})
        self._storage_pool_total_MiB = 0
        self._storage_pool_free_MiB = 0
        self._storage_pool_used_MiB = 0

        free_space_by_node = {}

        for pool in list(
            filter(lambda x: x["stor_pool_name"] == self.storage_pool, pool_data)
        ):
            free_space_by_node[pool["node_name"]] = pool["free_space"]

        if self.nodes:
            lowest_free_node = self.nodes[0]
            for node in self.nodes:
                try:
                    if (
                        free_space_by_node[node]["total_capacity"]
                        < free_space_by_node[node]["total_capacity"]
                    ):
                        lowest_free_node = node
                except KeyError:
                    util.error_message(
                        "Node {} does not appear to contain storage pool {}".format(
                            self.name, self.storage_pool
                        )
                    )
                    raise
            self._storage_pool_total_MiB += (
                free_space_by_node[lowest_free_node].get("total_capacity", 0) // 1024
            )
            self._storage_pool_free_MiB += (
                free_space_by_node[lowest_free_node].get("free_capacity", 0) // 1024
            )
        else:
            for space_info in free_space_by_node.values():
                self._storage_pool_total_MiB += (
                    space_info.get("total_capacity", 0) // int(self.auto_place)
                ) // 1024
                self._storage_pool_free_MiB += (
                    space_info.get("free_capacity", 0) // int(self.auto_place)
                ) // 1024

        self._storage_pool_used_MiB = (
            self._storage_pool_total_MiB - self._storage_pool_free_MiB
        )

    def _run_command(self, command):
        client_opts = ["linstor", "--no-color"]
        if self._controllers:
            client_opts += ["--controllers", self._controllers]
        final = client_opts + command

        util.log_info("running linstor {}".format(" ".join(command)))

        try:
            return subprocess.check_output(
                " ".join(final), shell=True, stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as cpe:
            util.error_message(cpe.output)
            raise

    def _match_nodes(self, res_states):
        return self._name == res_states["name"]

    @contextmanager
    def _autoclean(self, cleaner):

        try:
            yield
        except subprocess.CalledProcessError:
            cleaner.clean()

            raise


class Autocleaner(object):
    def __init__(self, res_name=None, snap_name=None):
        self._res_name = res_name
        self._snap_name = snap_name

    def clean(self):
        # Create a new resource to protect current instance in the case of
        # failed clones with healthy parent resources.

        failed_res = Resource(name=self._res_name)

        if self._snap_name:
            failed_res.snap_delete(self._snap_name)
        else:
            failed_res.delete()
