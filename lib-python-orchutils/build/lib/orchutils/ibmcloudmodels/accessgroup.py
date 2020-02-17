class AccessGroup(object):
    def __init__(self, access_group_json):
        self.group_id = access_group_json['id']
        self.name = access_group_json['name']

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @classmethod
    def parse_access_groups(self, access_groups_json):
        """
        Helper method to parse a list of access groups dictionaries.
        This method simply iterates over the list, instantiating an acces group object for each dictionary.
        Args:
            access_groups_json: A list of access group dictionaries from the ibmcloud cli
        Returns: A list of AccessGroup objects
        """
        access_groups = []
        for access_group_json in access_groups_json:
            access_groups.append(AccessGroup(access_group_json))
        return access_groups
