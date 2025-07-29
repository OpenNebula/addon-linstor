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
