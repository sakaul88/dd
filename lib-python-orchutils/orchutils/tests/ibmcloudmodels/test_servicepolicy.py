import copy
import json
import unittest

from orchutils.ibmcloudmodels.servicepolicy import ServicePolicy

service_policies_json = [
    {
        'id': '11ec84df-8ef0-4186-8dce-76023432a338',
        'type': 'access',
        'subjects': [
            {
                'attributes': [
                    {
                        'name': 'iam_id',
                        'value': 'iam-ServiceId-75ae2724-48be-433f-8c83-be05e32e4b60'
                    }
                ]
            }
        ],
        'roles': [
            {
                'role_id': 'crn:v1:bluemix:public:iam::::serviceRole:Writer',
                'display_name': 'Writer',
                'description': 'As a Writer, one can create/modify/delete buckets. In addition, one can upload and download the objects in the bucket.'
            }
        ],
        'resources': [
            {
                'attributes': [
                    {
                        'name': 'accountId',
                        'value': '69a92444d0c448d994ceb2f517b2fd39'
                    },
                    {
                        'name': 'serviceName',
                        'value': 'cloud-object-storage'
                    },
                    {
                        'name': 'servicepolicy',
                        'value': 'cbb40c53-54b5-4747-b1d6-7c83d2d1171b'
                    }
                ]
            }
        ],
        'href': 'https://iam.cloud.ibm.com/v1/policies/11ec84df-8ef0-4186-8dce-76023432a338',
        'created_at': '2019-08-20T14:56:11.072Z',
        'created_by_id': 'iam-ServiceId-a9e7347c-e7be-4a9e-8dd9-99e1abb72c8f',
        'last_modified_at': '2019-08-20T15:59:16.322Z',
        'last_modified_by_id': 'IBMid-270004DMSR'
    }
]


class TestServicePolicy(unittest.TestCase):
    def test_constructor(self):
        policy = ServicePolicy(service_policies_json[0])
        self.assertEqual('11ec84df-8ef0-4186-8dce-76023432a338', policy.id)
        self.assertEqual('access', policy.type)
        self.assertEqual(1, len(policy.subjects))
        self.assertEqual('iam_id', policy.subjects[0].attributes[0].name)
        self.assertEqual(1, len(policy.roles))
        self.assertEqual('crn:v1:bluemix:public:iam::::serviceRole:Writer', policy.roles[0].id)
        self.assertEqual(1, len(policy.resources))
        self.assertEqual('accountId', policy.resources[0].attributes[0].name)

    def test_properties(self):
        policy = ServicePolicy(service_policies_json[0])
        self.assertEqual('11ec84df-8ef0-4186-8dce-76023432a338', policy.id)
        policy.id = 'newid'
        self.assertEqual('newid', policy.id)
        policy.type = 'type'
        self.assertEqual('type', policy.type)
        policy.subjects = []
        self.assertEqual([], policy.subjects)
        policy.resources = []
        self.assertEqual([], policy.resources)
        policy.roles = []
        self.assertEqual([], policy.roles)

    def test_parse_service_policies(self):
        policies = ServicePolicy.parse_service_policies(service_policies_json)
        self.assertEqual(1, len(policies))
        self.assertEqual('11ec84df-8ef0-4186-8dce-76023432a338', policies[0].id)

    def test_to_json(self):
        policy = ServicePolicy(service_policies_json[0])
        cloned_policy_json = copy.deepcopy(service_policies_json[0])
        del cloned_policy_json['id']
        del cloned_policy_json['href']
        del cloned_policy_json['created_at']
        del cloned_policy_json['created_by_id']
        del cloned_policy_json['last_modified_at']
        del cloned_policy_json['last_modified_by_id']
        del cloned_policy_json['roles'][0]['display_name']
        del cloned_policy_json['roles'][0]['description']
        self.assertDictEqual(cloned_policy_json, json.loads(json.dumps(policy, default=lambda o: getattr(o, 'to_json')())))


if __name__ == '__main__':
    unittest.main()
