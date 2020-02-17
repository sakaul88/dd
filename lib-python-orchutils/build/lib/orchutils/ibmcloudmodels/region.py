class Region(object):
    def __init__(self, region_json):
        self.mccp_id = region_json['mccp_id']
        self.name = region_json['name']

    @property
    def mccp_id(self):
        return self._mccp_id

    @mccp_id.setter
    def mccp_id(self, mccp_id):
        self._mccp_id = mccp_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
