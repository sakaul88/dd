class ALB(object):
    def __init__(self, alb_json):
        self.id = alb_json['albID']
        self.cluster_id = alb_json['clusterID']
        self.type = alb_json['albType']
        self.enabled = alb_json['enable']
        self.state = alb_json['state']
        self.zone = alb_json['zone']
        self.ip = alb_json['albip']

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def cluster_id(self):
        return self._cluster_id

    @cluster_id.setter
    def cluster_id(self, cluster_id):
        self._cluster_id = cluster_id

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def zone(self):
        return self._zone

    @zone.setter
    def zone(self, zone):
        self._zone = zone

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, ip):
        self._ip = ip
