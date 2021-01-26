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

from one import driver_action

TEST_XML = """
<DS_DRIVER_ACTION_DATA>
   <IMAGE>
      <ID>0</ID>
      <UID>0</UID>
      <GID>0</GID>
      <UNAME>oneadmin</UNAME>
      <GNAME>oneadmin</GNAME>
      <NAME>ttylinux</NAME>
      <PERMISSIONS>
         <OWNER_U>1</OWNER_U>
         <OWNER_M>1</OWNER_M>
         <OWNER_A>0</OWNER_A>
         <GROUP_U>0</GROUP_U>
         <GROUP_M>0</GROUP_M>
         <GROUP_A>0</GROUP_A>
         <OTHER_U>0</OTHER_U>
         <OTHER_M>0</OTHER_M>
         <OTHER_A>0</OTHER_A>
      </PERMISSIONS>
      <TYPE>0</TYPE>
      <DISK_TYPE>0</DISK_TYPE>
      <PERSISTENT>0</PERSISTENT>
      <REGTIME>1385145541</REGTIME>
      <SOURCE />
      <PATH>/tmp/ttylinux.img</PATH>
      <FSTYPE />
      <SIZE>40</SIZE>
      <STATE>4</STATE>
      <RUNNING_VMS>0</RUNNING_VMS>
      <CLONING_OPS>0</CLONING_OPS>
      <CLONING_ID>-1</CLONING_ID>
      <DATASTORE_ID>1</DATASTORE_ID>
      <DATASTORE>default</DATASTORE>
      <VMS />
      <CLONES />
      <TEMPLATE>
         <DEV_PREFIX><![CDATA[hd]]></DEV_PREFIX>
         <PUBLIC><![CDATA[YES]]></PUBLIC>
      </TEMPLATE>
   </IMAGE>
   <DATASTORE>
      <ID>1</ID>
      <UID>0</UID>
      <GID>0</GID>
      <UNAME>oneadmin</UNAME>
      <GNAME>oneadmin</GNAME>
      <NAME>default</NAME>
      <PERMISSIONS>
         <OWNER_U>1</OWNER_U>
         <OWNER_M>1</OWNER_M>
         <OWNER_A>0</OWNER_A>
         <GROUP_U>1</GROUP_U>
         <GROUP_M>0</GROUP_M>
         <GROUP_A>0</GROUP_A>
         <OTHER_U>1</OTHER_U>
         <OTHER_M>0</OTHER_M>
         <OTHER_A>0</OTHER_A>
      </PERMISSIONS>
      <DS_MAD>fs</DS_MAD>
      <TM_MAD>shared</TM_MAD>
      <TYPE>0</TYPE>
      <DISK_TYPE>0</DISK_TYPE>
      <CLUSTER_ID>-1</CLUSTER_ID>
      <CLUSTER />
      <TOTAL_MB>86845</TOTAL_MB>
      <FREE_MB>20777</FREE_MB>
      <USED_MB>1000</USED_MB>
      <IMAGES />
      <TEMPLATE>
         <CLONE_TARGET><![CDATA[SYSTEM]]></CLONE_TARGET>
         <DISK_TYPE><![CDATA[FILE]]></DISK_TYPE>
         <DS_MAD><![CDATA[fs]]></DS_MAD>
         <LN_TARGET><![CDATA[NONE]]></LN_TARGET>
         <TM_MAD><![CDATA[shared]]></TM_MAD>
         <TYPE><![CDATA[IMAGE_DS]]></TYPE>
      </TEMPLATE>
   </DATASTORE>
</DS_DRIVER_ACTION_DATA>
"""

