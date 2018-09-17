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


import json

import pytest

from linstor_helper import resource

NODE_DATA_0 = """
[
  {
    "resource_states": [
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "bill",
        "node_name": "boudicca"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "bill2000",
        "node_name": "boudicca"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "bill",
        "node_name": "charlemagne"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "bill2000",
        "node_name": "charlemagne"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "bill",
        "node_name": "attila"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "bill2000",
        "node_name": "attila"
      }
    ],
    "resources": [
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1000",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1000,
            "backing_disk": "/dev/drbdpool/bill_00000",
            "vlm_uuid": "c3887fc4-d208-4d33-b021-8d92d50dece2",
            "vlm_dfn_uuid": "dbb7c487-cc96-4fb0-ab55-91b32346322a"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "17d39ccc-3995-4345-a52e-9f209cdde2dd",
        "node_name": "attila",
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "9c298a4b-a2ae-4855-a931-08fa4826f3ed",
        "name": "bill"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1000",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1000,
            "backing_disk": "/dev/drbdpool/bill_00000",
            "vlm_uuid": "f58c12f4-79d2-4b10-9818-1716c178cb51",
            "vlm_dfn_uuid": "dbb7c487-cc96-4fb0-ab55-91b32346322a"
          }
        ],
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "uuid": "c56356e4-f35f-4706-933b-cba9cf8baf5e",
        "node_name": "boudicca",
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "9c298a4b-a2ae-4855-a931-08fa4826f3ed",
        "name": "bill"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1000",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "254472cf-fad9-4d0b-a57b-f783c40ac179",
            "vlm_minor_nr": 1000,
            "backing_disk": "/dev/drbdpool/bill_00000",
            "vlm_uuid": "eaa32672-18ee-4737-8e6b-7d3c55744f8b",
            "vlm_dfn_uuid": "dbb7c487-cc96-4fb0-ab55-91b32346322a"
          }
        ],
        "node_uuid": "172da4c8-250a-468f-bc0c-f4a4fd5d8d04",
        "uuid": "f6c4b45c-6e5f-41f2-ae1a-843305b52ee9",
        "node_name": "charlemagne",
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "9c298a4b-a2ae-4855-a931-08fa4826f3ed",
        "name": "bill"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1003,
            "backing_disk": "/dev/drbdpool/bill2000_00000",
            "vlm_uuid": "c5bd9741-2e57-49c5-9d74-536f1072002d",
            "vlm_props": [
              {
                "value": "bill",
                "key": "RestoreFromResource"
              },
              {
                "value": "bill-snap",
                "key": "RestoreFromSnapshot"
              },
              {
                "value": "thin",
                "key": "StorPoolName"
              }
            ],
            "vlm_dfn_uuid": "8bc9bba2-10c5-4a25-9dd1-07c977f089ce"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "3f81d6d6-8bda-40a6-b43f-8a7d8c0d63ef",
        "node_name": "attila",
        "props": [
          {
            "value": "7",
            "key": "PeerSlots"
          }
        ],
        "rsc_dfn_uuid": "41eb00e5-bff7-4c14-8dbb-76d28fd815ee",
        "name": "bill2000"
      },
      {
        "rsc_flags": [
            "DISKLESS"
        ],
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1003,
            "backing_disk": "/dev/drbdpool/bill2000_00000",
            "vlm_uuid": "ce628247-3a1f-4596-8dde-d8407399329a",
            "vlm_props": [
              {
                "value": "bill",
                "key": "RestoreFromResource"
              },
              {
                "value": "bill-snap",
                "key": "RestoreFromSnapshot"
              },
              {
                "value": "thin",
                "key": "StorPoolName"
              }
            ],
            "vlm_dfn_uuid": "8bc9bba2-10c5-4a25-9dd1-07c977f089ce"
          }
        ],
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "uuid": "a885348a-d57d-4fef-b15c-91867308ef62",
        "node_name": "boudicca",
        "props": [
          {
            "value": "7",
            "key": "PeerSlots"
          }
        ],
        "rsc_dfn_uuid": "41eb00e5-bff7-4c14-8dbb-76d28fd815ee",
        "name": "bill2000"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1009",
            "vlm_nr": 1,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "254472cf-fad9-4d0b-a57b-f783c40ac179",
            "vlm_minor_nr": 1009,
            "backing_disk": "/dev/drbdpool/bill2000_00009",
            "vlm_uuid": "babd12e8-a6c7-438e-b5e0-3d460c34d86d",
            "vlm_props": [
              {
                "value": "bill",
                "key": "RestoreFromResource"
              },
              {
                "value": "bill-snap",
                "key": "RestoreFromSnapshot"
              },
              {
                "value": "thin",
                "key": "StorPoolName"
              }
            ],
            "vlm_dfn_uuid": "8bc9bba2-10c5-4a25-9dd1-07c977f089ce"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "254472cf-fad9-4d0b-a57b-f783c40ac179",
            "vlm_minor_nr": 1003,
            "backing_disk": "/dev/drbdpool/bill2000_00000",
            "vlm_uuid": "babd12e8-a6c7-438e-b5e0-3d460c34d86d",
            "vlm_props": [
              {
                "value": "bill",
                "key": "RestoreFromResource"
              },
              {
                "value": "bill-snap",
                "key": "RestoreFromSnapshot"
              },
              {
                "value": "thin",
                "key": "StorPoolName"
              }
            ],
            "vlm_dfn_uuid": "8bc9bba2-10c5-4a25-9dd1-07c977f089ce"
          }
        ],
        "node_uuid": "172da4c8-250a-468f-bc0c-f4a4fd5d8d04",
        "uuid": "8eaad34b-eea5-4988-8193-71282109173c",
        "node_name": "charlemagne",
        "props": [
          {
            "value": "7",
            "key": "PeerSlots"
          }
        ],
        "rsc_dfn_uuid": "41eb00e5-bff7-4c14-8dbb-76d28fd815ee",
        "name": "bill2000"
      }
    ]
  }
]
"""

