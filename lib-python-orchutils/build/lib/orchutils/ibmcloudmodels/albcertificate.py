class ALBCertificate(object):
    def __init__(self, alb_certificate_json):
        self.secret_name = alb_certificate_json['secretName']
        self.cluster_id = alb_certificate_json['clusterID']
        self.domain_name = alb_certificate_json['domainName']
        self.cert_crn = alb_certificate_json['certCrn']
        self.issuer_name = alb_certificate_json['issuerName']
        self.expires_on = alb_certificate_json['expiresOn']
        self.state = alb_certificate_json['state']

    @property
    def secret_name(self):
        return self._secret_name

    @secret_name.setter
    def secret_name(self, secret_name):
        self._secret_name = secret_name

    @property
    def cluster_id(self):
        return self._cluster_id

    @cluster_id.setter
    def cluster_id(self, cluster_id):
        self._cluster_id = cluster_id

    @property
    def domain_name(self):
        return self._domain_name

    @domain_name.setter
    def domain_name(self, domain_name):
        self._domain_name = domain_name

    @property
    def cert_crn(self):
        return self._cert_crn

    @cert_crn.setter
    def cert_crn(self, cert_crn):
        self._cert_crn = cert_crn

    @property
    def issuer_name(self):
        return self._issuer_name

    @issuer_name.setter
    def issuer_name(self, issuer_name):
        self._issuer_name = issuer_name

    @property
    def expires_on(self):
        return self._expires_on

    @expires_on.setter
    def expires_on(self, expires_on):
        self._expires_on = expires_on

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @classmethod
    def parse_alb_certificates(self, alb_certificates_json):
        """
        Helper method to parse a list of ALB certificate dictionaries.
        This method simply iterates over the list, instantiating an ALB certificate object for each dictionary.
        Args:
            alb_certificates_json: A list of ALB certificate dictionaries from the ibmcloud cli
        Returns: A list of ALBCertificate objects
        """
        alb_certificates = []
        for alb_certificate_json in alb_certificates_json:
            alb_certificates.append(ALBCertificate(alb_certificate_json))
        return alb_certificates
