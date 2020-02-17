import unittest

from orchutils.ibmcloudmodels.alb import ALB

alb_json = {
    'albID': 'private-cr24e98d911cbc4f4ca59949a0527e7432-alb1',
    'clusterID': '24e98d911cbc4f4ca59949a0527e7432',
    'name': '',
    'albType': 'private',
    'enable': False,
    'state': 'disabled',
    'createdDate': '',
    'numOfInstances': '',
    'resize': False,
    'albip': '',
    'zone': 'sjc03',
    'disableDeployment': False,
    'albBuild': '406',
    'authBuild': '301'
}


class TestALB(unittest.TestCase):
    def test_constructor(self):
        alb = ALB(alb_json)
        self.assertEqual('private-cr24e98d911cbc4f4ca59949a0527e7432-alb1', alb.id)
        self.assertEqual('24e98d911cbc4f4ca59949a0527e7432', alb.cluster_id)
        self.assertEqual('private', alb.type)
        self.assertEqual(False, alb.enabled)
        self.assertEqual('disabled', alb.state)
        self.assertEqual('sjc03', alb.zone)
        self.assertEqual('', alb.ip)

    def test_properties(self):
        alb = ALB(alb_json)
        self.assertEqual('private-cr24e98d911cbc4f4ca59949a0527e7432-alb1', alb.id)
        alb.id = 'newid'
        self.assertEqual('newid', alb.id)
        alb.cluster_id = 'cluster_id'
        self.assertEqual('cluster_id', alb.cluster_id)
        alb.type = 'type'
        self.assertEqual('type', alb.type)
        alb.enabled = True
        self.assertEqual(True, alb.enabled)
        alb.state = 'state'
        self.assertEqual('state', alb.state)
        alb.zone = 'zone'
        self.assertEqual('zone', alb.zone)
        alb.ip = 'ip'
        self.assertEqual('ip', alb.ip)


if __name__ == '__main__':
    unittest.main()
