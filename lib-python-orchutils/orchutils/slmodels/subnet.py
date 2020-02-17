from orchutils.slmodels.ip import IP


class Subnet(object):
    def __init__(self, id, subnet_json):
        self.id = id
        self.cidr = '{identifier}/{mask}'.format(identifier=subnet_json['networkIdentifier'], mask=subnet_json['cidr'])
        self.vlan_id = subnet_json['networkVlanId']
        self.ips = []
        self.ips_available = []
        self.ips_inuse = {}
        for ip_json in subnet_json['ipAddresses']:
            ip = IP(ip_json['id'], ip_json)
            self.ips.append(ip)
            if not ip.network and not ip.broadcast and not ip.gateway and not ip.reserved:
                if ip.note:
                    self.ips_inuse[ip.note] = ip
                else:
                    self.ips_available.append(ip)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def cidr(self):
        return self._cidr

    @cidr.setter
    def cidr(self, cidr):
        self._cidr = cidr

    @property
    def vlan_id(self):
        return self._vlan_id

    @vlan_id.setter
    def vlan_id(self, vlan_id):
        self._vlan_id = vlan_id

    @property
    def ips(self):
        return self._ips

    @ips.setter
    def ips(self, ips):
        self._ips = ips

    @property
    def ips_available(self):
        return self._ips_available

    @ips_available.setter
    def ips_available(self, ips_available):
        self._ips_available = ips_available

    @property
    def ips_inuse(self):
        return self._ips_inuse

    @ips_inuse.setter
    def ips_inuse(self, ips_inuse):
        self._ips_inuse = ips_inuse

    def __eq__(self, subnet):
        return self.id == subnet.id and self.ips == subnet.ips and self.ips_available == subnet.ips_available and self.ips_inuse == subnet.ips_inuse