INTERFACE_DATA = """
[
  {
    "nodes": [
      {
        "connection_status": 2,
        "uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "net_interfaces": [
          {
            "address": "192.168.6.193",
            "uuid": "bb679899-01fc-4ba6-8485-05e0426074b7",
            "name": "default"
          }
        ],
        "props": [
          {
            "value": "default",
            "key": "CurStltConnName"
          }
        ],
        "type": "SATELLITE",
        "name": "attila"
      },
      {
        "connection_status": 2,
        "uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "net_interfaces": [
          {
            "address": "192.168.6.192",
            "uuid": "b34eff00-3eb0-49cf-b6a2-ebf4056e20fb",
            "name": "default"
          }
        ],
        "props": [
          {
            "value": "default",
            "key": "CurStltConnName"
          }
        ],
        "type": "SATELLITE",
        "name": "boudicca"
      },
      {
        "connection_status": 2,
        "uuid": "172da4c8-250a-468f-bc0c-f4a4fd5d8d04",
        "net_interfaces": [
          {
            "address": "192.168.6.191",
            "uuid": "d94c7bfe-9117-4bcd-831e-745ca78ca5ec",
            "name": "default"
          }
        ],
        "props": [
          {
            "value": "default",
            "key": "CurStltConnName"
          }
        ],
        "type": "SATELLITE",
        "name": "charlemagne"
      },
      {
        "connection_status": 0,
        "uuid": "c78d312b-77a1-44f2-802f-ca0dac78e0ba",
        "net_interfaces": [
          {
            "address": "192.168.6.190",
            "uuid": "8e9e4cdd-9241-4b4d-ba12-ea6100dbc33b",
            "name": "default"
          }
        ],
        "props": [
          {
            "value": "default",
            "key": "CurStltConnName"
          }
        ],
        "type": "CONTROLLER",
        "name": "vercingetorix"
      }
    ]
  }
]
"""

NODE_DATA_1 = """
[
  {
    "resource_states": [
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-199",
        "node_name": "boudicca"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-198",
        "node_name": "boudicca"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-196",
        "node_name": "boudicca"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-207",
        "node_name": "boudicca"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-195",
        "node_name": "boudicca"
      },
      {
        "vlm_states": [
          {
            "disk_state": "Diskless",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-199",
        "node_name": "sam"
      },
      {
        "vlm_states": [
          {
            "disk_state": "Diskless",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-210-vm58-disk1",
        "node_name": "sam"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-210",
        "node_name": "charlemagne"
      },
      {
        "vlm_states": [
          {
            "disk_state": "Diskless",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-210-vm58-disk1",
        "node_name": "charlemagne"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-210",
        "node_name": "attila"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-199",
        "node_name": "attila"
      },
      {
        "vlm_states": [
          {
            "disk_state": "Diskless",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-210-vm58-disk1",
        "node_name": "attila"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-198",
        "node_name": "attila"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-196",
        "node_name": "attila"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-207",
        "node_name": "attila"
      },
      {
        "vlm_states": [
          {
            "disk_state": "UpToDate",
            "vlm_nr": 0
          }
        ],
        "in_use": false,
        "rsc_name": "OpenNebula-Image-195",
        "node_name": "attila"
      }
    ],
    "resources": [
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1005",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1005,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-195_00000",
            "vlm_uuid": "5d6c0701-c251-409a-bf73-bac41155cd5d",
            "vlm_dfn_uuid": "04aa8545-ab4a-4a2c-ab50-cc99514a78de"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "9f9af81a-e4c5-4c02-a14d-cda6842c23f4",
        "node_name": "attila",
        "node_id": 0,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "927a0e4e-c9b1-41b6-a98c-6b159869171c",
        "name": "OpenNebula-Image-195"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1005",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1005,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-195_00000",
            "vlm_uuid": "66148af8-f6a4-4572-9ed2-f27e87e41f34",
            "vlm_dfn_uuid": "04aa8545-ab4a-4a2c-ab50-cc99514a78de"
          }
        ],
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "uuid": "eb34e076-ab64-4074-81e8-7df468230e1c",
        "node_name": "boudicca",
        "node_id": 1,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "927a0e4e-c9b1-41b6-a98c-6b159869171c",
        "name": "OpenNebula-Image-195"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1006",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1006,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-196_00000",
            "vlm_uuid": "6cd16507-62bc-4d18-b6f2-3e7cf25fab8e",
            "vlm_dfn_uuid": "f016717e-834a-43b1-af47-a8fa30fed65e"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "80ba4ebe-90c9-4f47-8ae6-6dd16841418c",
        "node_name": "attila",
        "node_id": 0,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "b9fc71ae-94f4-4034-9a35-0fc288a0b253",
        "name": "OpenNebula-Image-196"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1006",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1006,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-196_00000",
            "vlm_uuid": "3e9e3582-71c9-4813-b322-8ab005bda28b",
            "vlm_dfn_uuid": "f016717e-834a-43b1-af47-a8fa30fed65e"
          }
        ],
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "uuid": "c7f6c359-c363-4334-b1eb-dffd5a093e3d",
        "node_name": "boudicca",
        "node_id": 1,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "b9fc71ae-94f4-4034-9a35-0fc288a0b253",
        "name": "OpenNebula-Image-196"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1000",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1000,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-198_00000",
            "vlm_uuid": "a11c654d-519f-48a2-947f-5e200088b53b",
            "vlm_dfn_uuid": "f3bc0824-0eda-47f3-8068-7c33f3472d22"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "d4a0d5b0-9baf-4909-b533-da48a3697d76",
        "node_name": "attila",
        "node_id": 0,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "32a7fc07-922e-48c5-8cf5-8e1723e5dd11",
        "name": "OpenNebula-Image-198"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1000",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1000,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-198_00000",
            "vlm_uuid": "c61c6832-aba3-46c9-b01f-4952380a955f",
            "vlm_dfn_uuid": "f3bc0824-0eda-47f3-8068-7c33f3472d22"
          }
        ],
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "uuid": "91fe9f1e-a2a7-465f-b172-009879e56acf",
        "node_name": "boudicca",
        "node_id": 1,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "32a7fc07-922e-48c5-8cf5-8e1723e5dd11",
        "name": "OpenNebula-Image-198"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1003,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-199_00000",
            "vlm_uuid": "0df0d836-da0d-409d-81e5-8ad9e015b9c9",
            "vlm_dfn_uuid": "7fff48f4-1781-4bb1-8614-fd845a4a592d"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "13bcaec3-dce4-492e-ae2d-83612b717ed7",
        "node_name": "attila",
        "node_id": 0,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "5d2f1960-b96a-4451-9a3d-d70f2f315667",
        "name": "OpenNebula-Image-199"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1003,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-199_00000",
            "vlm_uuid": "c29bbba5-5ab9-4a55-92ef-7403e4a4adee",
            "vlm_dfn_uuid": "7fff48f4-1781-4bb1-8614-fd845a4a592d"
          }
        ],
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "uuid": "17ea9287-ac24-4659-a63c-a8447af01083",
        "node_name": "boudicca",
        "node_id": 1,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "5d2f1960-b96a-4451-9a3d-d70f2f315667",
        "name": "OpenNebula-Image-199"
      },
      {
        "rsc_flags": [
          "DISKLESS"
        ],
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "DfltDisklessStorPool",
            "stor_pool_uuid": "01f14bb8-561c-452a-b100-fcb60f617381",
            "vlm_minor_nr": 1003,
            "backing_disk": "none",
            "vlm_uuid": "45f0b05d-4b25-4240-a047-4c2919ba97cb",
            "vlm_dfn_uuid": "7fff48f4-1781-4bb1-8614-fd845a4a592d"
          }
        ],
        "node_uuid": "7594b663-08c2-4543-9a92-8679cfcade24",
        "uuid": "ae0b2efb-9770-4ae7-bb24-2d4da0898a52",
        "node_name": "sam",
        "node_id": 2,
        "props": [
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "DfltDisklessStorPool",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "5d2f1960-b96a-4451-9a3d-d70f2f315667",
        "name": "OpenNebula-Image-199"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1001",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1001,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-207_00000",
            "vlm_uuid": "5a36de3e-fca2-4593-b706-cdc7a170ed2a",
            "vlm_dfn_uuid": "cb6c1a1e-81f0-4f4e-8d1d-dbfd553e6ef2"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "f95244da-39ff-4daa-9259-f0d03912c36e",
        "node_name": "attila",
        "node_id": 0,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "90925993-54d8-458b-a028-ab66893a5f91",
        "name": "OpenNebula-Image-207"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1001",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1001,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-207_00000",
            "vlm_uuid": "05f00795-05c0-4521-b712-e04a1412d09d",
            "vlm_dfn_uuid": "cb6c1a1e-81f0-4f4e-8d1d-dbfd553e6ef2"
          }
        ],
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "uuid": "4e41f53e-030e-4a88-84fe-fbfedf002568",
        "node_name": "boudicca",
        "node_id": 1,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "90925993-54d8-458b-a028-ab66893a5f91",
        "name": "OpenNebula-Image-207"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1002",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1002,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-210_00000",
            "vlm_uuid": "3533f761-fb68-46ec-9b4b-2d60b3125369",
            "vlm_dfn_uuid": "adbde4ef-004f-411b-b083-a44dfd627246"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "be31a71f-09d6-4789-9190-b692ea0688a5",
        "node_name": "attila",
        "node_id": 1,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "7bda375f-adf5-4fe1-bf3f-56f16eda3cc1",
        "name": "OpenNebula-Image-210"
      },
      {
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1002",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "254472cf-fad9-4d0b-a57b-f783c40ac179",
            "vlm_minor_nr": 1002,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-210_00000",
            "vlm_uuid": "a9242b62-aff8-4d68-866a-835ea0fd2254",
            "vlm_dfn_uuid": "adbde4ef-004f-411b-b083-a44dfd627246"
          }
        ],
        "node_uuid": "172da4c8-250a-468f-bc0c-f4a4fd5d8d04",
        "uuid": "0a87601b-6ec7-498b-881b-90131645613e",
        "node_name": "charlemagne",
        "node_id": 0,
        "props": [
          {
            "value": "thin",
            "key": "AutoSelectedStorPoolName"
          },
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "thin",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "7bda375f-adf5-4fe1-bf3f-56f16eda3cc1",
        "name": "OpenNebula-Image-210"
      },
      {
        "vlms": [
          {
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1004,
            "vlm_uuid": "5cb2486c-c6a5-4c45-bb0f-890dd6e42c05",
            "vlm_props": [
              {
                "value": "OpenNebula-Image-210",
                "key": "RestoreFromResource"
              },
              {
                "value": "OpenNebula-Image-210-snap",
                "key": "RestoreFromSnapshot"
              }
            ],
            "vlm_dfn_uuid": "59adbda5-19db-48d5-a702-173fb61b0634"
          }
        ],
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "uuid": "f2266b22-6e4c-4f75-bd6f-af6e7b5a87ab",
        "node_name": "attila",
        "node_id": 0,
        "props": [
          {
            "value": "7",
            "key": "PeerSlots"
          }
        ],
        "rsc_dfn_uuid": "5c3eeb9f-89e3-4938-a269-3d3a944bdba9",
        "name": "OpenNebula-Image-210-vm58-disk1"
      },
      {
        "vlms": [
          {
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "254472cf-fad9-4d0b-a57b-f783c40ac179",
            "vlm_minor_nr": 1004,
            "vlm_uuid": "336adbc0-98f9-422c-939a-6472bd11a8c4",
            "vlm_props": [
              {
                "value": "OpenNebula-Image-210",
                "key": "RestoreFromResource"
              },
              {
                "value": "OpenNebula-Image-210-snap",
                "key": "RestoreFromSnapshot"
              }
            ],
            "vlm_dfn_uuid": "59adbda5-19db-48d5-a702-173fb61b0634"
          }
        ],
        "node_uuid": "172da4c8-250a-468f-bc0c-f4a4fd5d8d04",
        "uuid": "73016558-f2e9-4401-832a-d33b614470e7",
        "node_name": "charlemagne",
        "node_id": 1,
        "props": [
          {
            "value": "7",
            "key": "PeerSlots"
          }
        ],
        "rsc_dfn_uuid": "5c3eeb9f-89e3-4938-a269-3d3a944bdba9",
        "name": "OpenNebula-Image-210-vm58-disk1"
      },
      {
        "rsc_flags": [
          "DISKLESS"
        ],
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1004",
            "vlm_nr": 0,
            "stor_pool_name": "DfltDisklessStorPool",
            "stor_pool_uuid": "01f14bb8-561c-452a-b100-fcb60f617381",
            "vlm_minor_nr": 1004,
            "backing_disk": "none",
            "vlm_uuid": "fd722acf-4c50-470b-90fd-08c1c5d7f7e6",
            "vlm_dfn_uuid": "59adbda5-19db-48d5-a702-173fb61b0634"
          }
        ],
        "node_uuid": "7594b663-08c2-4543-9a92-8679cfcade24",
        "uuid": "44ae4561-bbc3-4711-91f4-c7935d92d0c2",
        "node_name": "sam",
        "node_id": 2,
        "props": [
          {
            "value": "7",
            "key": "PeerSlots"
          },
          {
            "value": "DfltDisklessStorPool",
            "key": "StorPoolName"
          }
        ],
        "rsc_dfn_uuid": "5c3eeb9f-89e3-4938-a269-3d3a944bdba9",
        "name": "OpenNebula-Image-210-vm58-disk1"
      }
    ]
  }
]
"""