STAT_XML = """<DS_DRIVER_ACTION_DATA><IMAGE>
<PATH>http://centos.osuosl.org/7/isos/x86_64/CentOS-7-x86_64-Minimal-1804.iso"</PATH>
</IMAGE><DATASTORE><ID>106</ID><UID>0</UID><GID>0</GID><UNAME>oneadmin</UNAME><GNAME>oneadmin</GNAME>
<NAME>linstor</NAME><PERMISSIONS><OWNER_U>1</OWNER_U><OWNER_M>1</OWNER_M><OWNER_A>0</OWNER_A><GROUP_U>1</GROUP_U>
<GROUP_M>0</GROUP_M><GROUP_A>0</GROUP_A><OTHER_U>0</OTHER_U><OTHER_M>0</OTHER_M><OTHER_A>0</OTHER_A></PERMISSIONS>
<DS_MAD><![CDATA[linstor]]></DS_MAD><TM_MAD><![CDATA[linstor]]></TM_MAD><BASE_PATH>
<![CDATA[/var/lib/one//datastores/106]]></BASE_PATH><TYPE>0</TYPE><DISK_TYPE>0</DISK_TYPE><STATE>0</STATE>
<CLUSTERS><ID>0</ID></CLUSTERS><TOTAL_MB>50000000</TOTAL_MB><FREE_MB>50000000</FREE_MB><USED_MB>0</USED_MB>
<IMAGES></IMAGES><TEMPLATE><ALLOW_ORPHANS><![CDATA[NO]]></ALLOW_ORPHANS><BRIDGE_LIST><![CDATA[no one cares]]>
</BRIDGE_LIST><CLONE_TARGET><![CDATA[SELF]]></CLONE_TARGET><DISK_TYPE><![CDATA[FILE]]></DISK_TYPE><DS_MAD>
<![CDATA[linstor]]></DS_MAD><LINSTOR_AUTO_PLACE><![CDATA[2]]></LINSTOR_AUTO_PLACE><LINSTOR_STORAGE_POOL>
<![CDATA[thin]]></LINSTOR_STORAGE_POOL><LN_TARGET><![CDATA[NONE]]></LN_TARGET><RESTRICTED_DIRS><![CDATA[/]]>
</RESTRICTED_DIRS><SAFE_DIRS><![CDATA[/var/tmp]]></SAFE_DIRS><TM_MAD><![CDATA[linstor]]></TM_MAD></TEMPLATE>
</DATASTORE></DS_DRIVER_ACTION_DATA>"""


MONITOR_XML = """
<DS_DRIVER_ACTION_DATA>
   <DATASTORE>
      <ID>117</ID>
      <UID>0</UID>
      <GID>0</GID>
      <UNAME>oneadmin</UNAME>
      <GNAME>oneadmin</GNAME>
      <NAME>linstor2</NAME>
      <PERMISSIONS>
         <OWNER_U>1</OWNER_U>
         <OWNER_M>1</OWNER_M>
         <OWNER_A>0</OWNER_A>
         <GROUP_U>1</GROUP_U>
         <GROUP_M>0</GROUP_M>
         <GROUP_A>0</GROUP_A>
         <OTHER_U>0</OTHER_U>
         <OTHER_M>0</OTHER_M>
         <OTHER_A>0</OTHER_A>
      </PERMISSIONS>
      <DS_MAD><![CDATA[linstor]]></DS_MAD>
      <TM_MAD><![CDATA[linstor]]></TM_MAD>
      <BASE_PATH><![CDATA[/var/lib/one//datastores/117]]></BASE_PATH>
      <TYPE>0</TYPE>
      <DISK_TYPE>0</DISK_TYPE>
      <STATE>0</STATE>
      <CLUSTERS>
         <ID>0</ID>
      </CLUSTERS>
      <TOTAL_MB>0</TOTAL_MB>
      <FREE_MB>0</FREE_MB>
      <USED_MB>0</USED_MB>
      <IMAGES />
      <TEMPLATE>
         <ALLOW_ORPHANS><![CDATA[NO]]></ALLOW_ORPHANS>
         <BRIDGE_LIST><![CDATA[no one cares]]></BRIDGE_LIST>
         <CLONE_TARGET><![CDATA[SELF]]></CLONE_TARGET>
         <DISK_TYPE><![CDATA[FILE]]></DISK_TYPE>
         <DS_MAD><![CDATA[linstor]]></DS_MAD>
         <LINSTOR_AUTO_PLACE><![CDATA[2]]></LINSTOR_AUTO_PLACE>
         <LINSTOR_STORAGE_POOL><![CDATA[thin]]></LINSTOR_STORAGE_POOL>
         <LN_TARGET><![CDATA[NONE]]></LN_TARGET>
         <RESTRICTED_DIRS><![CDATA[/]]></RESTRICTED_DIRS>
         <SAFE_DIRS><![CDATA[/var/tmp]]></SAFE_DIRS>
         <TM_MAD><![CDATA[linstor]]></TM_MAD>
      </TEMPLATE>
   </DATASTORE>
</DS_DRIVER_ACTION_DATA>
"""


class TestDriverAction(unittest.TestCase):
    def test_create_driver_action(self):
        driver_action_test = driver_action.DriverAction(TEST_XML)

        self.assertEqual(driver_action_test.image.id, "0")
        self.assertEqual(driver_action_test.image.size, "40")

        self.assertEqual(driver_action_test.datastore.ds_mad, "fs")
        self.assertEqual(driver_action_test.datastore.total_mb, "86845")

    def test_stat_xml(self):
        driver_action_test = driver_action.DriverAction(STAT_XML)

        self.assertEqual(driver_action_test.datastore.id, "106")

    def test_monitor_xml(self):
        driver_action_test = driver_action.DriverAction(MONITOR_XML)

        self.assertEqual(driver_action_test.datastore.id, "117")
        self.assertEqual(driver_action_test.datastore.storage_pool, "thin")
