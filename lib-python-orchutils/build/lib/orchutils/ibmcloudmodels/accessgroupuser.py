class AccessGroupUser(object):
    def __init__(self, access_group_user_json):
        self.id = access_group_user_json['id']
        self.access_type = access_group_user_json['type']

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def access_type(self):
        return self._access_type

    @access_type.setter
    def access_type(self, access_type):
        self._access_type = access_type

    @classmethod
    def parse_access_group_users(self, access_group_users_json):
        """
        Helper method to parse a list of access groups dictionaries.
        This method simply iterates over the list, instantiating an acces group object for each dictionary.
        Args:
            access_group_users_json: A list of access group dictionaries from the ibmcloud cli
        Returns: A list of AccessGroupUser objects
        """
        access_group_users = []
        for access_group_user_json in access_group_users_json:
            access_group_users.append(AccessGroupUser(access_group_user_json))
        return access_group_users
