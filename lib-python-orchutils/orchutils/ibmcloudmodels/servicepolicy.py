from orchutils.ibmcloudmodels.resource import Resource
from orchutils.ibmcloudmodels.role import Role
from orchutils.ibmcloudmodels.subject import Subject


class ServicePolicy(object):
    def __init__(self, policy_json):
        self.id = policy_json['id']
        self.type = policy_json['type']
        self.subjects = Subject.parse_subjects(policy_json['subjects'])
        self.roles = Role.parse_roles(policy_json['roles'])
        self.resources = Resource.parse_resources(policy_json['resources'])

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def subjects(self):
        return self._subjects

    @subjects.setter
    def subjects(self, subjects):
        self._subjects = subjects

    @property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, roles):
        self._roles = roles

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, resources):
        self._resources = resources

    @classmethod
    def parse_service_policies(self, policies_json):
        """
        Helper method to parse a list of ServicePolicy dictionaries.
        This method simply iterates over the list, instantiating a ServicePolicy object for each dictionary.
        Args:
            policies_json: A list of ServicePolicy dictionaries from the ibmcloud cli
        Returns: A list of ServicePolicy objects
        """
        policies = []
        for policy_json in policies_json:
            policies.append(ServicePolicy(policy_json))
        return policies

    def to_json(self):
        """
        Converts the instance into a JSON dictionary.
        However, the json is defined as per needed by ibmcloud cli update commands and will not include everything. The ID, for example, is not included.
        """
        return {
            'type': self.type,
            'subjects': self.subjects,
            'roles': self.roles,
            'resources': self.resources,
        }
