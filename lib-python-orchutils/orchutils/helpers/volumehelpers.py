import json

from orchutils import ibmcloud

# CONSTANTS
BLOCK = 'block'
CLUSTER = 'cluster'
FILE = 'file'


def get_volume_list():
    """Gets all file volumes and block volumes from ibmcloud
    Returns:
        List of all ibmcloud volumes
    """
    ibmcloud_file_volume_list = ibmcloud.file_volume_list()
    ibmcloud_block_volume_list = ibmcloud.block_volume_list()
    volume_list = ibmcloud_file_volume_list + ibmcloud_block_volume_list

    return volume_list


def get_iks_volume_list():
    """Gets all file volumes and block volumes from ibmcloud and filters the IKS related ones
    Returns:
        List of all ibmcloud IKS volumes
    """
    volume_list = get_volume_list()
    iks_volume_list = []
    for volume in volume_list:
        volume_notes = get_volume_notes(volume)
        if volume_notes and volume_notes.get(CLUSTER):
            iks_volume_list.append(volume)

    return iks_volume_list


def get_volume_notes(volume):
    """Parse a volume's notes
    Args:
        Volume: volume -> ibmcloud volume to get the notes from
    Returns:
        a python object with the volume notes or an empty object if there are
        no notes or if the are not in JSON format
    """
    try:
        return json.loads(volume.notes)
    except Exception:
        return {}


def separate_volumes_by_type(volumes):
    """Separates volumes by type (file and block)
    Args:
        list[Volume]: volumes -> List of ibmcloud volumes
    Returns:
        A tuple with a list of file volumes and a list of block volumes
    """
    file_volumes = []
    block_volumes = []
    for volume in volumes:
        if volume.volume_type == FILE:
            file_volumes.append(volume)
        if volume.volume_type == BLOCK:
            block_volumes.append(volume)
    return (file_volumes, block_volumes)


def get_volume_orphan_list(cluster_ids, volumes):
    """Filters volumes whose clusters are missing of ibmcloud from a list of volmes (orphaned volumes)
    Args:
        list[str]: cluster_ids -> list of cluster ids
        list[Volume]: volumes -> list of ibmcloud volumes
    Returns:
        List of orphaned volumes
    """
    orphan_list = []
    for volume in volumes:
        volume_notes = get_volume_notes(volume)
        current_volume_notes_cluster_id = volume_notes.get(CLUSTER)
        if current_volume_notes_cluster_id and (current_volume_notes_cluster_id not in cluster_ids):
            orphan_list.append(volume)
    return orphan_list
