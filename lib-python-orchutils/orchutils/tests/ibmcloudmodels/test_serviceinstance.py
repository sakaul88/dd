import unittest

from orchutils.ibmcloudmodels.serviceinstance import ServiceInstance

service_instances_json = [
    {
        'guid': 'cbb40c53-54b5-4747-b1d6-7c83d2d1171b',
        'id': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-54b5-4747-b1d6-7c83d2d1171b::',
        'url': '/v2/resource_instances/cbb40c53-54b5-4747-b1d6-7c83d2d1171b',
        'created_at': '2019-01-31T16:33:02.530426451Z',
        'updated_at': '2019-02-05T22:06:06.805925825Z',
        'deleted_at': None,
        'name': 'P2PaaS-Platform-NonProd-COS',
        'region_id': 'global',
        'account_id': '69a92444d0c448d994ceb2f517b2fd39',
        'resource_plan_id': '744bfc56-d12c-4866-88d5-dac9139e0e5d',
        'resource_group_id': 'caf60fc4514c420c86d2040feb352ef2',
        'crn': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-54b5-4747-b1d6-7c83d2d1171b::',
        'create_time': 0,
        'state': 'active',
        'type': 'service_instance',
        'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c',
        'dashboard_url': '/objectstorage/crn%3Av1%3Abluemix%3Apublic%3Acloud-object-storage%3Aglobal%3Aa%2F69a92444d0c4eb2f517b2fd39%3Acbb40c53-54b5-4747-b1d6-7c83d2d1171b%3A3A',
        'last_operation': None,
        'account_url': '',
        'resource_plan_url': '',
        'resource_bindings_url': '/v2/resource_instances/cbb40c53-54b5-4747-b1d6-7c83d2d1171b/resource_bindings',
        'resource_aliases_url': '/v2/resource_instances/cbb40c53-54b5-4747-b1d6-7c83d2d1171b/resource_aliases',
        'siblings_url': '',
        'target_crn': 'crn:v1:bluemix:public:globalcatalog::::deployment:744bfc56-d12c-4866-88d5-dac9139e0e5d%3Aglobal'
    },
    {
        'guid': '90cdb7c0-5bba-45e9-8f03-b27d19f0f54e',
        'id': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:90cdb7c0-5bba-45e9-8f03-b27d19f0f54e::',
        'url': '/v2/resource_instances/90cdb7c0-5bba-45e9-8f03-b27d19f0f54e',
        'created_at': '2019-03-22T10:53:38.077257073Z',
        'updated_at': '2019-03-22T10:53:38.077257073Z',
        'deleted_at': None,
        'name': 'alan-test',
        'region_id': 'global',
        'account_id': '69a92444d0c448d994ceb2f517b2fd39',
        'resource_plan_id': '744bfc56-d12c-4866-88d5-dac9139e0e5d',
        'resource_group_id': 'caf60fc4514c420c86d2040feb352ef2',
        'crn': 'crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:90cdb7c0-5bba-45e9-8f03-b27d19f0f54e::',
        'parameters': {
            'subscription_id': '',
            'HMAC': True
        },
        'create_time': 0,
        'state': 'active',
        'type': 'service_instance',
        'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c',
        'dashboard_url': '/objectstorage/crn%3Av1%3Abluemix%3Apublic%3Acloud-object-storage%3Aglobal%3Aa%2F69a92444d0c4b2f517b2fd39%3A90cdb7c0-5bba-45e9-8f03-b27d19f0f54e%3A%3A',
        'last_operation': None,
        'account_url': '',
        'resource_plan_url': '',
        'resource_bindings_url': '/v2/resource_instances/90cdb7c0-5bba-45e9-8f03-b27d19f0f54e/resource_bindings',
        'resource_aliases_url': '/v2/resource_instances/90cdb7c0-5bba-45e9-8f03-b27d19f0f54e/resource_aliases',
        'siblings_url': '',
        'target_crn': 'crn:v1:bluemix:public:globalcatalog::::deployment:744bfc56-d12c-4866-88d5-dac9139e0e5d%3Aglobal'
    }
]


class TestServiceInstance(unittest.TestCase):
    def test_constructor(self):
        instance = ServiceInstance(service_instances_json[0])
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-54b5-4747-b1d6-7c83d2d1171b::', instance.id)
        self.assertEqual('cbb40c53-54b5-4747-b1d6-7c83d2d1171b', instance.guid)
        self.assertEqual('P2PaaS-Platform-NonProd-COS', instance.name)
        self.assertEqual('global', instance.location)
        self.assertEqual('744bfc56-d12c-4866-88d5-dac9139e0e5d', instance.resource_plan_id)
        self.assertEqual('caf60fc4514c420c86d2040feb352ef2', instance.resource_group_id)
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-54b5-4747-b1d6-7c83d2d1171b::', instance.crn)
        self.assertEqual({}, instance.parameters)
        self.assertEqual('active', instance.state)

    def test_properties(self):
        instance = ServiceInstance(service_instances_json[0])
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-54b5-4747-b1d6-7c83d2d1171b::', instance.id)
        instance.id = 'newid'
        self.assertEqual('newid', instance.id)
        instance.guid = 'guid'
        self.assertEqual('guid', instance.guid)
        instance.name = 'name'
        self.assertEqual('name', instance.name)
        instance.location = 'location'
        self.assertEqual('location', instance.location)
        instance.resource_plan_id = '1234'
        self.assertEqual('1234', instance.resource_plan_id)
        instance.resource_group_id = 'resource_group_id'
        self.assertEqual('resource_group_id', instance.resource_group_id)
        instance.crn = 'crn'
        self.assertEqual('crn', instance.crn)
        instance.parameters = {'k': 'v'}
        self.assertEqual({'k': 'v'}, instance.parameters)
        instance.parameters['k2'] = 'v2'
        self.assertEqual({'k': 'v', 'k2': 'v2'}, instance.parameters)
        instance.state = 'state'
        self.assertEqual('state', instance.state)

    def test_parse_service_instances(self):
        instances = ServiceInstance.parse_service_instances(service_instances_json)
        self.assertEqual(2, len(instances))
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:cbb40c53-54b5-4747-b1d6-7c83d2d1171b::', instances[0].id)
        self.assertEqual('crn:v1:bluemix:public:cloud-object-storage:global:a/69a92444d0c448d994ceb2f517b2fd39:90cdb7c0-5bba-45e9-8f03-b27d19f0f54e::', instances[1].id)


if __name__ == '__main__':
    unittest.main()
