class ResourceGroup(object):
    def __init__(self, resource_group_json):
        self.id = resource_group_json['id']
        self.account_id = resource_group_json['account_id']
        self.name = resource_group_json['name']
        self.default = resource_group_json['default']
        self.state = resource_group_json['state']
        self.created_at = resource_group_json['created_at']
        self.updated_at = resource_group_json['updated_at']

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def account_id(self):
        return self._account_id

    @account_id.setter
    def account_id(self, account_id):
        self._account_id = account_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, default):
        self._default = default

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        self._created_at = created_at

    @property
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        self._updated_at = updated_at

    @classmethod
    def parse_resource_groups(self, resource_groups_json):
        """
        Helper method to parse a list of resource groups dictionaries.
        This method simply iterates over the list, instantiating a resource group object for each dictionary.
        Args:
            resource_groups_json: A list of resource group dictionaries from the ibmcloud cli
        Returns: A list of ResourceGroup objects
        """
        resource_groups = []
        for resource_group_json in resource_groups_json:
            resource_groups.append(ResourceGroup(resource_group_json))
        return resource_groups
