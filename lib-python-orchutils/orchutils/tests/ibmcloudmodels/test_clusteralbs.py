import unittest

from orchutils.ibmcloudmodels.clusteralbs import ClusterALBs

clusteralbs_json = {
    'id': 'bm12clsw08k9uctrq8cg',
    'region': 'us-east',
    'dataCenter': 'wdc04',
    'isPaid': True,
    'ingressHostname': 'platform-orchestration.us-east.containers.appdomain.cloud',
    'ingressSecretName': 'platform-orchestration',
    'alb': [
        {
            'albID': 'private-crbm12clsw08k9uctrq8cg-alb1',
            'clusterID': 'bm12clsw08k9uctrq8cg',
            'name': '',
            'albType': 'private',
            'enable': True,
            'state': 'enabled',
            'createdDate': '',
            'numOfInstances': '2',
            'resize': False,
            'albip': '10.183.50.106',
            'zone': 'wdc04',
            'disableDeployment': False,
            'albBuild': '579',
            'authBuild': '341',
            'vlanID': '2342855',
            'status': '',
            'nlbVersion': '1.0'
        },
        {
            'albID': 'public-crbm12clsw08k9uctrq8cg-alb1',
            'clusterID': 'bm12clsw08k9uctrq8cg',
            'name': '',
            'albType': 'public',
            'enable': True,
            'state': 'enabled',
            'createdDate': '',
            'numOfInstances': '2',
            'resize': False,
            'albip': '169.47.145.226',
            'zone': 'wdc04',
            'disableDeployment': False,
            'albBuild': '579',
            'authBuild': '341',
            'vlanID': '2342853',
            'status': '',
            'nlbVersion': '1.0'
        }
    ]
}


class TestClusterALBs(unittest.TestCase):
    def test_constructor(self):
        clusteralbs = ClusterALBs(clusteralbs_json)
        self.assertEqual('bm12clsw08k9uctrq8cg', clusteralbs.id)
        self.assertEqual('us-east', clusteralbs.region)
        self.assertEqual('platform-orchestration.us-east.containers.appdomain.cloud', clusteralbs.ingress_hostname)
        self.assertEqual('platform-orchestration', clusteralbs.ingress_secretname)
        self.assertEqual(2, len(clusteralbs.albs))
        self.assertEqual('private-crbm12clsw08k9uctrq8cg-alb1', clusteralbs.albs[0].id)

    def test_properties(self):
        clusteralbs = ClusterALBs(clusteralbs_json)
        self.assertEqual('bm12clsw08k9uctrq8cg', clusteralbs.id)
        clusteralbs.id = 'newid'
        self.assertEqual('newid', clusteralbs.id)
        clusteralbs.region = 'eu-de'
        self.assertEqual('eu-de', clusteralbs.region)
        clusteralbs.ingress_hostname = 'hostname'
        self.assertEqual('hostname', clusteralbs.ingress_hostname)
        clusteralbs.ingress_secretname = 'secretname'
        self.assertEqual('secretname', clusteralbs.ingress_secretname)
        alb = clusteralbs.albs[0]
        self.assertEqual(2, len(clusteralbs.albs))
        clusteralbs.albs = []
        self.assertEqual([], clusteralbs.albs)
        clusteralbs.albs.append(alb)
        self.assertEqual(1, len(clusteralbs.albs))
        self.assertEqual('private-crbm12clsw08k9uctrq8cg-alb1', clusteralbs.albs[0].id)


if __name__ == '__main__':
    unittest.main()
