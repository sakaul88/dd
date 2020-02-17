import unittest

from orchutils.ibmcloudmodels.resourcegroup import ResourceGroup

resource_group_json = [
    {
        'id': '1af071b8b438f3349835869568445645',
        'account_id': 'urf9r93rt39urt39urthr93uht9urh',
        'name': 'resource_group_name',
        'default': False,
        'state': 'ACTIVE',
        'created_at': '2019-01-01T22:00:31.480Z',
        'updated_at': '2019-11-11T11:42:00.522Z'
    }
]


class TestResourceGroup(unittest.TestCase):
    def test_constructor(self):
        resource_group = ResourceGroup(resource_group_json[0])
        self.assertEqual('1af071b8b438f3349835869568445645', resource_group.id)
        self.assertEqual('urf9r93rt39urt39urthr93uht9urh', resource_group.account_id)
        self.assertEqual('resource_group_name', resource_group.name)
        self.assertEqual(False, resource_group.default)
        self.assertEqual('ACTIVE', resource_group.state)
        self.assertEqual('2019-01-01T22:00:31.480Z', resource_group.created_at)
        self.assertEqual('2019-11-11T11:42:00.522Z', resource_group.updated_at)

    def test_properties(self):
        resource_group = ResourceGroup(resource_group_json[0])
        self.assertEqual('1af071b8b438f3349835869568445645', resource_group.id)
        resource_group.id = 'newid'
        self.assertEqual('newid', resource_group.id)
        resource_group.account_id = 'account_id'
        self.assertEqual('account_id', resource_group.account_id)
        resource_group.name = 'name'
        self.assertEqual('name', resource_group.name)
        resource_group.default = True
        self.assertEqual(True, resource_group.default)
        resource_group.state = 'state'
        self.assertEqual('state', resource_group.state)
        resource_group.created_at = 'created_at'
        self.assertEqual('created_at', resource_group.created_at)
        resource_group.updated_at = 'updated_at'
        self.assertEqual('updated_at', resource_group.updated_at)

    def test_parse_resource_groups(self):
        resource_group = ResourceGroup.parse_resource_groups(resource_group_json)
        self.assertEqual(1, len(resource_group))
        self.assertEqual('1af071b8b438f3349835869568445645', resource_group[0].id)


if __name__ == '__main__':
    unittest.main()
