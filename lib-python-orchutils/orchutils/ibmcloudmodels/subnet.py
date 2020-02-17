class Subnet(object):
    def __init__(self, subnet_json):
        self.id = subnet_json['id']
        self.type = subnet_json['type']
        self.vlan_id = subnet_json['vlan_id']
        properties = subnet_json.get('properties', {})
        self.bound_cluster = properties.get('bound_cluster')
        self.note = properties.get('note')

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def vlan_id(self):
        return self._vlan_id

    @vlan_id.setter
    def vlan_id(self, vlan_id):
        self._vlan_id = vlan_id

    @property
    def bound_cluster(self):
        return self._bound_cluster

    @bound_cluster.setter
    def bound_cluster(self, bound_cluster):
        self._bound_cluster = bound_cluster

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, note):
        self._note = note

    @classmethod
    def parse_subnets(self, subnets_json):
        """
        Helper method to parse a list of subnet dictionaries.
        This method simply iterates over the list, instantiating a Subnet object for each dictionary.
        Args:
            subnets_json: A list of subnet dictionaries from the ibmcloud cli
        Returns: A list of Subnet objects
        """
        subnets = []
        for subnet_json in subnets_json:
            subnets.append(Subnet(subnet_json))
        return subnets
