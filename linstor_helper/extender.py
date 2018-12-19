import time

from linstor import Resource, Volume, MultiLinstor
from one import util


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
    free_space_by_node = {x.node_name: x.free_space for x in storage_pools.storage_pools}
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


def delete(resource):
    """
    Deletes a resource with all it's snapshots

    :param Resource resource:
    :return: True
    """
    with MultiLinstor(resource.client.uri_list) as lin:
        snapshots = lin.snapshot_dfn_list()[0]
        for snap in [x for x in snapshots.proto_msg.snapshot_dfns if x.rsc_name == resource.name]:
            util.log_info("Deleting snapshot '{r}/{s}'".format(r=resource.name, s=snap.snapshot_name))
            lin.snapshot_delete(rsc_name=resource.name, snapshot_name=snap.snapshot_name)

    util.log_info("Deleting resource '{r}'".format(r=resource.name))
    resource.delete()
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


def clone(resource, clone_name, place_nodes, auto_place_count, mode=CloneMode.SNAPSHOT):
    """

    :param Resource resource:
    :param str clone_name:
    :param place_nodes:
    :param int auto_place_count:
    :param int mode:
    :return:
    """
    return_code = 0
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
        nodes = resource.diskful_nodes()
        copy_node = nodes[0]
        clone_res.activate(copy_node)

        from_dev_path = resource.volumes[0].device_path if resource.volumes[0].device_path \
            else "/dev/drbd{minor}".format(minor=resource.volumes[0].minor)
        to_dev_path = clone_res.volumes[0].device_path if clone_res.volumes[0].device_path \
            else "/dev/drbd{minor}".format(minor=clone_res.volumes[0].minor)

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

        clone_res.deactivate(copy_node)

    return return_code == 0
