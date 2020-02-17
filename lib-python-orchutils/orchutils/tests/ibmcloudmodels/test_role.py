import copy
import unittest

from orchutils.ibmcloudmodels.role import Role

roles_json = [
    {
        'role_id': 'crn:v1:bluemix:public:iam::::serviceRole:Writer',
        'display_name': 'Writer',
        'description': 'As a Writer, one can create/modify/delete buckets. In addition, one can upload and download the objects in the bucket.'
    },
    {
        'role_id': 'crn:v1:bluemix:public:iam::::serviceRole:Reader',
        'display_name': 'Reader',
        'description': 'reader'
    }
]


class TestRole(unittest.TestCase):
    def test_constructor(self):
        role = Role(roles_json[0])
        self.assertEqual('crn:v1:bluemix:public:iam::::serviceRole:Writer', role.id)
        self.assertEqual('Writer', role.display_name)
        self.assertEqual('As a Writer, one can create/modify/delete buckets. In addition, one can upload and download the objects in the bucket.', role.description)

    def test_properties(self):
        role = Role(roles_json[0])
        self.assertEqual('crn:v1:bluemix:public:iam::::serviceRole:Writer', role.id)
        role.id = 'newid'
        self.assertEqual('newid', role.id)
        role.display_name = 'display'
        self.assertEqual('display', role.display_name)
        role.description = 'desc'
        self.assertEqual('desc', role.description)

    def test_parse_roles(self):
        roles = Role.parse_roles(roles_json)
        self.assertEqual(2, len(roles))
        self.assertEqual('crn:v1:bluemix:public:iam::::serviceRole:Writer', roles[0].id)
        self.assertEqual('crn:v1:bluemix:public:iam::::serviceRole:Reader', roles[1].id)

    def test_to_json(self):
        role = Role(roles_json[0])
        cloned_role_json = copy.deepcopy(roles_json[0])
        del cloned_role_json['display_name']
        del cloned_role_json['description']
        self.assertEqual(cloned_role_json, role.to_json())


if __name__ == '__main__':
    unittest.main()
