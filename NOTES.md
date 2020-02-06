# Dev-notes

Here are some notes on how to trigger various driver scripts:


## datastore

### clone

Used in various places.
Storage -> Images -> Clone

### cp

Storage -> Images -> Add Image ->
Type: Readonly CD-ROM
Datastore: linstor datastore
* Path from server
Path: path to an uploaded iso on the server

-- Advance
BUS: SCSI

### export

???

### mkfs

Storage -> Images -> Add Image ->
Type: Generic storage datablock
Datastore: linstor datastore
Persistent: yes
* Empty disk image

-- Advance
BUS: virtio
Image mapping driver: qcow2

### monitor

Periodically called

### rm

Storage -> Images -> Trash symbol

### snap_delete

Image needs to be unused and has snapshots.

Storage -> Images -> select image -> Snapshots -> delete

### snap_flatten

Image needs to be unused and has snapshots.

Storage -> Images -> select image -> Snapshots -> flatten

### snap_revert

Image needs to be unused and has snapshots.

Storage -> Images -> select image -> Snapshots -> revert


## tm  (transfer manager)

Most of these functions will only be trigger if run in an linstor system datastore


### clone

???

### context

Instantiate or migrate/live migrate a running VM to another host

### cpds

Instances -> VM -> Running VM -> Storage -> Actions -> SaveAs(Disk symbol)

### delete

Instances -> VM -> Trash symbol

### ln

Instantiate a new VM with a image attached
Or attaching a image to a VM

### monitor

Periodically called

### mv

Migrate offline VM to another host

### mvds

Detach image from VM

### postmigrate

Live migrate VM

### premigrate

Live migrate VM

### failmigrate

Called if a KVM migrate command failed, used for cleanup premigrate stuff

### resize

Instances -> VM -> (Running) VM -> Storage -> Actions -> resize

### snap_create

Instances -> VM -> Powered off VM -> Storage -> Actions -> snapshot

### snap_creat_live

???

### snap_delete

Instances -> VM -> Powered off VM -> Storage -> Actions -> delete snapshot

### snap_revert

Instances -> VM -> Powered off VM -> Storage -> Actions -> revert to snapshot

### mkswap

Add a volatile disk to an VM and instantiate

### mkimage

Add a volatile non swap disk to an VM and instantiate
