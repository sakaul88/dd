import unittest

from orchutils.ibmcloudmodels.accessgroupuser import AccessGroupUser

access_group_user_json = [
    {
        "id": "IBMid-5504t5563563563563456Tsd4",
        "type": "user"
    }
]


class TestAccessGroupUser(unittest.TestCase):
    def test_constructor(self):
        access_group_user = AccessGroupUser(access_group_user_json[0])
        self.assertEqual('IBMid-5504t5563563563563456Tsd4', access_group_user.id)
        self.assertEqual('user', access_group_user.access_type)

    def test_properties(self):
        access_group_user = AccessGroupUser(access_group_user_json[0])
        self.assertEqual('IBMid-5504t5563563563563456Tsd4', access_group_user.id)
        access_group_user.id = 'newid'
        self.assertEqual('newid', access_group_user.id)
        access_group_user.access_type = 'access_type'
        self.assertEqual('access_type', access_group_user.access_type)

    def test_parse_access_group_users(self):
        access_group_user = AccessGroupUser.parse_access_group_users(access_group_user_json)
        self.assertEqual(1, len(access_group_user))
        self.assertEqual('IBMid-5504t5563563563563456Tsd4', access_group_user[0].id)


if __name__ == '__main__':
    unittest.main()
