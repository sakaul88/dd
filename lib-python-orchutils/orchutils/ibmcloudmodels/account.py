class Account(object):
    def __init__(self, user_json):
        self.guid = user_json['guid']
        self.name = user_json['name']
        self.owner = user_json['owner']

    @property
    def guid(self):
        return self._guid

    @guid.setter
    def guid(self, guid):
        self._guid = guid

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner
