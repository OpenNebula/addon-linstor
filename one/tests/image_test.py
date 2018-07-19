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
