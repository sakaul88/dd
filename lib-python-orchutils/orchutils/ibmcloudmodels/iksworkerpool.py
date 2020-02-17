from orchutils.ibmcloudmodels.zone import Zone


class IKSWorkerPool(object):
    def __init__(self, worker_pool_json):
        self.id = worker_pool_json['id']
        self.name = worker_pool_json['name']
        self.size_per_zone = worker_pool_json['sizePerZone']
        self.isolation = worker_pool_json['isolation']
        self.labels = worker_pool_json['labels']
        self.machine_type = worker_pool_json['machineType']
        self.region = worker_pool_json['region']
        self.state = worker_pool_json['state']
        self.reason_for_delete = worker_pool_json['reasonForDelete']
        self.is_balanced = worker_pool_json['isBalanced']
        self.autoscale_enabled = worker_pool_json['autoscaleEnabled']
        self.zones = Zone.parse_zones(worker_pool_json['zones'])

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
    def size_per_zone(self):
        return self._size_per_zone

    @size_per_zone.setter
    def size_per_zone(self, size_per_zone):
        self._size_per_zone = size_per_zone

    @property
    def isolation(self):
        return self._isolation

    @isolation.setter
    def isolation(self, isolation):
        self._isolation = isolation

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels

    @property
    def machine_type(self):
        return self._machine_type

    @machine_type.setter
    def machine_type(self, machine_type):
        self._machine_type = machine_type

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def reason_for_delete(self):
        return self._reason_for_delete

    @reason_for_delete.setter
    def reason_for_delete(self, reason_for_delete):
        self._reason_for_delete = reason_for_delete

    @property
    def is_balanced(self):
        return self._is_balanced

    @is_balanced.setter
    def is_balanced(self, is_balanced):
        self._is_balanced = is_balanced

    @property
    def autoscale_enabled(self):
        return self._autoscale_enabled

    @autoscale_enabled.setter
    def autoscale_enabled(self, autoscale_enabled):
        self._autoscale_enabled = autoscale_enabled

    @property
    def zones(self):
        return self._zones

    @zones.setter
    def zones(self, zones):
        self._zones = zones

    @classmethod
    def parse_iks_worker_pools(self, worker_pools_json):
        """
        Helper method to parse a list of IKS worker pool dictionaries.
        This method simply iterates over the list, instantiating an IKS worker pool object for each dictionary.
        Args:
            worker_pools_json: A list of IKS worker pool dictionaries from the ibmcloud cli
        Returns: A list of IKSWorkerPool objects
        """
        worker_pools = []
        for worker_pool_json in worker_pools_json:
            worker_pools.append(IKSWorkerPool(worker_pool_json))
        return worker_pools
