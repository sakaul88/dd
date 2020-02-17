class Zone(object):
    def __init__(self, zone_json):
        self.private_vlan = zone_json['privateVlan']
        self.public_vlan = zone_json['publicVlan']
        self.id = zone_json['id']
        self.worker_count = zone_json['workerCount']

    @property
    def private_vlan(self):
        return self._private_vlan

    @private_vlan.setter
    def private_vlan(self, private_vlan):
        self._private_vlan = private_vlan

    @property
    def public_vlan(self):
        return self._public_vlan

    @public_vlan.setter
    def public_vlan(self, public_vlan):
        self._public_vlan = public_vlan

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def worker_count(self):
        return self._worker_count

    @worker_count.setter
    def worker_count(self, worker_count):
        self._worker_count = worker_count

    @classmethod
    def parse_zones(self, zones_json):
        """
        Helper method to parse a list of zone dictionaries.
        This method simply iterates over the list, instantiating a zone object for each dictionary.
        Args:
            zones_json: A list of zone dictionaries from the ibmcloud cli
        Returns: A list of Zone objects
        """
        zones = []
        for zone_json in zones_json:
            zones.append(Zone(zone_json))
        return zones
