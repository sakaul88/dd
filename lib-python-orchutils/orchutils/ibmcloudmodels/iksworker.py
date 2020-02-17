class IKSWorker(object):
    def __init__(self, worker_json):
        self.id = worker_json['id']
        self.state = worker_json['state']
        self.status = worker_json['status']
        self.private_ip = worker_json['privateIP']
        self.public_ip = worker_json['publicIP']
        self.machine_type = worker_json['machineType']
        self.location = worker_json['location']
        self.pool_name = worker_json['poolName']
        self.kube_version = worker_json['kubeVersion']
        self.target_version = worker_json['targetVersion']
        self.pending_operation = worker_json['pendingOperation']

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def private_ip(self):
        return self._private_ip

    @private_ip.setter
    def private_ip(self, private_ip):
        self._private_ip = private_ip

    @property
    def public_ip(self):
        return self._public_ip

    @public_ip.setter
    def public_ip(self, public_ip):
        self._public_ip = public_ip

    @property
    def machine_type(self):
        return self._machine_type

    @machine_type.setter
    def machine_type(self, machine_type):
        self._machine_type = machine_type

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    def pool_name(self):
        return self._pool_name

    @pool_name.setter
    def pool_name(self, pool_name):
        self._pool_name = pool_name

    @property
    def kube_version(self):
        return self._kube_version

    @kube_version.setter
    def kube_version(self, kube_version):
        self._kube_version = kube_version

    @property
    def target_version(self):
        return self._target_version

    @target_version.setter
    def target_version(self, target_version):
        self._target_version = target_version

    @property
    def pending_operation(self):
        return self._pending_operation

    @pending_operation.setter
    def pending_operation(self, pending_operation):
        self._pending_operation = pending_operation

    @classmethod
    def parse_iks_workers(self, workers_json):
        """
        Helper method to parse a list of IKS worker dictionaries.
        This method simply iterates over the list, instantiating an IKS worker object for each dictionary.
        Args:
            workers_json: A list of IKS worker dictionaries from the ibmcloud cli
        Returns: A list of IKSWorker objects
        """
        workers = []
        for worker_json in workers_json:
            workers.append(IKSWorker(worker_json))
        return workers
