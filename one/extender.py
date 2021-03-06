import time

from linstor import Resource, Volume, MultiLinstor, LinstorError, SizeCalc
from linstor.responses import ResourceDefinitionResponse
from one import util, consts
from one.vm import Vm
from one.datastore import Datastore
from one.image import Image


def calculate_space(lin, storage_pool_name, nodes, auto_place):
    """

    :param linstor.MultiLinstor lin:
    :param str storage_pool_name:
    :param nodes:
    :param auto_place:
    :return: Tuple with 3 values (used, total, free) in MiB
    :rtype: Tuple(int, int, int)
    """

    storage_pools = lin.storage_pool_list_raise(filter_by_stor_pools=[storage_pool_name])
    free_space_by_node = {x.node_name: x.free_space for x in storage_pools.storage_pools if x.free_space}
    storage_pool_total_mib = 0
    storage_pool_free_mib = 0
    if nodes:
        lowest_free_node = nodes[0]
        for node in nodes:
            if node not in free_space_by_node:
                raise RuntimeError(
                    "Node '{node}' does not have storage pool '{sp}'".format(node=node, sp=storage_pool_name)
                )
            if free_space_by_node[node].total_capacity < free_space_by_node[node].total_capacity:
                lowest_free_node = node
        storage_pool_total_mib += free_space_by_node[lowest_free_node].total_capacity // 1024
        storage_pool_free_mib += free_space_by_node[lowest_free_node].free_capacity // 1024
    else:
        for space_info in free_space_by_node.values():
            storage_pool_total_mib += (space_info.total_capacity // int(auto_place)) // 1024
            storage_pool_free_mib += (space_info.free_capacity // int(auto_place)) // 1024

    return storage_pool_total_mib - storage_pool_free_mib, storage_pool_total_mib, storage_pool_free_mib


def node_has_storagepool(uri_list, node, storage_pool):
    """
    Checks if a node has the given storage pool.

    :param str uri_list: linstor controller uri list
    :param str node: node to check for storage pool
    :param str storage_pool: storage pool name to check
    :return: True if node has the given storage pool
    :rtype: bool
    """
    with MultiLinstor(MultiLinstor.controller_uri_list(uri_list)) as lin:
        stor_pool_result = lin.storage_pool_list_raise(filter_by_nodes=[node], filter_by_stor_pools=[storage_pool])
        return bool(stor_pool_result.storage_pools)


def deploy(
        linstor_controllers,
        resource_name,
        storage_pool,
        vlm_size_str,
        deployment_nodes,
        auto_place_count,
        resource_group=None,
        prefer_node=None
):
    """
    Deploys resource depending on resource_group, deployment nodes or auto_place setting.

    :param str linstor_controllers:
    :param str resource_name: Name of the new resource definition
    :param str storage_pool: Name of the storage pool to use
    :param str vlm_size_str: volume size string
    :param list[str] deployment_nodes: list of node names
    :param int auto_place_count:
    :param Optional[str] resource_group: Name of the resource group to use
    :param Optional[str] prefer_node: Tries to place a diskful on this node(if autoplace)
    :return: Resource object of the new deployment
    :rtype: Resource
    """
    if resource_group:
        util.log_info("Deploying resource '{}' using resource group '{}', prefer node: {n}".format(
            resource_name, resource_group, n=prefer_node))
        resource = Resource.from_resource_group(
            linstor_controllers,
            resource_group,
            resource_name,
            [vlm_size_str],
            definitions_only=bool(prefer_node)
        )
        if prefer_node:
            resource.placement.redundancy = None  # force resource group values, default would be 2
            resource.placement.storage_pool = storage_pool
            if node_has_storagepool(linstor_controllers, prefer_node, storage_pool):
                resource.diskful(prefer_node)
            resource.autoplace()
    else:
        resource = Resource(resource_name, linstor_controllers)
        resource.placement.storage_pool = storage_pool
        resource.volumes[0] = Volume(vlm_size_str)
        if deployment_nodes:
            util.log_info("Deploying resource '{}' using deployment_nodes '{}'".format(resource_name, deployment_nodes))
            for node in deployment_nodes:
                resource.diskful(node)
        elif auto_place_count:
            util.log_info("Deploying resource '{}' using auto-place-count {}, prefer node: {n}".format(
                resource_name, auto_place_count, n=prefer_node))
            if prefer_node and node_has_storagepool(linstor_controllers, prefer_node, storage_pool):
                resource.diskful(prefer_node)
            resource.placement.redundancy = auto_place_count
            resource.autoplace()
        else:
            raise RuntimeError("No deploy mode selected. nodes: {n}, resource_group: {a}".format(
                n=deployment_nodes, a=resource_group)
            )
    return resource


def delete(resource_name, uri_list):
    """
    Deletes a resource with all it's snapshots

    :param str resource_name: name of the resource
    :param str uri_list: linstor uris string
    :return: True
    """
    with MultiLinstor(MultiLinstor.controller_uri_list(uri_list)) as lin:
        snapshots = lin.snapshot_dfn_list()[0]
        for snap in [x for x in snapshots.snapshots if x.rsc_name == resource_name]:
            util.log_info("Deleting snapshot '{r}/{s}'".format(r=resource_name, s=snap.snapshot_name))
            lin.snapshot_delete(rsc_name=resource_name, snapshot_name=snap.snapshot_name)

        # there is a regression in python-linstor 0.9.5, were it isn't possible to try to delete
        # non existing resources (exception with None value)
        # so deleting it with the low level api still works, also opennebula doesn't need the external name feature
        util.log_info("Deleting resource '{r}'".format(r=resource_name))
        rs = lin.resource_dfn_delete(name=resource_name)
        if not rs[0].is_success():
            raise LinstorError('Could not delete resource {}: {}'.format(resource_name, rs[0]))
    return True


def delete_vm_contexts(uri_list, vm_id, disk_id):
    """
    Tries to delete all generated vm context images.
    First queries linstor for all context images for the vm and then deletes one by one ignoring any failed attempts.

    :param str uri_list: linstor uri list string
    :param int vm_id: Opennebula id of the VM
    :param int disk_id: Opennebula disk id of the VM
    :return: Dict, where key is the resource name and either None(Success) or LinstorError on failure.
    :rtype: dict[str, Optional[LinstorError]]
    """
    del_result = {}
    with MultiLinstor(MultiLinstor.controller_uri_list(uri_list)) as lin:
        rsc_dfn_list_resp = lin.resource_dfn_list(query_volume_definitions=False)
        if rsc_dfn_list_resp:
            rsc_dfn_list = rsc_dfn_list_resp[0]  # type: ResourceDefinitionResponse
            delete_list = [x.name for x in rsc_dfn_list.resource_definitions
                           if x.name.startswith(consts.CONTEXT_PREFIX + "-vm{vm_id}-disk{disk_id}"
                                                                        .format(vm_id=vm_id, disk_id=disk_id))]
            for rsc_name in delete_list:
                try:
                    delete(rsc_name, uri_list)
                    del_result[rsc_name] = None
                except LinstorError as le:
                    del_result[rsc_name] = le

    return del_result


class CloneMode(object):
    SNAPSHOT = 1
    COPY = 2

    __STR_MAP = {
        "snapshot": SNAPSHOT,
        "copy": COPY
    }

    @classmethod
    def from_str(cls, clone_mode):
        return cls.__STR_MAP.get(clone_mode)

    @classmethod
    def to_str(cls, clone_mode):
        for x in cls.__STR_MAP:
            if cls.__STR_MAP[x] == clone_mode:
                return x
        return None


def get_in_use_node(resource):
    """
    Returns the node that currently has the resource primary.

    :param Resource resource: resource object to check for in use(primary).
    :return: node name of the primary node, or None if all secondary
    :rtype: Optional[str]
    """
    with MultiLinstor(resource.client.uri_list) as lin:
        lst = lin.resource_list(filter_by_resources=[resource.name])
        if lst:
            nodes = [x for x in lst[0].resource_states if x.in_use]
            if nodes:
                return nodes[0].node_name
    return None


def clone(
        resource,
        clone_name,
        place_nodes,
        auto_place_count,
        resource_group=None,
        mode=CloneMode.SNAPSHOT,
        prefer_node=None,
        new_size=None):
    """
    Clones a resource to a new resource.

    :param Resource resource: resource object to clone
    :param str clone_name: name of the new resource
    :param list[str] place_nodes: deployment nodes string, e.g. "alpha bravo charly"
    :param int auto_place_count:
    :param Optional[str] resource_group: resource group to use
    :param int mode:
    :param Optional[str] prefer_node: try to place resource on this node
    :param Optional[int] new_size: new volume size, works only in CloneMode.COPY, None to keep original size
    :return: True if clone was successful
    :rtype: bool
    """
    return_code = 0
    util.log_info("Cloning from resource '{src}' to '{tgt}' clone mode {m}.".format(
        src=resource.name, tgt=clone_name, m=CloneMode.to_str(mode))
    )

    if mode == CloneMode.SNAPSHOT and resource.placement.storage_pool \
            and resource.placement.storage_pool != resource.volumes[0].storage_pool_name:
        util.log_info(
            "Deployment storage pool '{dp}' in different storage pool '{sp}', fall back to clone mode COPY".format(
                dp=resource.placement.storage_pool, sp=resource.volumes[0].storage_pool_name
            )
        )
        mode = CloneMode.COPY

    use_storpool = resource.placement.storage_pool \
        if resource.placement.storage_pool else resource.volumes[0].storage_pool_name
    linstor_controllers = ",".join(resource.client.uri_list)

    if mode == CloneMode.SNAPSHOT:
        snap_name = "for-" + clone_name
        try:
            resource.snapshot_create(snap_name)
            clone_res = resource.restore_from_snapshot(snap_name, clone_name)
            time.sleep(1)  # wait a second for deletion, here is a potential race condition
            if prefer_node and node_has_storagepool(linstor_controllers, prefer_node, use_storpool):
                clone_res.placement.storage_pool = use_storpool
                clone_res.diskful(prefer_node)
        finally:
            # always try to get rid of the temporary snapshot
            try:
                resource.snapshot_delete(snap_name)
            except LinstorError as le:
                #  the snapshot delete will always fail for zfs storage pools (parent-child relation)
                util.log_info("Snapshot '{s}' delete failed: {ex}".format(s=snap_name, ex=le))
    elif mode == CloneMode.COPY:
        vol_size_str = str(new_size) + "MiB" if new_size else str(resource.volumes[0].size) + "b"
        clone_res = deploy(
            linstor_controllers=linstor_controllers,
            resource_name=clone_name,
            storage_pool=use_storpool,
            vlm_size_str=vol_size_str,
            deployment_nodes=place_nodes,
            auto_place_count=auto_place_count,
            resource_group=resource_group,
            prefer_node=prefer_node
        )

        # use copy source on the current primary node or on one with a disk, if all secondary
        copy_node = get_in_use_node(resource)
        if copy_node is None:
            if prefer_node in resource.diskful_nodes():
                copy_node = prefer_node
            else:
                copy_node = resource.diskful_nodes()[0]
        clone_res.activate(copy_node)

        from_dev_path = get_device_path(resource)
        to_dev_path = get_device_path(clone_res)

        block_size_kb = 64

        block_count = resource.volumes[0].size / 1024.0 / block_size_kb  # float division
        block_count_int = int(block_count) if block_count.is_integer() else (block_count + 1)

        conv_opts = ["fsync"]
        if clone_res.is_thin():
            conv_opts.append("sparse")

        dd_cmd = 'dd if={_if} of={_of} bs={bs}K count={c} conv={conv}'.format(
            _if=from_dev_path,
            _of=to_dev_path,
            bs=block_size_kb,
            c=block_count_int,
            conv=",".join(conv_opts)
        )
        # dd on the node
        return_code = util.ssh_exec_and_log(
            host=copy_node,
            cmd=dd_cmd,
            error_msg='error copying image data from {_if} to {_of}'.format(_if=from_dev_path, _of=to_dev_path))

        time.sleep(0.5)  # wait a bit until we are sure dd closed the block device

        clone_res.deactivate(copy_node)

    return return_code == 0


def get_rsc_name(target_vm, disk_id):
    """
    Tries to detect the correct resource name.

    :param Vm target_vm: Vm object
    :param str disk_id: Id of the disk vm
    :return: The linstor resource name
    :rtype: str
    """
    disk_source = target_vm.disk_source(disk_id)
    if not disk_source:  # volatile
        res_name = consts.VOLATILE_PREFIX + "-vm{}-disk{}".format(target_vm.id, disk_id)
    else:
        res_name = target_vm.disk_source(disk_id)

        if not target_vm.disk_persistent(disk_id):
            if target_vm.disk_type(disk_id) == "CDROM":
                util.log_info("{} is a non-persistent CDROM image".format(res_name))
            else:
                res_name = "{}-vm{}-disk{}".format(res_name, target_vm.id, disk_id)
                util.log_info(
                    "{} is a non-persistent OS or DATABLOCK image".format(res_name)
                )
        else:
            util.log_info("{} is a persistent OS or DATABLOCK image".format(res_name))

    return res_name


def get_current_context_id(uri_list, vm_id, disk_id):
    """

    :param str uri_list: linstor uri list string
    :param int vm_id: Opennebula id of the VM
    :param int disk_id: Opennebula disk id of the VM
    :return:
    :rtype: Optional[int]
    """
    with MultiLinstor(MultiLinstor.controller_uri_list(uri_list)) as lin:
        rsc_dfn_list_resp = lin.resource_dfn_list(query_volume_definitions=False)
        if rsc_dfn_list_resp:
            rsc_dfn_list = rsc_dfn_list_resp[0]  # type: ResourceDefinitionResponse
            prefix = consts.CONTEXT_PREFIX + "-vm{vm_id}-disk{disk_id}".format(vm_id=vm_id, disk_id=disk_id)
            contexts = [x.name for x in rsc_dfn_list.resource_definitions
                        if x.name.startswith(prefix)]
            index_dict = {}
            for context in contexts:
                strindex = context[len(prefix):]
                if strindex:  # e.g. strindex = '-2'
                    numindex = int(strindex[1:])
                else:
                    numindex = 0
                index_dict[numindex] = context
            return sorted(index_dict.keys())[-1] if index_dict else None
    return None


def get_current_context(uri_list, vm_id, disk_id):
    """
    Returns the latest/current context resource name for the specified vm_id and disk_id

    :param str uri_list: linstor uri list string
    :param int vm_id: Opennebula id of the VM
    :param int disk_id: Opennebula disk id of the VM
    :return: resource name string
    :rtype: str
    """
    c_id = get_current_context_id(uri_list, vm_id, disk_id)
    if c_id is None:
        return None
    elif c_id == 0:
        return consts.CONTEXT_PREFIX + "-vm{vm_id}-disk{disk_id}".format(vm_id=vm_id, disk_id=disk_id)
    return consts.CONTEXT_PREFIX + "-vm{vm_id}-disk{disk_id}-{cid}".format(vm_id=vm_id, disk_id=disk_id, cid=c_id)


def get_device_path(res):
    """
    Tries to get the correct device path for the resource.
    Usually device_path should be available from res.volumes[0].device_path,
    but old bugs/timing issues may render them empty, so this helps to acquire a valid device_path.

    :param Resource res: resource object to get the device path from
    :return: device path of the first volume
    :rtype: str
    :raises: RuntimeError if it isn't possible to get a device path
    """
    device_path = res.volumes[0].device_path

    if not device_path and res.volumes[0].minor is not None:
        device_path = "/dev/drbd{minor}".format(minor=res.volumes[0].minor)

    if not device_path:
        raise RuntimeError("Could not get volume device path for resource '{res}'".format(res=res.name))

    return device_path


def get_storage_pool_name(lin, datastore):
    """
    Returns the used storage pool of the given datastore.

    :param MultiLinstor lin: Linstor access object
    :param Datastore datastore: Opennebula datastore object
    :return: Used storage pool name from datastore
    :rtype: str
    """
    storage_pool = 'DfltStorPool'
    rsc_grp_name = datastore.linstor_resource_group
    if rsc_grp_name:
        rsc_grp_resp = lin.resource_group_list_raise(filter_by_resource_groups=[rsc_grp_name])
        if rsc_grp_resp.resource_groups:
            rsc_grp_data = rsc_grp_resp.resource_groups[0]
            storage_pool = rsc_grp_data.select_filter.storage_pool \
                if rsc_grp_data.select_filter.storage_pool else datastore.storage_pool
    else:
        storage_pool = datastore.storage_pool

    return storage_pool


def resize_disk(resource, target_vm, disk_id, new_size):
    """

    :param Resource resource:
    :param vm.Vm target_vm:
    :param str disk_id:
    :param int new_size: new size in mega bytes
    :return:
    """
    util.log_info("Resizing resource {r} new size: {s}MiB".format(r=resource.name, s=new_size))
    resource.volumes[0].size = SizeCalc.convert(new_size, SizeCalc.UNIT_MiB, SizeCalc.UNIT_B)

    resize_if_qcow2(resource, target_vm, disk_id, new_size)


def resize_if_qcow2(resource, target_vm, disk_id, new_size):
    """
    Resize the qcow2 image if it is one, otherwise noop.

    :param Resource resource:
    :param vm.Vm target_vm:
    :param str disk_id:
    :param int new_size: new size in mega bytes
    :return:
    """
    image_id = target_vm.disk_image_id(disk_id)
    if image_id:
        image_data = Image(util.show_image(image_id))
        fmt = image_data.format
        driver = image_data.template_driver
    else:
        fmt = target_vm.disk_format(disk_id)
        driver = target_vm.disk_driver(disk_id)
    if fmt == "qcow2" or driver == "qcow2":
        primary_node = get_in_use_node(resource)
        resize_node = primary_node if primary_node else resource.diskful_nodes()[0]
        rc, err = util.ssh_exec_and_log_with_err(
            host=resize_node,
            cmd="$QEMU_IMG resize {p} {s}M".format(p=get_device_path(resource), s=new_size),
            error_msg="Error qemu resize image {p}".format(p=get_device_path(resource)))
        if rc != 0:
            raise RuntimeError("Error qemu resize image {p}: {o}".format(
                p=get_device_path(resource),
                o=err))