STORAGE_POOL_DATA_0 = """
[
  {
    "stor_pools": [
      {
        "stor_pool_dfn_uuid": "3d6d66f2-d966-4aad-bdab-740db8341c4a",
        "node_uuid": "9198fcab-2ed6-4039-8385-2e25cfd2aa35",
        "stor_pool_name": "thin",
        "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
        "static_traits": [
          {
            "value": "Thin",
            "key": "Provisioning"
          },
          {
            "value": "true",
            "key": "SupportsSnapshots"
          }
        ],
        "driver": "LvmThinDriver",
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1005",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1005,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-195_00000",
            "vlm_uuid": "5d6c0701-c251-409a-bf73-bac41155cd5d",
            "vlm_dfn_uuid": "04aa8545-ab4a-4a2c-ab50-cc99514a78de"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1006",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1006,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-196_00000",
            "vlm_uuid": "6cd16507-62bc-4d18-b6f2-3e7cf25fab8e",
            "vlm_dfn_uuid": "f016717e-834a-43b1-af47-a8fa30fed65e"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1000",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1000,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-198_00000",
            "vlm_uuid": "a11c654d-519f-48a2-947f-5e200088b53b",
            "vlm_dfn_uuid": "f3bc0824-0eda-47f3-8068-7c33f3472d22"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1003,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-199_00000",
            "vlm_uuid": "0df0d836-da0d-409d-81e5-8ad9e015b9c9",
            "vlm_dfn_uuid": "7fff48f4-1781-4bb1-8614-fd845a4a592d"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1001",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1001,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-207_00000",
            "vlm_uuid": "5a36de3e-fca2-4593-b706-cdc7a170ed2a",
            "vlm_dfn_uuid": "cb6c1a1e-81f0-4f4e-8d1d-dbfd553e6ef2"
          },
          {
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
            "vlm_minor_nr": 1002,
            "vlm_uuid": "983319ba-b7db-4c65-862f-81cfe63190bd",
            "vlm_props": [
              {
                "value": "OpenNebula-Image-207",
                "key": "RestoreFromResource"
              },
              {
                "value": "OpenNebula-Image-207-snap",
                "key": "RestoreFromSnapshot"
              }
            ],
            "vlm_dfn_uuid": "c66147da-ca2e-4ce2-a0ae-5bdd6d044196"
          }
        ],
        "node_name": "attila",
        "props": [
          {
            "value": "drbdpool",
            "key": "StorDriver/LvmVg"
          },
          {
            "value": "drbdthinpool",
            "key": "StorDriver/ThinPool"
          }
        ],
        "free_space": {
          "free_capacity": 11330625,
          "stor_pool_uuid": "193bd06a-1267-4478-ac23-85f75290f14b",
          "stor_pool_name": "thin",
          "total_capacity": 14663680
        }
      },
      {
        "stor_pool_dfn_uuid": "3d6d66f2-d966-4aad-bdab-740db8341c4a",
        "node_uuid": "10f01093-2516-4d30-bc8d-a7b1ab5e72b2",
        "stor_pool_name": "thin",
        "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
        "static_traits": [
          {
            "value": "Thin",
            "key": "Provisioning"
          },
          {
            "value": "true",
            "key": "SupportsSnapshots"
          }
        ],
        "driver": "LvmThinDriver",
        "vlms": [
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1005",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1005,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-195_00000",
            "vlm_uuid": "66148af8-f6a4-4572-9ed2-f27e87e41f34",
            "vlm_dfn_uuid": "04aa8545-ab4a-4a2c-ab50-cc99514a78de"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1006",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1006,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-196_00000",
            "vlm_uuid": "3e9e3582-71c9-4813-b322-8ab005bda28b",
            "vlm_dfn_uuid": "f016717e-834a-43b1-af47-a8fa30fed65e"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1000",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1000,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-198_00000",
            "vlm_uuid": "c61c6832-aba3-46c9-b01f-4952380a955f",
            "vlm_dfn_uuid": "f3bc0824-0eda-47f3-8068-7c33f3472d22"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1003",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1003,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-199_00000",
            "vlm_uuid": "c29bbba5-5ab9-4a55-92ef-7403e4a4adee",
            "vlm_dfn_uuid": "7fff48f4-1781-4bb1-8614-fd845a4a592d"
          },
          {
            "meta_disk": "internal",
            "device_path": "/dev/drbd1001",
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1001,
            "backing_disk": "/dev/drbdpool/OpenNebula-Image-207_00000",
            "vlm_uuid": "05f00795-05c0-4521-b712-e04a1412d09d",
            "vlm_dfn_uuid": "cb6c1a1e-81f0-4f4e-8d1d-dbfd553e6ef2"
          },
          {
            "vlm_nr": 0,
            "stor_pool_name": "thin",
            "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
            "vlm_minor_nr": 1002,
            "vlm_uuid": "92d50f0a-0cb5-4e41-af4e-253584db207f",
            "vlm_props": [
              {
                "value": "OpenNebula-Image-207",
                "key": "RestoreFromResource"
              },
              {
                "value": "OpenNebula-Image-207-snap",
                "key": "RestoreFromSnapshot"
              }
            ],
            "vlm_dfn_uuid": "c66147da-ca2e-4ce2-a0ae-5bdd6d044196"
          }
        ],
        "node_name": "boudicca",
        "props": [
          {
            "value": "drbdpool",
            "key": "StorDriver/LvmVg"
          },
          {
            "value": "drbdthinpool",
            "key": "StorDriver/ThinPool"
          }
        ],
        "free_space": {
          "free_capacity": 11315961,
          "stor_pool_uuid": "921af4e0-ff6d-43d6-b56a-a3f8cd45678f",
          "stor_pool_name": "thin",
          "total_capacity": 14663680
        }
      },
      {
        "stor_pool_dfn_uuid": "3d6d66f2-d966-4aad-bdab-740db8341c4a",
        "node_uuid": "172da4c8-250a-468f-bc0c-f4a4fd5d8d04",
        "stor_pool_name": "thin",
        "stor_pool_uuid": "254472cf-fad9-4d0b-a57b-f783c40ac179",
        "static_traits": [
          {
            "value": "Thin",
            "key": "Provisioning"
          },
          {
            "value": "true",
            "key": "SupportsSnapshots"
          }
        ],
        "driver": "LvmThinDriver",
        "node_name": "charlemagne",
        "props": [
          {
            "value": "drbdpool",
            "key": "StorDriver/LvmVg"
          },
          {
            "value": "drbdthinpool",
            "key": "StorDriver/ThinPool"
          }
        ],
        "free_space": {
          "free_capacity": 14663680,
          "stor_pool_uuid": "254472cf-fad9-4d0b-a57b-f783c40ac179",
          "stor_pool_name": "thin",
          "total_capacity": 14663680
        }
      }
    ]
  }
]
"""


def test_path():
    res = resource.Resource(name="bill")
    res.path = NODE_DATA_0
    assert res._path == "/dev/drbd1000"

    res = resource.Resource(name="bill2000")
    res.path = NODE_DATA_0
    assert res._path == "/dev/drbd1003"

    res = resource.Resource(name="OpenNebula-Image-210-vm58-disk1")
    with pytest.raises(KeyError) as e_info:
        res.path = NODE_DATA_1


def test_deployment_nodes():
    res = resource.Resource(name="bill")
    assert set(res._deployed_nodes(json.loads(NODE_DATA_0)[0]["resources"])) == set(
        ["charlemagne", "boudicca", "attila"]
    )


def test_get_node_interface():
    res = resource.Resource(name="bill")
    assert res._get_node_interface(INTERFACE_DATA, "vercingetorix") == "192.168.6.190"


def test_space_reporting():
    res = resource.Resource(name="test-resource-please-ignore", storage_pool="thin")
    res._update_storage_info(STORAGE_POOL_DATA_0)
    assert res._storage_pool_free_MiB == 36435
    assert res._storage_pool_used_MiB == 6525
    assert res._storage_pool_total_MiB == 42960

    # More redundancy means less usable space.
    res = resource.Resource(
        name="test-resource-please-ignore", storage_pool="thin", auto_place="4"
    )
    res._update_storage_info(STORAGE_POOL_DATA_0)
    assert res._storage_pool_free_MiB == 9108
    assert res._storage_pool_used_MiB == 1632
    assert res._storage_pool_total_MiB == 10740

    # Node-based deployments can only use the space from those nodes.
    res = resource.Resource(
        name="test-resource-please-ignore", storage_pool="thin", nodes=["attila"]
    )
    res._update_storage_info(STORAGE_POOL_DATA_0)
    assert res._storage_pool_free_MiB == 11065
    assert res._storage_pool_used_MiB == 3255
    assert res._storage_pool_total_MiB == 14320

    # Node-based deployments can only use the space from those nodes
    # and must place them on every node, so only count the most
    # space-restricted node.
    res = resource.Resource(
        name="test-resource-please-ignore",
        storage_pool="thin",
        nodes=["attila", "boudicca"],
    )
    res._update_storage_info(STORAGE_POOL_DATA_0)
    assert res._storage_pool_free_MiB == 11065
    assert res._storage_pool_used_MiB == 3255
    assert res._storage_pool_total_MiB == 14320

    with pytest.raises(KeyError):
        res = resource.Resource(
            name="test-resource-please-ignore",
            storage_pool="thin",
            nodes=["attila", "boudicca", "bogus.node"],
        )
        res._update_storage_info(STORAGE_POOL_DATA_0)


def test_is_client():
    res = resource.Resource(name="bill2000")
    assert res._is_client(NODE_DATA_0, "boudicca") is True

    res = resource.Resource(name="bill2000")
    assert res._is_client(NODE_DATA_0, "attila") is False

    res = resource.Resource(name="bill")
    assert res._is_client(NODE_DATA_0, "boudicca") is False

    res = resource.Resource(name="fake-resource")
    with pytest.raises(IndexError):
        assert res._is_client(NODE_DATA_0, "boudicca") is False

    res = resource.Resource(name="bill2000")
    with pytest.raises(IndexError):
        assert res._is_client(NODE_DATA_0, "fake-node") is False

    res = resource.Resource(name="fake-resource")
    with pytest.raises(IndexError):
        assert res._is_client(NODE_DATA_0, "fake-node") is False
