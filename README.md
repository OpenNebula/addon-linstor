# Linstor Storage Driver

## Description

This driver allows for highly available storage using DRBD9 + Linstor in
OpenNebula.

## Development

To contribute bug patches or new features, you can use the github Pull Request
model. It is assumed that code and documentation are contributed under the
Apache License 2.0.

Support for this addon can be found at the
[OpenNebula user forum](https://forum.opennebula.org/c/support) or the
[DRBD-User](http://lists.linbit.com/listinfo/drbd-user) mailing list.

## Authors

Hayley Swimelar [<hayley@linbit.com>](hayley@linbit.com)

## Compatibility

* This addon is compatible with OpenNebula versions up to 5.0.2
* It was tested with versions 4.14 and 5.0.2
* This version of README.md describes the installation process for ONE 5.0.2 environments
* This is intended for use as an images datastore for use with an NFS system datastore

## Requirements

* DRBD9 9.0.1+

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

To upgrade the driver, simply run the installation script again.

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

If you do not intend for the Front-End or Host nodes to be used as storage
nodes in addition to their primary role, they should be added to the DRBD
Manage cluster as
[pure controller nodes](http://docs.linbit.com/doc/users-guide-90/s-dm-add-node/#_adding_a_pure_controller_node).

#### Front-End Configuration

The Front-End node must be a control node with it's own copy of the control
volume, this means that you must provide a small, approximately 4Gb, volume
for the drbdpool volume group, even if you do not plan to use this node for
DRBD storage.

#### Host Configuration

The Host nodes may also be configured as
[pure client nodes](http://docs.linbit.com/doc/users-guide-90/s-dm-add-node/#_adding_a_pure_client_node)
without a local control volume by adding the `--satellite` option while adding
the node the the Linstor cluster. This allows hosts to be added without
preparing local storage for DRBD on that node.

#### Storage Node Configuration

Only the Front-End and Host nodes require OpenNebula to be installed, but the
oneadmin user must be able to passwordlessly access storage nodes. Refer to
the OpenNebula install guide for your distribution on how to manually
configure the oneadmin user account.

The Storage nodes must use one of the storage plugins that support snapshots,
this means one of the thin LVM plugins or ZFS. The merits of the different
plugins are discussed in the
[User's Guide](http://docs.linbit.com/doc/users-guide-90/s-linstor-storage-plugins/#_discussion_of_the_storage_plugins).

In this example preparation of thinly-provisioned storage using LVM for DRBD
Manage, you must create a volume group and thinLV using LVM on each storage
node.

Example of this process using two physical volumes (/dev/sdX and /dev/sdY) and
the default names for the volume group and thinpool. Make sure to set the thinLV's
metadata volume to a reasonable size, once it becomes full it can be difficult to resize:

```bash
pvcreate /dev/sdX /dev/sdY
vgcreate drbdpool /dev/sdX /dev/sdY
lvcreate -l 95%VG --poolmetadatasize 8g -T /dev/drbdpool/drbdthinpool
```

Instructions on how to configure Linstor to use a storage plugin can be
found in the cluster configuration section of the
[User's Guide](http://docs.linbit.com/doc/users-guide-90/s-linstor-storage-plugins/).

### Additonal Driver Configuration

Additional configuration for the driver can be found in the
`datastore/linstor.conf` file in the driver director or in the install path,
normally `/var/lib/one/remotes/datastore/linstor/linstor.conf`

### Permissions for Oneadmin

The oneadmin user must have passwordless sudo access to the `linstor` program on the Front-End node 

```bash
oneadmin ALL=(root) NOPASSWD: /usr/bin/linstor
```

and the `mkfs` command on the Storage nodes

```bash
oneadmin ALL=(root) NOPASSWD: /sbin/mkfs
```

A policy section for the oneadmin user must also be added in
`/etc/dbus-1/system.d/org.drbd.drbdmanaged.conf` on the Front-End node. Be
sure to leave the original policy section intact!

```
<!DOCTYPE busconfig PUBLIC
"-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"
"http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>

  <policy user="0">
    <allow own="org.drbd.drbdmanaged"/>
    <allow send_interface="org.drbd.drbdmanaged"/>
    <allow send_destination="org.drbd.drbdmanaged"/>
  </policy>

  <policy user="oneadmin">
    <allow own="org.drbd.drbdmanaged"/>
    <allow send_interface="org.drbd.drbdmanaged"/>
    <allow send_destination="org.drbd.drbdmanaged"/>
  </policy>

</busconfig>
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
mutually exclusive deployment options: DRBD_REDUNDANCY and
DRBD_DEPLOYMENT_NODES. For both of these options, BRIDGE_LIST must be a space
separated list of all storage nodes in the Linstor cluster.

#### Deploying to a Redundancy Level

The DRBD_REDUNDANCY option takes a level of redundancy which is a number between
one and the total number of storage nodes. Resources are assigned to storage
nodes automatically based on the level of redundancy and Linstor's
deployment policy. The following example shows a cluster with three storage
nodes that will deploy new resources to two of the nodes in the BRIDGE_LIST
based on the free space available on the storage nodes.

```bash
cat >ds.conf <<EOI
NAME = drbdmanage_redundant
DS_MAD = linstor
TM_MAD = linstor
DRBD_REDUNDANCY = 2
BRIDGE_LIST = "alice bob charlie"
EOI

onedatastore create ds.conf
```
#### Deploying to a List of Nodes

Using DRBD_DEPLOYMENT_NODES allows you to select a group of nodes that
resources will always be assigned to. In the following example, new resources
will always be assigned to the nodes alice and charlie. Please note that the
bridge list still contains all of the storage nodes in the Linstor cluster.

```bash
cat >ds.conf <<EOI
NAME = drbdmanage_nodes
DS_MAD = linstor
TM_MAD = linstor
DRBD_DEPLOYMENT_NODES = "alice charlie"
BRIDGE_LIST = "alice bob charlie"
EOI

onedatastore create ds.conf
```
#### Restricting Where Resources Can Be Deployed

Using DRBD_DEPLOYMENT_SITE allows you to select a [site](https://www.drbd.org/en/doc/users-guide-90/s-dm-set-config)
defined in DRBD MANAGE to restrict deployment of resources. This optional setting
works in tandem with either DRBD_DEPLOYMENT_NODES or DRBD_REDUNDANCY. When
deploying to a redundancy level, only nodes within the site are considered when
deciding which nodes to deploy on. When deploying to a list of nodes, this
option blocks deployment to nodes listed in DRBD_DEPLOYMENT_NODES that are not
also in the site.

```bash
cat >ds.conf <<EOI
NAME = drbdmanage_nodes
DS_MAD = linstor
TM_MAD = linstor
DRBD_REDUNDANCY = 2
BRIDGE_LIST = "alice bob charlie"
DRBD_DEPLOYMENT_SITE = "alpha"
EOI

onedatastore create ds.conf
```
#### Optional Attributes

There are three additional attributes that you may add to a datastore's
template. These can be used to overwrite the options of the same name in the
`datastore/linstor.conf` file.

DRBD_MIN_COUNT is the minimum number of nodes that a resource must be deployed
on for the deployment of a new resource to be considered a success. This
should be an integer between 0 and the total number of storage nodes in your
Linstor cluster.

DRBD_MIN_RATIO is the ratio of nodes a resource must be deployed on for the
deployment of a new resource to be considered a success. This should be a
number between 0.0 and 1.0.

More information on the above policies can be found in the
[Policy Plugin](http://docs.linbit.com/doc/users-guide-90/s-linstor-deployment-policy/)
section of the
[DRBD9 User's Guide](http://docs.linbit.com/doc/users-guide-90/drbd-users-guide/).

DRBD_SUPPORT_LIVE_MIGRATION enables the live migration of VMs. Valid options are
"yes" and "no" (default). If this option is enabled, you must also configure
your Linstor cluster to allow dual primary.  To do this, run the following
command:

```bash
linstor net-options --allow-two-primaries yes --common
```

Please note that images that were created before live migration support has been
enabled may not be available to all hosts. These images may be assigned to hosts
after the fact using Linstor directly.

#### Validating a Datastore Configuration

It is recommended to validate your configuration using the validation tool
provided with the driver. The tool will report any errors it finds in your
configuration. Simply pass the configuration file you wish to validate as an
argument.

```bash
./validate_config.py ds.conf
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
