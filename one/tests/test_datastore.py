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

from one import datastore

TEST_XML_1 = """
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
      <LINSTOR_STORAGE_POOL>drbdpool</LINSTOR_STORAGE_POOL>
      <LINSTOR_AUTO_PLACE>3</LINSTOR_AUTO_PLACE>
   </TEMPLATE>
</DATASTORE>
"""

TEST_XML_2 = """
<DATASTORE>
   <ID>100</ID>
   <UID>0</UID>
   <GID>0</GID>
   <UNAME>steve</UNAME>
   <GNAME>steve</GNAME>
   <NAME>fantastic-datastore</NAME>
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
   <DS_MAD>linstor</DS_MAD>
   <TM_MAD>shared</TM_MAD>
   <TYPE>3</TYPE>
   <DISK_TYPE>0</DISK_TYPE>
   <CLUSTER_ID>-1</CLUSTER_ID>
   <CLUSTER />
   <TOTAL_MB>555555585</TOTAL_MB>
   <FREE_MB>20000</FREE_MB>
   <USED_MB>5000</USED_MB>
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
"""


class TestDriverAction(unittest.TestCase):
    def test_create_datastore(self):
        test_datastore = datastore.Datastore(TEST_XML_1)

        self.assertEqual(test_datastore.ID, "1")
        self.assertEqual(test_datastore.name, "default")
        self.assertEqual(test_datastore.ds_mad, "fs")
        self.assertEqual(test_datastore.tm_mad, "shared")
        self.assertEqual(test_datastore.total_mb, "86845")
        self.assertEqual(test_datastore.free_mb, "20777")
        self.assertEqual(test_datastore.used_mb, "1000")
        self.assertEqual(test_datastore.storage_pool, "drbdpool")
        self.assertEqual(test_datastore.auto_place, 3)
        self.assertIsNone(test_datastore.deployment_nodes)

        test_datastore = datastore.Datastore(TEST_XML_2)

        self.assertEqual(test_datastore.ID, "100")
        self.assertEqual(test_datastore.name, "fantastic-datastore")
        self.assertEqual(test_datastore.ds_mad, "linstor")
        self.assertEqual(test_datastore.tm_mad, "shared")
        self.assertEqual(test_datastore.total_mb, "555555585")
        self.assertEqual(test_datastore.free_mb, "20000")
        self.assertEqual(test_datastore.used_mb, "5000")
