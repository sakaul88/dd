class UserResourceGroup(object):
    def __init__(self, user_resource_group_json):
        self.email = user_resource_group_json['user_email']
        self.access_level = user_resource_group_json['access_level']
        self.group_id = user_resource_group_json['group_id']
        self.group_name = user_resource_group_json['group_name']

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

    @property
    def access_level(self):
        return self._access_level

    @access_level.setter
    def access_level(self, access_level):
        self._access_level = access_level

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id

    @property
    def group_name(self):
        return self._group_name

    @group_name.setter
    def group_name(self, group_name):
        self._group_name = group_name

    @classmethod
    def parse_user_resource_group(self, user_resource_group_json):
        """
        Helper method to parse a list of a users resource group dictionaries.
        This method simply iterates over the list, instantiating an acces group object for each dictionary.
        Args:
            user_resource_groups_json: A list of users resource group dictionaries from the ibmcloud cli
        Returns: A list of UserResourceGroup objects
        """
        user_resource_groups = []
        for user_resource_group in user_resource_group_json:
            user_resource_groups.append(UserResourceGroup(user_resource_group))
        return user_resource_groups
