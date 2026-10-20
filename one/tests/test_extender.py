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
