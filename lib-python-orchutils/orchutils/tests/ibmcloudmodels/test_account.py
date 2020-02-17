import unittest

from orchutils.ibmcloudmodels.account import Account

account_json = {
    'guid': '69a92444d0c448d994ceb2f517b2fd39',
    'name': 'P2PaaS Account',
    'owner': 'owner@us.ibm.com'
}


class TestAccount(unittest.TestCase):
    def test_constructor(self):
        account = Account(account_json)
        self.assertEqual('69a92444d0c448d994ceb2f517b2fd39', account.guid)
        self.assertEqual('P2PaaS Account', account.name)
        self.assertEqual('owner@us.ibm.com', account.owner)

    def test_properties(self):
        account = Account(account_json)
        self.assertEqual('69a92444d0c448d994ceb2f517b2fd39', account.guid)
        account.guid = 'guid'
        self.assertEqual('guid', account.guid)
        account.name = 'newname'
        self.assertEqual('newname', account.name)
        account.owner = 'newowner@ie.ibm.com'
        self.assertEqual('newowner@ie.ibm.com', account.owner)


if __name__ == '__main__':
    unittest.main()
