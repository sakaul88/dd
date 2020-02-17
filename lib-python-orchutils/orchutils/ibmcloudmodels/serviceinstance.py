class ServiceInstance(object):
    def __init__(self, instance_json):
        self.id = instance_json['id']
        self.guid = instance_json['guid']
        self.name = instance_json['name']
        self.location = instance_json['region_id']
        self.resource_plan_id = instance_json['resource_plan_id']
        self.resource_group_id = instance_json['resource_group_id']
        self.crn = instance_json['crn']
        self.parameters = instance_json.get('parameters', {})
        self.state = instance_json['state']

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

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
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    def resource_plan_id(self):
        return self._resource_plan_id

    @resource_plan_id.setter
    def resource_plan_id(self, resource_plan_id):
        self._resource_plan_id = resource_plan_id

    @property
    def resource_group_id(self):
        return self._resource_group_id

    @resource_group_id.setter
    def resource_group_id(self, resource_group_id):
        self._resource_group_id = resource_group_id

    @property
    def crn(self):
        return self._crn

    @crn.setter
    def crn(self, crn):
        self._crn = crn

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        self._parameters = parameters

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @classmethod
    def parse_service_instances(self, instances_json):
        """
        Helper method to parse a list of ServiceInstance dictionaries.
        This method simply iterates over the list, instantiating a ServiceInstance object for each dictionary.
        Args:
            instances_json: A list of ServiceInstance dictionaries from the ibmcloud cli
        Returns: A list of ServiceInstance objects
        """
        instances = []
        for instance_json in instances_json:
            instances.append(ServiceInstance(instance_json))
        return instances
