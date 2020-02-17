import unittest

from orchutils.ibmcloudmodels.kpkey import KPKey

kp_keys_json = [
        {
                'id': '387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a',
                'name': 'rk-platform-orchestration-np-sjc03',
                'type': 'application/vnd.ibm.kms.key+json',
                'createdBy': 'IBMid-270004DMSR',
                'creationDate': '2019-05-23T14:39:06Z',
                'extractable': False,
                'state': 1,
                'crn': 'crn:v1:bluemix:public:kms:us-east:a/69a92444d0c448d994ceb2f517b2fd39:741fac7d-ec04-4a10-a1e0-eef07f70927a:key:387c4fb0-4075-8bc8-51a9ec51ad8a'
        },
        {
                'id': '47f623ff-f2a5-45ff-9258-31c75f0253cf',
                'name': 'mykey',
                'type': 'application/vnd.ibm.kms.key+json',
                'createdBy': 'IBMid-270004DMSR',
                'creationDate': '2019-05-23T14:55:42Z',
                'extractable': False,
                'state': 1,
                'crn': 'crn:v1:bluemix:public:kms:us-east:a/69a92444d0c448d994ceb2f517b2fd39:741fac7d-ec04-4a10-a1e0-eef07f70927a:key:47f623ff-45ff-9258-31c75f0253cf'
        }
]


class TestKPKey(unittest.TestCase):
    def test_constructor(self):
        key = KPKey(kp_keys_json[0])
        self.assertEqual('387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a', key.id)
        self.assertEqual('rk-platform-orchestration-np-sjc03', key.name)
        self.assertEqual('application/vnd.ibm.kms.key+json', key.type)
        self.assertEqual(False, key.extractable)
        self.assertEqual(1, key.state)
        self.assertEqual('crn:v1:bluemix:public:kms:us-east:a/69a92444d0c448d994ceb2f517b2fd39:741fac7d-ec04-4a10-a1e0-eef07f70927a:key:387c4fb0-4075-8bc8-51a9ec51ad8a', key.crn)

    def test_properties(self):
        key = KPKey(kp_keys_json[0])
        self.assertEqual('387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a', key.id)
        key.id = 'newid'
        self.assertEqual('newid', key.id)
        key.name = 'name'
        self.assertEqual('name', key.name)
        key.type = 'type'
        self.assertEqual('type', key.type)
        key.extractable = True
        self.assertEqual(True, key.extractable)
        key.state = 2
        self.assertEqual(2, key.state)
        key.crn = 'crn'
        self.assertEqual('crn', key.crn)

    def test_parse_kp_keys(self):
        keys = KPKey.parse_kp_keys(kp_keys_json)
        self.assertEqual(2, len(keys))
        self.assertEqual('387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a', keys[0].id)
        self.assertEqual('47f623ff-f2a5-45ff-9258-31c75f0253cf', keys[1].id)


if __name__ == '__main__':
    unittest.main()
