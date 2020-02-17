import unittest

from orchutils.ibmcloudmodels.albcertificate import ALBCertificate

alb_certificates_json = [
    {
        'secretName': 'console-p2paas-console-ui',
        'clusterID': '86055afa038f4472a3db265d306472de',
        'domainName': 'console.platform-hub-wdc.np.wce.ibm.com',
        'cloudCertInstanceID': '',
        'clusterCrn': '',
        'certCrn': 'crn:v1:bluemix:public:cloudcerts:us-south:a/69a92444d0c448d994ceb2f517b2fd39:21f25d57-2d21-46bf-ba3c-e73e37ffd6da:certificate:8737840436966e4e45eef7491c45d830',
        'issuerName': 'International Business Machines Corporation IBM INTERNAL INTERMEDIATE CA',
        'expiresOn': '1642049999000',
        'state': 'updated'
    }
]


class TestALBCertificate(unittest.TestCase):
    def test_constructor(self):
        alb_certificate_json = alb_certificates_json[0]
        alb_certificate = ALBCertificate(alb_certificate_json)
        self.assertEqual(alb_certificate_json['secretName'], alb_certificate.secret_name)
        self.assertEqual(alb_certificate_json['clusterID'], alb_certificate.cluster_id)
        self.assertEqual(alb_certificate_json['domainName'], alb_certificate.domain_name)
        self.assertEqual(alb_certificate_json['certCrn'], alb_certificate.cert_crn)
        self.assertEqual(alb_certificate_json['issuerName'], alb_certificate.issuer_name)
        self.assertEqual(alb_certificate_json['expiresOn'], alb_certificate.expires_on)
        self.assertEqual(alb_certificate_json['state'], alb_certificate.state)

    def test_properties(self):
        alb_certificate = ALBCertificate(alb_certificates_json[0])
        self.assertEqual('console-p2paas-console-ui', alb_certificate.secret_name)
        alb_certificate.secret_name = 'secretname'
        self.assertEqual('secretname', alb_certificate.secret_name)
        alb_certificate.cluster_id = 'cluster_id'
        self.assertEqual('cluster_id', alb_certificate.cluster_id)
        alb_certificate.domain_name = 'domain_name'
        self.assertEqual('domain_name', alb_certificate.domain_name)
        alb_certificate.cert_crn = 'cert_crn'
        self.assertEqual('cert_crn', alb_certificate.cert_crn)
        alb_certificate.issuer_name = 'issuer_name'
        self.assertEqual('issuer_name', alb_certificate.issuer_name)
        alb_certificate.expires_on = '100'
        self.assertEqual('100', alb_certificate.expires_on)
        alb_certificate.state = 'state'
        self.assertEqual('state', alb_certificate.state)

    def test_parse_alb_certificates(self):
        alb_certificates = ALBCertificate.parse_alb_certificates(alb_certificates_json)
        self.assertEqual(1, len(alb_certificates))
        self.assertEqual('console-p2paas-console-ui', alb_certificates[0].secret_name)


if __name__ == '__main__':
    unittest.main()
