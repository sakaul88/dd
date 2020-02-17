class Role(object):
    def __init__(self, role_json):
        self.id = role_json['role_id']
        self.display_name = role_json['display_name']
        self.description = role_json['description']

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        self._display_name = display_name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @classmethod
    def parse_roles(self, roles_json):
        """
        Helper method to parse a list of Attribute dictionaries.
        This method simply iterates over the list, instantiating an Attribute object for each dictionary.
        Args:
            roles_json: A list of Attribute dictionaries from the ibmcloud cli
        Returns: A list of Attribute objects
        """
        roles = []
        for role_json in roles_json:
            roles.append(Role(role_json))
        return roles

    def to_json(self):
        """
        Converts the instance into a JSON dictionary.
        However, the json is defined as per needed by ibmcloud cli update commands and will not include everything. The display_name, for example, is not included.
        """
        return {
            'role_id': self.id
        }
