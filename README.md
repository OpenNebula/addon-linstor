# Linstor Storage Driver

## Description

This driver allows for highly available storage using DRBD9 + Linstor in
OpenNebula.

## Development

To contribute bug patches or new features, you can use the github Pull Request
model. It is assumed that code and documentation are contributed under the
Apache License 2.0.

Before sumbitting pull requests, please run the `./format.sh` script found
in the root of the project and test using `tox`.

Support for this addon can be found at the
[OpenNebula user forum](https://forum.opennebula.org/c/support) or the
[DRBD-User](http://lists.linbit.com/listinfo/drbd-user) mailing list.

## Authors

Hayley Swimelar [<hayley@linbit.com>](hayley@linbit.com)

## Compatibility

* This addon is compatible with OpenNebula versions up to 5.6
* It was tested with version 5.6
* This version of README.md describes the installation process for ONE 5.6 environments
* This is intended for use as an images datastore for use with a NFS shared system datastore

## Requirements

* DRBD9 9.0.14+

## Features

* quickly attaches images to VMs
* fast image clones
* transfers images over the network in diskless mode

## Limitations

* snapshots of images are not available
* this driver does not support the ssh system datastore

## Installation

Follow these steps on the Front-End node only.

### Clone the Repository and Run the Install Script.

Run the following commands as either oneadmin or root:

```bash
python setup.py install
```

### Upgrading

To upgrade the driver, simply run the above installation script again.

## Configuration

### Configure the Driver in OpenNebula

Modify the following sections of `/etc/one/oned.conf`

Add linstor to the list of drivers in the `TM_MAD` and `DATASTORE_MAD`
sections:

```
TM_MAD = [
  executable = "one_tm",
  arguments = "-t 15 -d dummy,lvm,shared,fs_lvm,qcow2,ssh,vmfs,ceph,linstor"
]
```
```
DATASTORE_MAD = [
    EXECUTABLE = "one_datastore",
    ARGUMENTS  = "-t 15 -d dummy,fs,lvm,ceph,dev,iscsi_libvirt,vcenter,linstor -s shared,ssh,ceph,fs_lvm,qcow2"
```

Add new TM_MAD_CONF and DS_MAD_CONF sections:

```
TM_MAD_CONF = [
    name = "linstor", ln_target = "NONE", clone_target = "SELF", shared = "yes"
]
```
```
DS_MAD_CONF = [
    NAME = "linstor", REQUIRED_ATTRS = "BRIDGE_LIST", PERSISTENT_ONLY = "NO",
    MARKETPLACE_ACTIONS = "export"
]
```
After making these changes, restart the opennebula service.

### Configuring the Nodes

#### Overview of node Roles

The Front-End node issues commands to the Storage and Host nodes via DRBD
Manage.

Storage nodes hold disk images of VMs locally.

Host nodes are responsible for running instantiated VMs and typically have the
storage for the images they need attached across the network via Linstor
diskless mode.

All nodes must have DRBD9 and Linstor installed. This process is detailed in the
[User's Guide for DRBD9](http://docs.linbit.com/doc/users-guide-90/ch-admin-linstor/)

It is possible to have Front-End and Host nodes act as storage nodes in
addition to their primary role as long as they the meet all the requirements
for both roles.


#### Front-End Configuration

The Front-End node must have the `linstor` command in its `PATH`. Please verify
that the control node(s) that you hope to communicate with are reachable from
the Front-End node. `linstor node list` for locally running Linstor controllers
and `linstor --controllers "<IP:PORT>" node list` for remotely running Linstor
Controllers is a handy way to test this.

#### Host Configuration

Host nodes must have Linstor satellite processes running on them and be members
of the same Linstor cluster as the Front-End and Storage nodes, and may optionally
have storage locally.

#### Storage Node Configuration

Only the Front-End and Host nodes require OpenNebula to be installed, but the
oneadmin user must be able to passwordlessly access storage nodes. Refer to
the OpenNebula install guide for your distribution on how to manually
configure the oneadmin user account.

The Storage nodes must use storage pools created with a driver that's capabile
if making snapshots such as the thin LVM plugin.

In this example preparation of thinly-provisioned storage using LVM for Linstor,
you must create a volume group and thinLV using LVM on each storage node.

Example of this process using two physical volumes (/dev/sdX and /dev/sdY) and
generic names for the volume group and thinpool. Make sure to set the thinLV's
metadata volume to a reasonable size, once it becomes full it can be difficult to resize:

```bash
pvcreate /dev/sdX /dev/sdY
vgcreate drbdpool /dev/sdX /dev/sdY
lvcreate -l 95%VG --poolmetadatasize 8g -T /dev/drbdpool/drbdthinpool
```

Then you'll create storage pool(s) on Linstor using this as the backing storage.

### Permissions for Oneadmin

The oneadmin user must have passwordless sudo access to the `mkfs` command on
the Storage nodes

```bash
oneadmin ALL=(root) NOPASSWD: /sbin/mkfs
```

#### Groups

Be sure to consider the groups that oneadmin should be added to in order to
gain access to the devices and programs needed to access storage and
instantiate VMs. For this addon, the oneadmin user must belong to the `disk`
group on all nodes in order to access the DRBD devices where images are held.

```bash
usermod -a -G disk oneadmin
```

### Creating a New Linstor Datastore

Create a datastore configuration file named ds.conf and use the `onedatastore`
tool to create a new datastore based on that configuration. There are two
mutually exclusive deployment options: LINSTOR_AUTO_PLACE and
LINSTOR_DEPLOYMENT_NODES. If both are configured, LINSTOR_AUTO_PLACE is ignored.
For both of these options, BRIDGE_LIST must be a space
separated list of all storage nodes in the Linstor cluster.

#### Deploying via auto placement

The LINSTOR_AUTO_PLACE option takes a level of redundancy which is a number between
one and the total number of storage nodes. Resources are assigned to storage
nodes automatically based on the level of redundancy.
The following example shows a cluster with three storage
nodes that will deploy new resources to two of the nodes that have the LINSTOR_STORAGE_POOL
named "thin" configured on them.

```bash
cat >ds.conf <<EOI
NAME = linstor_auto_place
DS_MAD = linstor
TM_MAD = linstor
LINSTOR_AUTO_PLACE = 2
LINSTOR_STORAGE_POOL = "thin"
BRIDGE_LIST = "alice bob charlie"
EOI

onedatastore create ds.conf
```
#### Deploying to a List of Nodes

Using LINSTOR_DEPLOYMENT_NODES allows you to select a group of nodes that
resources will always be assigned to. In the following example, new resources
will always be assigned to the nodes alice and charlie. Please note that the
bridge list still contains all of the storage nodes in the Linstor cluster.

```bash
cat >ds.conf <<EOI
NAME = drbdmanage_nodes
DS_MAD = linstor
TM_MAD = linstor
LINSTOR_DEPLOYMENT_NODES = "alice charlie"
BRIDGE_LIST = "alice bob charlie"
EOI

onedatastore create ds.conf
```

#### Optional Attributes

Additional attributes that you may add to a datastore's
template:


##### linstor_controllers

linstor_controllers can be used to pass a comma separated list of controller
ips and ports to the Linstor client in the case where a Linstor controller
process is not running locally on the Front-End:

```bash
cat >ds.conf <<EOI
NAME = drbdmanage_nodes
DS_MAD = linstor
TM_MAD = linstor
LINSTOR_DEPLOYMENT_NODES = "alice charlie"
LINSTOR_CONTROLLERS = "192.168.1.10:8080,192.168.1.11:6000"
BRIDGE_LIST = "alice bob charlie"
EOI

onedatastore create ds.conf
```

## Usage

This driver will use Linstor to create new images and transfer them to
hosts. Images are attached to hosts across the network using diskless mode.
Images are replicated according to the deployment policy set in the datastore
template.

## License

Apache 2.0

##DRBD9 and Linstor User's Guide

If you have any questions about setting up, tuning, or administrating DRBD9 or
Linstor, be sure to check out the information provided in the
[User's Guide](http://docs.linbit.com/doc/users-guide-90/drbd-users-guide/)
