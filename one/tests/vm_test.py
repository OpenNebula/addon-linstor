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


from one import vm

TEXT_XML_1 = """
<VM>
  <ID>0</ID>
  <UID>0</UID>
  <GID>0</GID>
  <UNAME>oneadmin</UNAME>
  <GNAME>oneadmin</GNAME>
  <NAME>test vm instance</NAME>
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
  <LAST_POLL>1533755340</LAST_POLL>
  <STATE>3</STATE>
  <LCM_STATE>18</LCM_STATE>
  <PREV_STATE>3</PREV_STATE>
  <PREV_LCM_STATE>18</PREV_LCM_STATE>
  <RESCHED>0</RESCHED>
  <STIME>1533755190</STIME>
  <ETIME>0</ETIME>
  <DEPLOY_ID>one-0</DEPLOY_ID>
  <MONITORING>
    <CPU><![CDATA[2.01]]></CPU>
    <DISKRDBYTES><![CDATA[512]]></DISKRDBYTES>
    <DISKRDIOPS><![CDATA[1]]></DISKRDIOPS>
    <DISKWRBYTES><![CDATA[0]]></DISKWRBYTES>
    <DISKWRIOPS><![CDATA[0]]></DISKWRIOPS>
    <DISK_SIZE>
      <ID><![CDATA[0]]></ID>
      <SIZE><![CDATA[906]]></SIZE>
    </DISK_SIZE>
    <DISK_SIZE>
      <ID><![CDATA[1]]></ID>
      <SIZE><![CDATA[0]]></SIZE>
    </DISK_SIZE>
    <DISK_SIZE>
      <ID><![CDATA[2]]></ID>
      <SIZE><![CDATA[1]]></SIZE>
    </DISK_SIZE>
    <MEMORY><![CDATA[1153024]]></MEMORY>
    <STATE><![CDATA[a]]></STATE>
  </MONITORING>
  <TEMPLATE>
    <AUTOMATIC_DS_REQUIREMENTS><![CDATA[("CLUSTERS/ID" @> 0)]]></AUTOMATIC_DS_REQUIREMENTS>
    <AUTOMATIC_REQUIREMENTS><![CDATA[(CLUSTER_ID = 0) & !(PUBLIC_CLOUD = YES)]]></AUTOMATIC_REQUIREMENTS>
    <CONTEXT>
      <DISK_ID><![CDATA[2]]></DISK_ID>
      <NETWORK><![CDATA[YES]]></NETWORK>
      <SSH_PUBLIC_KEY><![CDATA[]]></SSH_PUBLIC_KEY>
      <TARGET><![CDATA[hda]]></TARGET>
    </CONTEXT>
    <CPU><![CDATA[1]]></CPU>
    <DISK>
      <ALLOW_ORPHANS><![CDATA[NO]]></ALLOW_ORPHANS>
      <CLONE><![CDATA[NO]]></CLONE>
      <CLONE_TARGET><![CDATA[SYSTEM]]></CLONE_TARGET>
      <CLUSTER_ID><![CDATA[0]]></CLUSTER_ID>
      <DATASTORE><![CDATA[default]]></DATASTORE>
      <DATASTORE_ID><![CDATA[1]]></DATASTORE_ID>
      <DEV_PREFIX><![CDATA[hd]]></DEV_PREFIX>
      <DISK_ID><![CDATA[0]]></DISK_ID>
      <DISK_SNAPSHOT_TOTAL_SIZE><![CDATA[0]]></DISK_SNAPSHOT_TOTAL_SIZE>
      <DISK_TYPE><![CDATA[FILE]]></DISK_TYPE>
      <DRIVER><![CDATA[raw]]></DRIVER>
      <IMAGE><![CDATA[fs iso]]></IMAGE>
      <IMAGE_ID><![CDATA[146]]></IMAGE_ID>
      <IMAGE_STATE><![CDATA[10]]></IMAGE_STATE>
      <IMAGE_UNAME><![CDATA[oneadmin]]></IMAGE_UNAME>
      <LN_TARGET><![CDATA[SYSTEM]]></LN_TARGET>
      <ORDER><![CDATA[2]]></ORDER>
      <ORIGINAL_SIZE><![CDATA[906]]></ORIGINAL_SIZE>
      <PERSISTENT><![CDATA[YES]]></PERSISTENT>
      <READONLY><![CDATA[NO]]></READONLY>
      <SAVE><![CDATA[YES]]></SAVE>
      <SIZE><![CDATA[906]]></SIZE>
      <SOURCE><![CDATA[/var/lib/one//datastores/1/baee88c26cb6055334aaed153a7c8327]]></SOURCE>
      <TARGET><![CDATA[hdb]]></TARGET>
      <TM_MAD><![CDATA[ssh]]></TM_MAD>
      <TYPE><![CDATA[FILE]]></TYPE>
    </DISK>
    <DISK>
      <ALLOW_ORPHANS><![CDATA[NO]]></ALLOW_ORPHANS>
      <CLUSTER_ID><![CDATA[0]]></CLUSTER_ID>
      <DATASTORE><![CDATA[system]]></DATASTORE>
      <DATASTORE_ID><![CDATA[0]]></DATASTORE_ID>
      <DEV_PREFIX><![CDATA[hd]]></DEV_PREFIX>
      <DISK_ID><![CDATA[1]]></DISK_ID>
      <DISK_TYPE><![CDATA[FILE]]></DISK_TYPE>
      <FORMAT><![CDATA[raw]]></FORMAT>
      <ORDER><![CDATA[1]]></ORDER>
      <SIZE><![CDATA[4096]]></SIZE>
      <TARGET><![CDATA[hdc]]></TARGET>
      <TM_MAD><![CDATA[ssh]]></TM_MAD>
      <TYPE><![CDATA[fs]]></TYPE>
    </DISK>
    <DISK>
      <ALLOW_ORPHANS><![CDATA[NO]]></ALLOW_ORPHANS>
      <CLONE><![CDATA[NO]]></CLONE>
      <CLONE_TARGET><![CDATA[SYSTEM]]></CLONE_TARGET>
      <CLUSTER_ID><![CDATA[0]]></CLUSTER_ID>
      <DATASTORE><![CDATA[default]]></DATASTORE>
      <DATASTORE_ID><![CDATA[2]]></DATASTORE_ID>
      <DEV_PREFIX><![CDATA[hd]]></DEV_PREFIX>
      <DISK_ID><![CDATA[2]]></DISK_ID>
      <DISK_SNAPSHOT_TOTAL_SIZE><![CDATA[0]]></DISK_SNAPSHOT_TOTAL_SIZE>
      <DISK_TYPE><![CDATA[FILE]]></DISK_TYPE>
      <DRIVER><![CDATA[raw]]></DRIVER>
      <IMAGE><![CDATA[fs iso]]></IMAGE>
      <IMAGE_ID><![CDATA[149]]></IMAGE_ID>
      <IMAGE_STATE><![CDATA[10]]></IMAGE_STATE>
      <IMAGE_UNAME><![CDATA[oneadmin]]></IMAGE_UNAME>
      <LN_TARGET><![CDATA[SYSTEM]]></LN_TARGET>
      <ORDER><![CDATA[2]]></ORDER>
      <ORIGINAL_SIZE><![CDATA[906]]></ORIGINAL_SIZE>
      <PERSISTENT><![CDATA[NO]]></PERSISTENT>
      <READONLY><![CDATA[NO]]></READONLY>
      <SAVE><![CDATA[YES]]></SAVE>
      <SIZE><![CDATA[906]]></SIZE>
      <SOURCE><![CDATA[/var/lib/one//datastores/1/baee88c26cb6055334aaed153a7c8327]]></SOURCE>
      <TARGET><![CDATA[hdc]]></TARGET>
      <TM_MAD><![CDATA[ssh]]></TM_MAD>
      <TYPE><![CDATA[BLOCK]]></TYPE>
    </DISK>
    <GRAPHICS>
      <LISTEN><![CDATA[0.0.0.0]]></LISTEN>
      <PORT><![CDATA[5900]]></PORT>
      <TYPE><![CDATA[SPICE]]></TYPE>
    </GRAPHICS>
    <MEMORY><![CDATA[1126]]></MEMORY>
    <OS>
      <BOOT><![CDATA[disk1,disk0]]></BOOT>
    </OS>
    <TEMPLATE_ID><![CDATA[0]]></TEMPLATE_ID>
    <VMID><![CDATA[0]]></VMID>
  </TEMPLATE>
  <USER_TEMPLATE>
    <MEMORY_UNIT_COST><![CDATA[MB]]></MEMORY_UNIT_COST>
  </USER_TEMPLATE>
  <HISTORY_RECORDS>
    <HISTORY>
      <OID>0</OID>
      <SEQ>0</SEQ>
      <HOSTNAME>sam.us.linbit</HOSTNAME>
      <HID>1</HID>
      <CID>0</CID>
      <STIME>1533755221</STIME>
      <ETIME>0</ETIME>
      <VM_MAD><![CDATA[kvm]]></VM_MAD>
      <TM_MAD><![CDATA[ssh]]></TM_MAD>
      <DS_ID>0</DS_ID>
      <PSTIME>1533755221</PSTIME>
      <PETIME>1533755246</PETIME>
      <RSTIME>1533755246</RSTIME>
      <RETIME>0</RETIME>
      <ESTIME>0</ESTIME>
      <EETIME>0</EETIME>
      <ACTION>19</ACTION>
      <UID>0</UID>
      <GID>0</GID>
      <REQUEST_ID>6912</REQUEST_ID>
    </HISTORY>
  </HISTORY_RECORDS>
</VM>
"""


def test_create_vm():
    test_vm = vm.Vm(TEXT_XML_1, "0")
    assert test_vm.ID == "0"
    assert test_vm.disk_ID == "0"
    assert test_vm.disk_image_ID == "146"
    assert test_vm.disk_target == "hdb"
    assert test_vm.disk_persistent == "YES"
    assert test_vm.disk_save_as == ""
    assert test_vm.disk_type == "FILE"

    test_vm = vm.Vm(TEXT_XML_1, "2")
    assert test_vm.ID == "0"
    assert test_vm.disk_ID == "2"
    assert test_vm.disk_image_ID == "149"
    assert test_vm.disk_target == "hdc"
    assert test_vm.disk_persistent == "NO"
    assert test_vm.disk_save_as == ""
    assert test_vm.disk_type == "BLOCK"
