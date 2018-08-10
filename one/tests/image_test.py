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


def test_create_image():
    test_vm = image.Image(TEXT_XML_1)
    assert test_vm.ID == "0"
    assert test_vm.size == "40"
    assert test_vm.datastore_ID == "1"

    test_vm = image.Image(TEXT_XML_2)
    assert test_vm.ID == "5"
    assert test_vm.size == "5830"
    assert test_vm.datastore_ID == "100"
