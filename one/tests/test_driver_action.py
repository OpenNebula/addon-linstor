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


MKFS_XML = """<DS_DRIVER_ACTION_DATA><IMAGE><ID>18</ID><UID>0</UID><GID>0</GID><UNAME>oneadmin</UNAME>
<GNAME>oneadmin</GNAME><NAME>test</NAME><PERMISSIONS><OWNER_U>1</OWNER_U><OWNER_M>1</OWNER_M><OWNER_A>0</OWNER_A>
<GROUP_U>0</GROUP_U><GROUP_M>0</GROUP_M><GROUP_A>0</GROUP_A><OTHER_U>0</OTHER_U><OTHER_M>0</OTHER_M>
<OTHER_A>0</OTHER_A></PERMISSIONS><TYPE>2</TYPE><DISK_TYPE>2</DISK_TYPE><PERSISTENT>0</PERSISTENT>
<REGTIME>1615368111</REGTIME><SOURCE><![CDATA[]]></SOURCE><PATH><![CDATA[]]></PATH><FORMAT><![CDATA[qcow2]]></FORMAT>
<FS><![CDATA[]]></FS><SIZE>2048</SIZE><STATE>4</STATE><PREV_STATE>0</PREV_STATE><RUNNING_VMS>0</RUNNING_VMS>
<CLONING_OPS>0</CLONING_OPS><CLONING_ID>-1</CLONING_ID><TARGET_SNAPSHOT>-1</TARGET_SNAPSHOT>
<DATASTORE_ID>103</DATASTORE_ID><DATASTORE>one_test_autoplace</DATASTORE><VMS></VMS><CLONES></CLONES>
<APP_CLONES></APP_CLONES><TEMPLATE><DEV_PREFIX><![CDATA[vd]]></DEV_PREFIX></TEMPLATE><SNAPSHOTS>
<ALLOW_ORPHANS><![CDATA[NO]]></ALLOW_ORPHANS><CURRENT_BASE><![CDATA[-1]]></CURRENT_BASE>
<NEXT_SNAPSHOT><![CDATA[0]]></NEXT_SNAPSHOT></SNAPSHOTS></IMAGE><DATASTORE><ID>103</ID><UID>0</UID><GID>0</GID>
<UNAME>oneadmin</UNAME><GNAME>oneadmin</GNAME><NAME>one_test_autoplace</NAME><PERMISSIONS><OWNER_U>1</OWNER_U>
<OWNER_M>1</OWNER_M><OWNER_A>0</OWNER_A><GROUP_U>1</GROUP_U><GROUP_M>0</GROUP_M><GROUP_A>0</GROUP_A>
<OTHER_U>0</OTHER_U><OTHER_M>0</OTHER_M><OTHER_A>0</OTHER_A></PERMISSIONS><DS_MAD><![CDATA[linstor]]></DS_MAD>
<TM_MAD><![CDATA[linstor]]></TM_MAD><BASE_PATH><![CDATA[/var/lib/one//datastores/103]]></BASE_PATH><TYPE>0</TYPE>
<DISK_TYPE>2</DISK_TYPE><STATE>0</STATE><CLUSTERS><ID>0</ID></CLUSTERS><TOTAL_MB>15354</TOTAL_MB>
<FREE_MB>12778</FREE_MB><USED_MB>2576</USED_MB><IMAGES></IMAGES><TEMPLATE>
<ALLOW_ORPHANS><![CDATA[yes]]></ALLOW_ORPHANS><BRIDGE_LIST><![CDATA[oneubu6120 oneubu6121 oneubu6122]]></BRIDGE_LIST>
<CLONE_TARGET><![CDATA[SELF]]></CLONE_TARGET><CLONE_TARGET_SHARED><![CDATA[SELF]]></CLONE_TARGET_SHARED>
<CLONE_TARGET_SSH><![CDATA[SELF]]></CLONE_TARGET_SSH><COMPATIBLE_SYS_DS><![CDATA[0,101]]></COMPATIBLE_SYS_DS>
<DISK_TYPE><![CDATA[BLOCK]]></DISK_TYPE><DISK_TYPE_SHARED><![CDATA[BLOCK]]></DISK_TYPE_SHARED>
<DISK_TYPE_SSH><![CDATA[BLOCK]]></DISK_TYPE_SSH><DS_MAD><![CDATA[linstor]]></DS_MAD>
<LINSTOR_AUTO_PLACE><![CDATA[2]]></LINSTOR_AUTO_PLACE><LINSTOR_CLONE_MODE><![CDATA[copy]]></LINSTOR_CLONE_MODE>
<LINSTOR_STORAGE_POOL><![CDATA[dflt]]></LINSTOR_STORAGE_POOL><LN_TARGET><![CDATA[NONE]]></LN_TARGET>
<LN_TARGET_SHARED><![CDATA[NONE]]></LN_TARGET_SHARED><LN_TARGET_SSH><![CDATA[NONE]]></LN_TARGET_SSH>
<RESTRICTED_DIRS><![CDATA[/]]></RESTRICTED_DIRS><SAFE_DIRS><![CDATA[/var/tmp]]></SAFE_DIRS>
<TM_MAD><![CDATA[linstor]]></TM_MAD><TM_MAD_SYSTEM><![CDATA[ssh,shared]]></TM_MAD_SYSTEM>
<TYPE><![CDATA[IMAGE_DS]]></TYPE></TEMPLATE></DATASTORE></DS_DRIVER_ACTION_DATA>"""


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

    def test_mkfs_xml(self):
        da = driver_action.DriverAction(MKFS_XML)

        self.assertEqual(da.image.fs, "")
        self.assertEqual(da.image.format, "qcow2")
