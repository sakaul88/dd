import datetime
import six


class IKSCluster(object):
    def __init__(self, cluster_json):
        self.id = cluster_json['id']
        self.name = cluster_json['name']
        self.region = cluster_json['region']
        self.zones = cluster_json['workerZones']
        self.resource_group_name = cluster_json['resourceGroupName']
        self.resource_group_id = cluster_json['resourceGroup']
        self.master_kube_version = cluster_json['masterKubeVersion']
        self.target_version = cluster_json['targetVersion']
        self.master_status = cluster_json['masterStatus']
        self.key_protect_enabled = cluster_json['keyProtectEnabled']
        self.pull_secret_applied = cluster_json['pullSecretApplied']
        self.created_date = cluster_json['createdDate']

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
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region

    @property
    def zones(self):
        return self._zones

    @zones.setter
    def zones(self, zones):
        self._zones = zones

    @property
    def resource_group_name(self):
        return self._resource_group_name

    @resource_group_name.setter
    def resource_group_name(self, resource_group_name):
        self._resource_group_name = resource_group_name

    @property
    def resource_group_id(self):
        return self._resource_group_id

    @resource_group_id.setter
    def resource_group_id(self, resource_group_id):
        self._resource_group_id = resource_group_id

    @property
    def master_kube_version(self):
        return self._master_kube_version

    @master_kube_version.setter
    def master_kube_version(self, master_kube_version):
        self._master_kube_version = master_kube_version

    @property
    def target_version(self):
        return self._target_version

    @target_version.setter
    def target_version(self, target_version):
        self._target_version = target_version

    @property
    def master_status(self):
        return self._master_status

    @master_status.setter
    def master_status(self, master_status):
        self._master_status = master_status

    @property
    def key_protect_enabled(self):
        return self._key_protect_enabled

    @key_protect_enabled.setter
    def key_protect_enabled(self, key_protect_enabled):
        self._key_protect_enabled = key_protect_enabled

    @property
    def pull_secret_applied(self):
        return self._pull_secret_applied

    @pull_secret_applied.setter
    def pull_secret_applied(self, pull_secret_applied):
        self._pull_secret_applied = pull_secret_applied

    @property
    def created_date(self):
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        if isinstance(created_date, six.string_types):
            self._created_date = datetime.datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S+0000')
        else:
            self._created_date = created_date

    @classmethod
    def parse_iks_clusters(self, clusters_json):
        """
        Helper method to parse a list of IKS cluster dictionaries.
        This method simply iterates over the list, instantiating an IKS cluster object for each dictionary.
        Args:
            clusters_json: A list of IKS cluster dictionaries from the ibmcloud cli
        Returns: A list of IKSCluster objects
        """
        clusters = []
        for cluster_json in clusters_json:
            clusters.append(IKSCluster(cluster_json))
        return clusters
