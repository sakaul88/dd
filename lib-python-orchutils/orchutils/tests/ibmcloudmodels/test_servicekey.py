import copy
import unittest

from orchutils.ibmcloudmodels.servicekey import ServiceKey

service_keys_json = [
    {
        'guid': '110e47b2-2362-486b-be05-1df3bb9e9e21',
        'id': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b:resource-key:110e47b26b-be05-1df39e9e21',
        'url': '/v2/resource_keys/110e47b2-2362-486b-be05-1df3bb9e9e21',
        'created_at': '2019-01-31T16:33:44.422624039Z',
        'updated_at': '2019-01-31T16:33:44.422624039Z',
        'deleted_at': None,
        'name': 'P2PaaS-Platform-NonProd-COS',
        'account_id': '69a92444d0c448d994ceb2f517b2fd39',
        'resource_group_id': 'caf60fc4514c420c86d2040feb352ef2',
        'source_crn': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b::',
        'state': 'active',
        'credentials': {
            'apikey': 'api_key_value',
            'cos_hmac_keys': {
                'access_key_id': 'key_id_value',
                'secret_access_key': 'secret_key_value'
            },
            'endpoints': 'https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints',
            'iam_apikey_description': 'Auto generated apikey during resource-key operation for key - crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c41b::',
            'iam_apikey_name': 'auto-generated-apikey-110e47b2-2362-486b-be05-1df3bb9e9e21',
            'iam_role_crn': 'crn:v1:bluemix:public:iam::::serviceRole:Writer',
            'iam_serviceid_crn': 'crn:v1:bluemix:public:iam-identity::a/69a92444d0c448d994ceb2f517b2fd39::serviceid:ServiceId-06c21a9b-3785-456b-8c5d-cff04e5b8efc',
            'resource_key_id': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b::'
        },
        'iam_compatible': True,
        'resource_key_url': '/v2/resource_keys/cbb40c53-2d1171b',
        'crn': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b:resource-key:110e47b26b-be05-1df39e9e21'
    }
]


class TestServiceKey(unittest.TestCase):
    def test_constructor(self):
        key = ServiceKey(service_keys_json[0])
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b:resource-key:110e47b26b-be05-1df39e9e21', key.id)
        self.assertEqual('P2PaaS-Platform-NonProd-COS', key.name)
        self.assertEqual('caf60fc4514c420c86d2040feb352ef2', key.resource_group_id)
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b::', key.source_crn)
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b:resource-key:110e47b26b-be05-1df39e9e21', key.crn)
        self.assertEqual('active', key.state)
        self.assertEqual(service_keys_json[0]['credentials'], key.credentials)
        key_raw = copy.deepcopy(service_keys_json[0])
        del key_raw['credentials']
        key = ServiceKey(key_raw)
        self.assertEqual({}, key.credentials)

    def test_properties(self):
        key = ServiceKey(service_keys_json[0])
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b:resource-key:110e47b26b-be05-1df39e9e21', key.id)
        key.id = 'newid'
        self.assertEqual('newid', key.id)
        key.name = 'name'
        self.assertEqual('name', key.name)
        key.resource_group_id = 'resource_group_id'
        self.assertEqual('resource_group_id', key.resource_group_id)
        key.crn = 'source_crn'
        self.assertEqual('source_crn', key.crn)
        key.crn = 'crn'
        self.assertEqual('crn', key.crn)
        key.state = 'state'
        self.assertEqual('state', key.state)
        key.credentials = {}
        self.assertEqual({}, key.credentials)
        key.credentials = None
        self.assertEqual({}, key.credentials)

    def test_parse_service_keys(self):
        keys = ServiceKey.parse_service_keys(service_keys_json)
        self.assertEqual(1, len(keys))
        key = keys[0]
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-2d1171b:resource-key:110e47b26b-be05-1df39e9e21', key.id)


if __name__ == '__main__':
    unittest.main()
