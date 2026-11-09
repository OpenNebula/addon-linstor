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
import importlib.util
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from one import vm

HAS_LINSTOR = importlib.util.find_spec("linstor") is not None

if HAS_LINSTOR:
    from one import extender

VM_XML = """
<VM>
  <ID>7</ID>
  <TEMPLATE>
    <DISK>
      <DISK_ID><![CDATA[0]]></DISK_ID>
      <PERSISTENT><![CDATA[YES]]></PERSISTENT>
      <SOURCE><![CDATA[OpenNebula-Image-10]]></SOURCE>
      <TYPE><![CDATA[BLOCK]]></TYPE>
    </DISK>
    <DISK>
      <DISK_ID><![CDATA[1]]></DISK_ID>
      <PERSISTENT><![CDATA[NO]]></PERSISTENT>
      <SOURCE><![CDATA[OpenNebula-Image-11]]></SOURCE>
      <TYPE><![CDATA[BLOCK]]></TYPE>
    </DISK>
    <DISK>
      <DISK_ID><![CDATA[2]]></DISK_ID>
      <SOURCE><![CDATA[OpenNebula-Image-12]]></SOURCE>
      <TYPE><![CDATA[BLOCK]]></TYPE>
    </DISK>
    <DISK>
      <DISK_ID><![CDATA[3]]></DISK_ID>
      <SOURCE><![CDATA[OpenNebula-Image-13]]></SOURCE>
      <TYPE><![CDATA[CDROM]]></TYPE>
    </DISK>
    <DISK>
      <DISK_ID><![CDATA[4]]></DISK_ID>
      <TYPE><![CDATA[fs]]></TYPE>
    </DISK>
  </TEMPLATE>
</VM>
"""


