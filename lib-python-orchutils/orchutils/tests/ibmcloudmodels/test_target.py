import unittest

from orchutils.ibmcloudmodels.account import Account
from orchutils.ibmcloudmodels.region import Region
from orchutils.ibmcloudmodels.target import Target
from orchutils.ibmcloudmodels.user import User

target_json = {
    'account': {
        'guid': '69a92444d0c448d994ceb2f517b2fd39',
        'name': 'P2PaaS Account',
        'owner': 'jrwong@ca.ibm.com'
    },
    'api_endpoint': 'https://cloud.ibm.com',
    'region': {
        'mccp_id': '',
        'name': ''
    },
    'user': {
        'display_name': 'alan.byrne@ie.ibm.com',
        'user_email': 'alan.byrne@ie.ibm.com'
    }
}


class TestTarget(unittest.TestCase):
    def test_constructor(self):
        target = Target(target_json)
        self.assertEqual('69a92444d0c448d994ceb2f517b2fd39', target.account.guid)
        self.assertEqual('https://cloud.ibm.com', target.api_endpoint)
        self.assertEqual('', target.region.name)
        self.assertEqual('alan.byrne@ie.ibm.com', target.user.display_name)

    def test_properties(self):
        target = Target(target_json)
        self.assertEqual('69a92444d0c448d994ceb2f517b2fd39', target.account.guid)
        account_json = target_json['account']
        account_json['guid'] = 'newguid'
        target.account = Account(account_json)
        self.assertEqual('newguid', target.account.guid)
        target.api_endpoint = 'endpoint'
        self.assertEqual('endpoint', target.api_endpoint)
        region_json = target_json['region']
        region_json['mccp_id'] = 'id'
        target.region = Region(region_json)
        self.assertEqual('id', target.region.mccp_id)
        user_json = target_json['user']
        user_json['display_name'] = 'name'
        target.user = User(user_json)
        self.assertEqual('name', target.user.display_name)


if __name__ == '__main__':
    unittest.main()
