class ServiceKey(object):
    def __init__(self, key_json):
        self.id = key_json['id']
        self.name = key_json['name']
        self.resource_group_id = key_json['resource_group_id']
        self.source_crn = key_json['source_crn']
        self.crn = key_json['crn']
        self.state = key_json['state']
        self.credentials = key_json.get('credentials')

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def resource_group_id(self):
        return self._resource_group_id

    @resource_group_id.setter
    def resource_group_id(self, resource_group_id):
        self._resource_group_id = resource_group_id

    @property
    def source_crn(self):
        return self._source_crn

    @source_crn.setter
    def source_crn(self, source_crn):
        self._source_crn = source_crn

    @property
    def crn(self):
        return self._crn

    @crn.setter
    def crn(self, crn):
        self._crn = crn

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, credentials):
        self._credentials = credentials or {}

    @classmethod
    def parse_service_keys(self, keys_json):
        """
        Helper method to parse a list of ServiceInstance dictionaries.
        This method simply iterates over the list, instantiating an ServiceInstance object for each dictionary.
        Args:
            albs_json: A list of ServiceInstance dictionaries from the ibmcloud cli
        Returns: A list of ServiceInstance objects
        """
        keys = []
        for key_json in keys_json:
            keys.append(ServiceKey(key_json))
        return keys
