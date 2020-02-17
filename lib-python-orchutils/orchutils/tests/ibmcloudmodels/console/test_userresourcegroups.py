import unittest

from orchutils.ibmcloudmodels.console import UserResourceGroup

user_resource_group_json = [
    {
        "email": "someone@ibm.com",
        "access_level": "admin",
        "group_id": "jefnwkjsngsjghsr9",
        "group_name": "AdminGroup"
    }
]


class TestUser(unittest.TestCase):
    def test_constructor(self):
        user_resource_group = UserResourceGroup(user_resource_group_json[0])
        self.assertEqual('someone@ibm.com', user_resource_group.email)
        self.assertEqual('admin', user_resource_group.access_level)
        self.assertEqual('jefnwkjsngsjghsr9', user_resource_group.group_id)
        self.assertEqual('AdminGroup', user_resource_group.group_name)

    def test_properties(self):
        user_resource_group = UserResourceGroup(user_resource_group_json[0])
        self.assertEqual('someone@ibm.com', user_resource_group.email)
        user_resource_group.email = 'newemail'
        self.assertEqual('newemail', user_resource_group.email)
        user_resource_group.access_level = 'newaccesslevel'
        self.assertEqual('newaccesslevel', user_resource_group.access_level)
        user_resource_group.group_id = 'newgroupid'
        self.assertEqual('newgroupid', user_resource_group.group_id)
        user_resource_group.group_name = 'newgroupname'
        self.assertEqual('newgroupname', user_resource_group.group_name)

    def test_parse_user_resource_group(self):
        user_resource_groups = UserResourceGroup.parse_user_resource_group(user_resource_group_json)
        self.assertEqual(1, len(user_resource_groups))
        self.assertEqual('someone@ibm.com', user_resource_groups[0].email)


if __name__ == '__main__':
    unittest.main()