@unittest.skipUnless(HAS_LINSTOR, "python-linstor not installed")
class TestExtender(unittest.TestCase):
    def test_get_rsc_name(self):
        test_vm = vm.Vm(VM_XML)

        self.assertEqual(extender.get_rsc_name(test_vm, "0"), "OpenNebula-Image-10")
        # PERSISTENT=NO and a missing PERSISTENT element are both non-persistent clones
        self.assertEqual(extender.get_rsc_name(test_vm, "1"), "OpenNebula-Image-11-vm7-disk1")
        self.assertEqual(extender.get_rsc_name(test_vm, "2"), "OpenNebula-Image-12-vm7-disk2")
        # non-persistent CDROMs use the shared image resource
        self.assertEqual(extender.get_rsc_name(test_vm, "3"), "OpenNebula-Image-13")
        self.assertEqual(extender.get_rsc_name(test_vm, "4"), "OpenNebula-Volatile-vm7-disk4")

    def test_clone_copy_takes_the_whole_device(self):
        # a clone into another resource group copies with dd: the DRBD device is larger than the volume size
        calls = []
        device_size = 3761446912

        class Resource:
            name = "OpenNebula-Image-11"
            resource_group_name = "one-image"
            client = SimpleNamespace(uri_list=["linstor://controller"])
            placement = SimpleNamespace(storage_pool="thin")
            volumes = [SimpleNamespace(size=3758096384, storage_pool_name="thin")]

            def diskful_nodes(self):
                return ["node1", "node2"]

        clone_res = SimpleNamespace(
            name="OpenNebula-Image-11-vm28-disk0",
            activate=lambda node: calls.append(("activate", node)),
            deactivate=lambda node: calls.append(("deactivate", node)),
            is_thin=lambda: True)

        def deploy(**kwargs):
            calls.append(("deploy", kwargs["vlm_size_str"]))
            return clone_res

        for new_size, vlm_size_str in [(None, "3761446912b"), (3584, "3761446912b"), (4096, "4294967296b")]:
            del calls[:]
            with patch.object(extender, "wait_resource_ready"), \
                    patch.object(extender, "get_in_use_node", return_value=None), \
                    patch.object(extender, "deploy", deploy), \
                    patch.object(extender.time, "sleep"), \
                    patch.object(extender.util, "block_device_size", return_value=device_size) as size, \
                    patch.object(extender.util, "ssh_exec_and_log",
                                 side_effect=lambda host, cmd, error_msg: calls.append(("ssh", host, cmd)) or 0):
                success, native = extender.clone(Resource(), clone_res.name, resource_group="one-image-2",
                                                 prefer_node="node2", new_size=new_size)

            self.assertTrue(success)
            self.assertFalse(native)
            size.assert_called_once_with("node2", "/dev/drbd/by-res/OpenNebula-Image-11/0")
            self.assertEqual(calls, [
                ("deploy", vlm_size_str),
                ("activate", "node2"),
                ("ssh", "node2", "dd if=/dev/drbd/by-res/OpenNebula-Image-11/0 "
                                 "of=/dev/drbd/by-res/OpenNebula-Image-11-vm28-disk0/0 bs=64K count=57396 "
                                 "conv=fsync,sparse"),
                ("deactivate", "node2"),
            ], new_size)

    def test_staging_volume(self):
        calls = []
        existing = ["openNebula-staging-7"]

        def volumes(pool, path):
            return SimpleNamespace(resources=[SimpleNamespace(volumes=[SimpleNamespace(
                storage_pool_name=pool, device_path=path)])])

        class Lin:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def resource_dfn_list_raise(self, query_volume_definitions, filter_by_resource_definitions=None):
                return SimpleNamespace(resource_definitions=[SimpleNamespace(name=x) for x in existing])

            def resource_dfn_delete(self, name):
                calls.append(("delete", name))
                del existing[:]
                return []

            def resource_list_raise(self, filter_by_nodes, filter_by_resources):
                if filter_by_resources == ["OpenNebula-Image-7"]:
                    return volumes("thinpool", "/dev/drbd1000")
                return volumes("thinpool", "/dev/vg/OpenNebula-Staging-7_00000")

            def resource_dfn_create(self, name, layer_list):
                calls.append(("rsc_dfn", name, layer_list))
                return []

            def volume_dfn_create(self, name, size):
                calls.append(("vlm_dfn", name, size))
                return []

            def resource_create(self, rscs):
                calls.append(("rsc", [(x.node_name, x.rsc_name, x.storage_pool, x.layer_list) for x in rscs]))
                return []

        resource = SimpleNamespace(name="OpenNebula-Image-7", _get_connection=Lin)
        with patch.object(extender.util, "log_info"):
            # a stale staging resource of an earlier import is removed first
            path = extender.create_staging_volume(resource, "OpenNebula-Staging-7", "node2", 1048576 * 100 + 1)
            extender.delete_staging_volume(resource, "OpenNebula-Staging-7")

        self.assertEqual(path, "/dev/vg/OpenNebula-Staging-7_00000")
        self.assertEqual(calls, [
            ("delete", "OpenNebula-Staging-7"),
            ("rsc_dfn", "OpenNebula-Staging-7", ["storage"]),
            ("vlm_dfn", "OpenNebula-Staging-7", 102401),
            ("rsc", [("node2", "OpenNebula-Staging-7", "thinpool", ["storage"])]),
        ])

        # stale: the image is gone or ready. Kept: still locked, unknown state, and other resources
        del calls[:]
        existing[:] = ["OpenNebula-Staging-7", "OpenNebula-Staging-8", "OpenNebula-Staging-9", "OpenNebula-Image-7",
                       "OpenNebula-Staging-x"]
        states = {"7": False, "8": True, "9": None}
        with patch.object(extender.util, "log_info"), \
                patch.object(extender.util, "image_is_locked", side_effect=lambda image_id: states[image_id]), \
                patch.object(extender, "delete_staging_volume",
                             side_effect=lambda rsc, name: calls.append(("stale", name))):
            extender.delete_stale_staging_volumes(resource)
        self.assertEqual(calls, [("stale", "OpenNebula-Staging-7")])

    def test_clone_waits_for_source_resource_to_be_uptodate(self):
        events = []

        class Resource:
            name = "OpenNebula-Image-11"
            resource_group_name = "default"
            client = SimpleNamespace(uri_list=["linstor://controller"])

            def clone(self, name, use_zfs_clone=False):
                events.append(("clone", name, use_zfs_clone))
                return SimpleNamespace()

        resource = Resource()
        with patch.object(
            extender,
            "wait_resource_ready",
            side_effect=lambda current: events.append(("wait", current.name)),
        ):
            success, native = extender.clone(
                resource,
                "OpenNebula-Image-11-vm28-disk0",
                resource_group="default",
                allow_dependent_clone=True,
            )

        self.assertTrue(success)
        self.assertTrue(native)
        self.assertEqual(events[0], ("wait", "OpenNebula-Image-11"))
        self.assertEqual(
            events[1],
            ("clone", "OpenNebula-Image-11-vm28-disk0", True),
        )
