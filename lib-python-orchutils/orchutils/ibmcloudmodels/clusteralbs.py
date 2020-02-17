from orchutils.ibmcloudmodels.alb import ALB


class ClusterALBs(object):
    def __init__(self, clusteralbs_json):
        self.id = clusteralbs_json['id']
        self.region = clusteralbs_json['region']
        self.ingress_hostname = clusteralbs_json['ingressHostname']
        self.ingress_secretname = clusteralbs_json['ingressSecretName']
        self.albs = []
        for alb_json in clusteralbs_json['alb']:
            self.albs.append(ALB(alb_json))

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region

    @property
    def ingress_hostname(self):
        return self._ingress_hostname

    @ingress_hostname.setter
    def ingress_hostname(self, ingress_hostname):
        self._ingress_hostname = ingress_hostname

    @property
    def ingress_hostname(self):
        return self._ingress_hostname

    @ingress_hostname.setter
    def ingress_hostname(self, ingress_hostname):
        self._ingress_hostname = ingress_hostname

    @property
    def albs(self):
        return self._albs

    @albs.setter
    def albs(self, albs):
        self._albs = albs
