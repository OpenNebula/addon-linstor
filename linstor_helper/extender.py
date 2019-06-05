import time

from linstor import Resource, Volume, MultiLinstor, LinstorError
from one import util, consts
from one.vm import Vm


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
    storage_pool_total_MiB = 0
    storage_pool_free_MiB = 0
    if nodes:
        lowest_free_node = nodes[0]
        for node in nodes:
            if free_space_by_node[node].total_capacity < free_space_by_node[node].total_capacity:
                lowest_free_node = node
        storage_pool_total_MiB += free_space_by_node[lowest_free_node].total_capacity // 1024
        storage_pool_free_MiB += free_space_by_node[lowest_free_node].free_capacity // 1024
    else:
        for space_info in free_space_by_node.values():
            storage_pool_total_MiB += (space_info.total_capacity // int(auto_place)) // 1024
            storage_pool_free_MiB += (space_info.free_capacity // int(auto_place)) // 1024

    return storage_pool_total_MiB - storage_pool_free_MiB, storage_pool_total_MiB, storage_pool_free_MiB


def deploy(resource, deployment_nodes, auto_place_count):
    """
    Deploys resource depending on deployment nodes or auto_place setting.

    :param Resource resource:
    :param str deployment_nodes:
    :param int auto_place_count:
    :return:
    """
    if deployment_nodes:
        for node in deployment_nodes.split(" "):
            resource.diskful(node)
    elif auto_place_count:
        resource.placement.redundancy = auto_place_count
        resource.autoplace()
    else:
        raise RuntimeError("No deploy mode selected. nodes: {n}, auto_place: {a}".format(
            n=deployment_nodes, a=auto_place_count)
        )


def delete(resource_name, uri_list):
    """
    Deletes a resource with all it's snapshots

    :param str resource_name: name of the resource
    :param str uris: linstor uris string
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
    :rtype: bool
    """
    with MultiLinstor(resource.client.uri_list) as lin:
        lst = lin.resource_list(filter_by_resources=[resource.name])
        if lst:
            nodes = [x for x in lst[0].resource_states if x.in_use]
            if nodes:
                return nodes[0].node_name
    return None


def clone(resource, clone_name, place_nodes, auto_place_count, mode=CloneMode.SNAPSHOT):
    """
    Clones a resource to a new resource.

    :param Resource resource: resource object to clone
    :param str clone_name: name of the new resource
    :param str place_nodes: deployment nodes string, e.g. "alpha bravo charly"
    :param int auto_place_count:
    :param int mode:
    :return: True if clone was successful
    :rtype: bool
    """
    return_code = 0
    util.log_info("Cloning from resource '{src}' to '{tgt}'.".format(src=resource.name, tgt=clone_name))
    if mode == CloneMode.SNAPSHOT:
        snap_name = "for-" + clone_name
        resource.snapshot_create(snap_name)
        resource.restore_from_snapshot(snap_name, clone_name)
        time.sleep(1)  # wait a second for deletion, here is a potential race condition
        resource.snapshot_delete(snap_name)
    elif mode == CloneMode.COPY:
        clone_res = Resource(
            name=clone_name,
            uri=",".join(resource.client.uri_list)
        )
        clone_res.placement.storage_pool = resource.volumes[0].storage_pool_name
        clone_res.volumes[0] = Volume(str(resource.volumes[0].size))
        deploy(clone_res, place_nodes, auto_place_count)

        # use copy source on the current primary node or on one with a disk, if all secondary
        copy_node = get_in_use_node(resource)
        if copy_node is None:
            nodes = resource.diskful_nodes()
            copy_node = nodes[0]
        clone_res.activate(copy_node)

        from_dev_path = get_device_path(resource)
        to_dev_path = get_device_path(clone_res)

        block_count = int(resource.volumes[0].size) // 1024 / 64 + 1

        conv_opts = ["sync"]
        if clone_res.is_thin():
            conv_opts.append("sparse")

        dd_cmd = '"dd if={_if} of={_of} bs=64K count={c} conv={conv}"'.format(
            _if=from_dev_path,
            _of=to_dev_path,
            c=block_count,
            conv=",".join(conv_opts)
        )
        # dd on the node
        return_code = util.ssh_exec_and_log(
            " ".join([
                '"{}"'.format(copy_node),
                dd_cmd,
                '"error copying image data from {_if} to {_of}"'.format(_if=from_dev_path, _of=to_dev_path)
            ])
        )

        time.sleep(0.5)  # wait a bit until we are sure dd closed the block device

        clone_res.deactivate(copy_node)

    return return_code == 0


def get_rsc_name(target_vm, disk_id):
    """
    Tries to detect the correct resource name.

    :param Vm target_vm: Vm object
    :param int disk_id: Id of the disk vm
    :return: The linstor resource name
    :rtype: str
    """
    res_name = None
    disk_source = target_vm.disk_source(disk_id)
    if not disk_source:  # volatile
        res_name = consts.VOLATILE_PREFIX + "-vm{}-disk{}".format(target_vm.ID, disk_id)
    else:
        res_name = target_vm.disk_source(disk_id)

        if not target_vm.disk_persistent(disk_id):
            if target_vm.disk_type(disk_id) == "CDROM":
                util.log_info("{} is a non-persistent CDROM image".format(res_name))
            else:
                res_name = "{}-vm{}-disk{}".format(res_name, target_vm.ID, disk_id)
                util.log_info(
                    "{} is a non-persistent OS or DATABLOCK image".format(res_name)
                )
        else:
            util.log_info("{} is a persistent OS or DATABLOCK image".format(res_name))

    return res_name


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
