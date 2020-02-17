class KPKey(object):
    def __init__(self, instance_json):
        self.id = instance_json['id']
        self.name = instance_json['name']
        self.type = instance_json['type']
        self.extractable = instance_json['extractable']
        self.state = instance_json['state']
        self.crn = instance_json['crn']

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
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def extractable(self):
        return self._extractable

    @extractable.setter
    def extractable(self, extractable):
        self._extractable = extractable

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def crn(self):
        return self._crn

    @crn.setter
    def crn(self, crn):
        self._crn = crn

    @classmethod
    def parse_kp_keys(self, keys_json):
        """
        Helper method to parse a list of KPKey dictionaries.
        This method simply iterates over the list, instantiating a KPKey object for each dictionary.
        Args:
            keys_json: A list of KPKey dictionaries from the ibmcloud cli
        Returns: A list of KPKey objects
        """
        keys = []
        for key_json in keys_json:
            keys.append(KPKey(key_json))
        return keys
