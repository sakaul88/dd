class IP(object):
    def __init__(self, id, ip_json):
        self.id = id
        self.subnet_id = ip_json['subnetId']
        self.address = ip_json['ipAddress']
        self.note = ip_json.get('note', '')
        self.network = ip_json.get('isNetwork', False)
        self.broadcast = ip_json.get('isBroadcast', False)
        self.gateway = ip_json.get('isGateway', False)
        self.reserved = ip_json.get('isReserved', False)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def subnet_id(self):
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, subnet_id):
        self._subnet_id = subnet_id

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, note):
        self._note = note

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, network):
        self._network = network

    @property
    def broadcast(self):
        return self._broadcast

    @broadcast.setter
    def broadcast(self, broadcast):
        self._broadcast = broadcast

    @property
    def gateway(self):
        return self._gateway

    @gateway.setter
    def gateway(self, gateway):
        self._gateway = gateway

    @property
    def reserved(self):
        return self._reserved

    @reserved.setter
    def reserved(self, reserved):
        self._reserved = reserved

    def __eq__(self, ip):
        for name, type in vars(IP).items():
            if isinstance(type, property) and getattr(self, name) != getattr(ip, name):
                return False
        return True
