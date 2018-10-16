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

from one import image

TEXT_XML_1 = """
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
"""

TEXT_XML_2 = """
<IMAGE>
   <ID>5</ID>
   <UID>5</UID>
   <GID>5</GID>
   <UNAME>charles</UNAME>
   <GNAME>public</GNAME>
   <NAME>ttylinux</NAME>
   <PERMISSIONS>
      <OWNER_U>1</OWNER_U>
      <OWNER_M>1</OWNER_M>
      <OWNER_A>0</OWNER_A>
      <GROUP_U>1</GROUP_U>
      <GROUP_M>1</GROUP_M>
      <GROUP_A>0</GROUP_A>
      <OTHER_U>1</OTHER_U>
      <OTHER_M>1</OTHER_M>
      <OTHER_A>0</OTHER_A>
   </PERMISSIONS>
   <TYPE>0</TYPE>
   <DISK_TYPE>0</DISK_TYPE>
   <PERSISTENT>1</PERSISTENT>
   <REGTIME>1385145634</REGTIME>
   <SOURCE />
   <PATH>/tmp/ttylinux.img</PATH>
   <FSTYPE />
   <SIZE>5830</SIZE>
   <STATE>4</STATE>
   <RUNNING_VMS>0</RUNNING_VMS>
   <CLONING_OPS>0</CLONING_OPS>
   <CLONING_ID>-1</CLONING_ID>
   <DATASTORE_ID>100</DATASTORE_ID>
   <DATASTORE>test-datastore</DATASTORE>
   <VMS />
   <CLONES />
   <TEMPLATE>
      <DEV_PREFIX><![CDATA[hd]]></DEV_PREFIX>
      <PUBLIC><![CDATA[YES]]></PUBLIC>
   </TEMPLATE>
</IMAGE>
"""

SNAP_DELETE_XML = """
   <IMAGE>
   <ID>233</ID>
   <UID>0</UID>
   <GID>0</GID>
   <UNAME>oneadmin</UNAME>
   <GNAME>oneadmin</GNAME>
   <NAME>pers</NAME>
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
   <TYPE>2</TYPE>
   <DISK_TYPE>0</DISK_TYPE>
   <PERSISTENT>1</PERSISTENT>
   <REGTIME>1539114838</REGTIME>
   <SOURCE><![CDATA[OpenNebula-Image-233]]></SOURCE>
   <PATH />
   <FSTYPE><![CDATA[raw]]></FSTYPE>
   <SIZE>1024</SIZE>
   <STATE>1</STATE>
   <RUNNING_VMS>0</RUNNING_VMS>
   <CLONING_OPS>0</CLONING_OPS>
   <CLONING_ID>-1</CLONING_ID>
   <TARGET_SNAPSHOT>0</TARGET_SNAPSHOT>
   <DATASTORE_ID>120</DATASTORE_ID>
   <DATASTORE>linstor2</DATASTORE>
   <VMS />
   <CLONES />
   <APP_CLONES />
   <TEMPLATE>
   <DEV_PREFIX><![CDATA[hd]]></DEV_PREFIX>
   <DRIVER><![CDATA[raw]]></DRIVER>
   <ERROR><![CDATA[Tue Oct  9 13:09:22 2018 : Error removing snapshot 1 from image 233]]></ERROR>
   </TEMPLATE>
   <SNAPSHOTS>
   <ALLOW_ORPHANS><![CDATA[YES]]></ALLOW_ORPHANS>
   <NEXT_SNAPSHOT><![CDATA[2]]></NEXT_SNAPSHOT>
   <SNAPSHOT>
   <DATE><![CDATA[1539115005]]></DATE>
   <ID><![CDATA[0]]></ID>
   <NAME><![CDATA[gfdgfd]]></NAME>
   <PARENT><![CDATA[-1]]></PARENT>
   <SIZE><![CDATA[1024]]></SIZE>
   </SNAPSHOT>
   </SNAPSHOTS>
   </IMAGE>
"""


def test_create_image():
    test_image = image.Image(TEXT_XML_1)
    assert test_image.ID == "0"
    assert test_image.size == "40"
    assert test_image.datastore_ID == "1"

    test_image = image.Image(TEXT_XML_2)
    assert test_image.ID == "5"
    assert test_image.size == "5830"
    assert test_image.datastore_ID == "100"


def test_snap_delete():
    test_image = image.Image(SNAP_DELETE_XML)
    assert test_image.source == "OpenNebula-Image-233"
    assert test_image.target_snap == "0"
