import logging
import os
import SoftLayer
import yaml
from functools import wraps

from orchutils.slmodels.ip import IP
from orchutils.slmodels.subnet import Subnet

logger = logging.getLogger(__name__)
credentials_file = '/root/.ibmcloud/credentials'
client = None
dns_manager = None
network_manager = None


def login(sl_username, sl_api_key):
    """
    Logs into SoftLayer, instantiating the long-lived client objects.
    This can either be called directly or you can rely on the ensure_clients decorator if the credentials are passed via environment variables or files.
    """
    global client, dns_manager, network_manager
    logger.info('Creating SoftLayer client objects')
    client = SoftLayer.create_client_from_env(username=sl_username, api_key=sl_api_key)
    dns_manager = SoftLayer.managers.dns.DNSManager(client)
    network_manager = SoftLayer.managers.network.NetworkManager(client)


def ensure_clients(f):
    """
    Ensures that the SoftLayer client objects have been initialised.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        global client, network_manager
        sl_username = sl_api_key = None
        if client is None:
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as fh:
                    credentials = yaml.safe_load(fh)
                    sl_username = credentials.get('sl_username')
                    sl_api_key = credentials.get('sl_api_key')
            else:
                sl_username = os.environ.get('SL_USERNAME')
                sl_api_key = os.environ.get('SL_API_KEY')
            if not sl_username or not sl_api_key:
                raise Exception('Not logged into SoftLayer and unable to discover SoftLayer credentials')
            login(sl_username, sl_api_key)
        return f(*args, **kwargs)
    return decorated


@ensure_clients
def create_dns_record(zone_id, record_hostname, data, record_type='CNAME', ttl=86400):
    """
    Creates a domain name record of a given type.
    If the record already exists, with both the same hostname and data value, nothing will be done.
    If the hostname exists but with a different data value, an additional record will be created.
    Args:
        zone_id: The ID of the hosted zone in SoftLayer where the record will be created
        record_hostname: The DNS record to create in the hosted zone
        data: The value of the DNS record
        record_type: The type of the DNS record, for example, CNAME (Optional, default: CNAME)
        ttl: TTL to associate with the record (Optional, default: 86400)
    Returns: The ID of the record created or discovered
    """
    zone_records = dns_manager.get_records(zone_id, record_type=record_type)
    for record in zone_records:
        if record['host'] == record_hostname and record['data'] == data:
            logger.info('"{type}" record host "{host}" with data "{data}" already exists'.format(type=record_type, host=record_hostname, data=data))
            return record['id']
    logger.info('Creating new "{type}" record with host "{host}" and data "{data}"'.format(type=record_type, host=record_hostname, data=data))
    return dns_manager.create_record(zone_id, record_hostname, record_type, data, ttl)['id']


@ensure_clients
def delete_dns_record(zone_id, record_hostname, record_type='CNAME'):
    """
    Deletes a domain name record of a given type.
    Args:
        zone_id: The ID of the hosted zone in SoftLayer where the record will be removed from
        record: The DNS record to remove from the hosted zone
        record_type: The type of the DNS record, for example, CNAME (Optional, default: CNAME)
    """
    zone_records = dns_manager.get_records(zone_id, record_type=record_type)
    for record in zone_records:
        if record['host'] == record_hostname:
            dns_manager.delete_record(record['id'])
            logger.info('Record {record} deleted'.format(record=record_hostname))
            # We will continue to loop as there can be multiple records


@ensure_clients
def get_hosted_zone_id(zone_name):
    """
    Gets the ID of a DNS hosted zone ID (top level domain) from SoftLayer.
    Args:
        zone_name: The name of the zone to retrieve
    Returns: The ID associated to the requested zone or None if it cannot be found
    """
    logger.info('Retrieving ID of hosted zone "{zone}"'.format(zone=zone_name))
    zone_id = None
    for zone in dns_manager.list_zones():
        if zone['name'] == zone_name:
            zone_id = zone['id']
            break
    return zone_id


@ensure_clients
def get_subnet(subnet_id):
    """
    Retrieves a subnet from SoftLayer. IPs in the subnet are subdivided into available and unused IPs.
    Available IPs are identified by not having a note attribute set.
    Unused are other IPs that are also not flagged as network, broadcast, gateway and reserved.
    Args:
        subnet_id: The ID of the subnet to lookup
    Returns: orchutils.slmodels.subnet.Subnet
    """
    logger.info('Retrieving contents of subnet "{subnet_id}"'.format(subnet_id=subnet_id))
    subnet_json = network_manager.get_subnet(subnet_id, mask='mask[id,ipAddresses,networkIdentifier,cidr,networkVlanId]')
    return Subnet(subnet_id, subnet_json)


@ensure_clients
def update_note(ip, ensure_empty=True):
    """
    Update the note for an IP, typically indicating its hostname.
    Network, broadcast, gateways and reserved IP cannot be updated via this method. An exception will be raised if the IP is unavailable.
    Args:
        ip: The IP to assign with the note correctly set. This is of type orchutils.slmodels.ip.IP
        ensure_empty: The IP can bet checked to ensure it also does not currently have a note assigned. (Optional, default: True)
    """
    ip_json = client.call('SoftLayer_Network_Subnet_IpAddress', 'getObject', id=ip.id)
    old_ip = IP(ip.id, ip_json)
    if not old_ip.network and not old_ip.broadcast and not old_ip.gateway and not old_ip.reserved and (
            not ensure_empty or not old_ip.note):
        logger.info('Assigning note "{note}" to ip "{ip}"'.format(note=ip.note, ip=ip.address))
        client.call('SoftLayer_Network_Subnet_IpAddress', 'editObject', {'id': ip.id, 'note': ip.note}, id=ip.id)
    else:
        raise Exception('IP "{ip}" is not available for assignment'.format(ip=ip.address))
