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

STAT_XML = "<DS_DRIVER_ACTION_DATA><IMAGE><PATH>http://centos.osuosl.org/7/isos/x86_64/CentOS-7-x86_64-Minimal-1804.iso</PATH></IMAGE><DATASTORE><ID>106</ID><UID>0</UID><GID>0</GID><UNAME>oneadmin</UNAME><GNAME>oneadmin</GNAME><NAME>linstor</NAME><PERMISSIONS><OWNER_U>1</OWNER_U><OWNER_M>1</OWNER_M><OWNER_A>0</OWNER_A><GROUP_U>1</GROUP_U><GROUP_M>0</GROUP_M><GROUP_A>0</GROUP_A><OTHER_U>0</OTHER_U><OTHER_M>0</OTHER_M><OTHER_A>0</OTHER_A></PERMISSIONS><DS_MAD><![CDATA[linstor]]></DS_MAD><TM_MAD><![CDATA[linstor]]></TM_MAD><BASE_PATH><![CDATA[/var/lib/one//datastores/106]]></BASE_PATH><TYPE>0</TYPE><DISK_TYPE>0</DISK_TYPE><STATE>0</STATE><CLUSTERS><ID>0</ID></CLUSTERS><TOTAL_MB>50000000</TOTAL_MB><FREE_MB>50000000</FREE_MB><USED_MB>0</USED_MB><IMAGES></IMAGES><TEMPLATE><ALLOW_ORPHANS><![CDATA[NO]]></ALLOW_ORPHANS><BRIDGE_LIST><![CDATA[no one cares]]></BRIDGE_LIST><CLONE_TARGET><![CDATA[SELF]]></CLONE_TARGET><DISK_TYPE><![CDATA[FILE]]></DISK_TYPE><DS_MAD><![CDATA[linstor]]></DS_MAD><LINSTOR_AUTO_PLACE><![CDATA[2]]></LINSTOR_AUTO_PLACE><LINSTOR_STORAGE_POOL><![CDATA[thin]]></LINSTOR_STORAGE_POOL><LN_TARGET><![CDATA[NONE]]></LN_TARGET><RESTRICTED_DIRS><![CDATA[/]]></RESTRICTED_DIRS><SAFE_DIRS><![CDATA[/var/tmp]]></SAFE_DIRS><TM_MAD><![CDATA[linstor]]></TM_MAD></TEMPLATE></DATASTORE></DS_DRIVER_ACTION_DATA>"


def test_create_driver_action():
    driver_action_test = driver_action.DriverAction(TEST_XML)

    assert driver_action_test.image.ID == "0"
    assert driver_action_test.image.size == "40"

    assert driver_action_test.datastore.ds_mad == "fs"
    assert driver_action_test.datastore.total_mb == "86845"


def test_stat_xml():
    driver_action_test = driver_action.DriverAction(STAT_XML)

    assert driver_action_test.datastore.ID == "106"
