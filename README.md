# Linstor Storage Driver

## Description

This driver allows for highly available storage using DRBD9 + Linstor in
OpenNebula.

## Development

To contribute bug patches or new features, you can use the github Pull Request
feature. It is assumed that code and documentation are contributed under the
Apache License 2.0.

Before submitting pull requests, please run the `./format.sh` script found
in the root of the project and test using `tox`.

Support for this addon can be found at the
[DRBD-User](http://lists.linbit.com/listinfo/drbd-user) mailing list.

## Authors

* Rene Peinthor [<rene.peinthor@linbit.com>](rene.peinthor@linbit.com)

## Compatibility

* This addon is compatible with OpenNebula versions from 5.8 to 7.0
* It was tested with version 6.8 and 7.0
* SSH agent forwarding for nested SSH transfer paths uses OpenNebula's
  `ssh_forward` helper when it is available. The helper is present in
  OpenNebula release 5.11.8 and newer stable releases, including 5.12 and
  later. On older OpenNebula versions, the driver falls back to an equivalent
  SSH command override using `ForwardAgent=yes`, `ControlMaster=no`, and
  `ControlPath=none`.
* This version of README.md describes the installation process for ONE 5.6 environments
* This is intended for use as an images datastore for use with either an NFS shared
* system datastore or a SSH system datastore

## Requirements

* DRBD9 9.0.28+
* LINSTOR 1.18.0+

## Features

* quickly attaches images to VMs
* fast image clones
* transfers images over the network in diskless mode
* allows for live migration even if the ssh system datastore is used

## Installation

Follow these steps on the Front-End node only.

### Clone the Repository and Run the Install Script.

Run the following commands as either oneadmin or whichever user is filling the
`ONE_USER` role (or have the `ONE_USER` environment defined):

```bash
python setup.py install
```

## Upgrading

To upgrade the driver, simply run the above installation script again.

## From 2.x to 3.x


### Linstor system datastore

In version 3.x we removed handling context images within Linstor plugin
and fallback to the `tm/ssh` implementation.

This means you have to remove the `CONTEXT_DISK_TYPE` attribute from
the Linstor system datastore, as we now use the default FILE type.

Context images are just read-only ISO files that are recreated everytime
the VM is started and there is not much benefit form having them
as DRBD resources.

The plugin will delete old context images on VM delete and undeploy actions.
If you want to clean up the context images `OpenNebula-vm-context-*` you need to
stop and start the VM that is still using it (no reboot).

## Configuration
Please refer the DRBD user guide for configuration and documentation:
[Linstor User's guide](https://docs.linbit.com/docs/linstor-guide/#ch-opennebula-linstor)

### Controller authentication

If your LINSTOR controller requires authentication, set the auth token on the
datastore template with the `LINSTOR_CONTROLLER_AUTH_TOKEN` attribute:

```
LINSTOR_CONTROLLER_AUTH_TOKEN = "<token>"
```

The token is sent as a bearer token and **only over a secure (HTTPS) connection**.
Make sure `LINSTOR_CONTROLLERS` uses the `linstor+ssl://` scheme (or a plain
`linstor://` controller that redirects to HTTPS); over plain HTTP the token is not
transmitted and requests would be unauthenticated.

### Interactive backups (OneBEX)

Interactive backups (`BACKUP_CONFIG/INTERACTIVE = "YES"`, e.g. the Veeam
integration) export the disks through the OpenNebula Backup Exporter (OneBEX)
with the `linstor` exporter. Full and incremental backups are supported;
incremental backups use LINSTOR's changed block tracking (CBT) if the LINSTOR
cluster supports it, see below. Non-interactive backups are still done by
OpenNebula's shared TM driver.

Requirements:

* OpenNebula 7.4.2 or later. Earlier versions only allow interactive backups for
  OpenNebula's own storage drivers and don't load third party OneBEX exporters
* the VM hosts are LINSTOR satellites: the backup reads the snapshot there through a
  (diskless) temporary resource
* for changed block tracking: LINSTOR with CBT support (REST API 1.30.0+), a
  python-linstor that supports it, DRBD and drbd-utils with CBT support and storage
  pools of type LVM, LVM-thin, ZFS or ZFS-thin
* for Veeam: an oVirt API server that reports the device size of the disks, see
  below

Without changed block tracking (any of the latter missing), interactive backups
still work, but every backup — also an increment of a chain — exports the whole
disk: the driver restores a plain snapshot into a temporary resource
(`OpenNebula-Backup-vm<vm>-disk<disk>`) that is made available on the VM's host.
Restoring a snapshot of a thick LVM pool copies the volume, thin LVM and ZFS pools
are recommended. The driver decides per backup, so it uses CBT once the cluster
supports it (the first such backup of a chain exports the whole disk once more).

Enable interactive backups for the driver in the `linstor` `TM_MAD_CONF` of
`/etc/one/oned.conf` and restart OpenNebula (`systemctl restart opennebula`):

```
TM_MAD_CONF = [
    NAME = "linstor", ...,
    INTERACTIVE_BACKUP = "YES"
]
```

Without it, `onevm backup` fails with `Disk does not support interactive backup`.

`python setup.py install` installs the exporter to
`/var/lib/one/remotes/onebex/exporters/linstor.rb`, where OneBEX loads it;
copy it to the hosts with `onehost sync --force`. If backups fail with
`Unsupported exporter: linstor`, OneBEX on the VM's host could not load it: the
error is logged in `/var/log/one/onebex.log` when OneBEX starts.

How a backup with CBT works: the guest is frozen if `FS_FREEZE` asks for it, all
disks get one CBT snapshot (`OpenNebula-Backup-<timestamp>`), and each snapshot is
made readable on the VM's host through a LINSTOR CBT session. The session and the
snapshot are removed once the backup application finished. The exporter reports the
disk's extents as ovirt-imageio does: a full backup skips the blocks that were never
written (with drbd-utils 9.36.0 or later). An incremental backup
only exports the changed blocks if the previous backup of the chain was the last
CBT snapshot of the disk; it is recorded in the resource definition property
`Aux/one/backup-cbt`. Otherwise — the previous backup failed, or another CBT
snapshot of the resource was taken in between — the increment contains the whole
disk. Every CBT snapshot starts a new tracking interval, so don't take CBT
snapshots of OpenNebula resources outside of the backups.

Exports have the size of the disk's DRBD device. LINSTOR allocates a volume's size
plus the DRBD metadata, rounded up to the allocation granularity of the storage pool
(the LVM extent size), so the device is up to one extent larger than the disk size
OpenNebula shows, and guests use that space (cloud-init growpart, one-context
grow-rootfs). Backup applications have to take the disk size from the device: with
an oVirt API server that reports the OpenNebula size, Veeam aborts backups of such
disks with `Received an area which goes beyond disk size`.

### Raw images

Without `LINSTOR_CONVERT_TO_RAW` the driver writes images to the DRBD device as
they are: a qcow2 image stays a qcow2 container on the device. Snapshots, CBT and
interactive backups see the device, so backups of such disks export the container
instead of the guest's blocks. To store all images as raw, set in the image
datastore template:

```
LINSTOR_CONVERT_TO_RAW = "YES"
```

This is the recommended setting for new image datastores, set it when you create
the datastore:

```
NAME = linstor_datastore
TYPE = IMAGE_DS
DS_MAD = linstor
TM_MAD = linstor
DISK_TYPE = BLOCK
LINSTOR_CONTROLLERS = "alice:3370"
LINSTOR_RESOURCE_GROUP = "OneRscGrp"
BRIDGE_LIST = "alice bob charlie"
LINSTOR_CONVERT_TO_RAW = "YES"
DRIVER = "raw"
```

The option is off if the attribute is missing, so existing datastores keep their
behavior. It can also be enabled on a datastore that already has images, see the
notes below.

Every image copied into the datastore (imports, marketplace appliances, restores of
backups) is then copied onto a temporary volume on the first diskful node of its new
resource and converted from there with `qemu-img convert` onto the DRBD device. The
image is registered as `FORMAT = raw`, so VMs use it with the raw driver.

The volume gets the image's size. For imports `stat` reports the image's virtual
size, so the volume holds it. Marketplace appliances and backups report a size of
their own: if their virtual size is larger than the device and the image only has
zeros beyond it, they are dropped. Otherwise, e.g. for GPT disks with their backup
header in the last sector, the volume is grown to the virtual size.

* the temporary volume is a LINSTOR resource without DRBD (`OpenNebula-Staging-<image>`)
  in the storage pool of the image on that node: the downloaded image isn't replicated
  and needs no space in a file system of the node. It is removed afterwards
* the temporary volume has the image's size plus 1% and 64 MiB, the storage pool needs
  room for it during the import (thin pools only for the downloaded data). Image files
  larger than that, e.g. qcow2 images with internal snapshots, fail the import
* `qemu-img` has to be installed on the storage nodes
* on new thin volumes (LVM-thin, ZFS) the zero areas of the image aren't written
* images that refer to other files (backing files, external data files, VMDKs with
  separate extent files) and encrypted images are rejected
* empty datablocks must have `FORMAT = raw`, the default. `DRIVER = "raw"` in the
  datastore template enforces it
* existing images aren't converted, and image clones and disks saved with
  `onevm disk-saveas` keep the format of their source

For interactive backups, also set `INTERACTIVE_BACKUP_FORMATS = "raw"` in the
`linstor` `TM_MAD_CONF`, so OpenNebula rejects backups of remaining qcow2 disks right
away.

## Usage

This driver will use Linstor to create new images and transfer them to
hosts. Images are attached to hosts across the network using diskless mode.
Images are replicated according to the deployment policy set in the datastore
template.

## License

Apache 2.0

## DRBD9 and Linstor User's Guide

If you have any questions about setting up, tuning, or administrating DRBD9 or
Linstor, be sure to check out the information provided in the
[Drbd User's Guide](http://docs.linbit.com/doc/users-guide-90/drbd-users-guide/)
or the
[Linstor User's Guide](https://docs.linbit.com/docs/linstor-guide/#ch-opennebula-linstor)
