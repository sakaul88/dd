import unittest

from orchutils.ibmcloudmodels.console import User

user_json = [
    {
        "state": "Active",
        "user_email": "someone@ibm.com",
        "user_id": "IDdfjneferngieurgi3rug"
    }
]


class TestUser(unittest.TestCase):
    def test_constructor(self):
        user = User(user_json[0])
        self.assertEqual('Active', user.state)
        self.assertEqual('someone@ibm.com', user.email)
        self.assertEqual('IDdfjneferngieurgi3rug', user.id)

    def test_properties(self):
        user = User(user_json[0])
        self.assertEqual('Active', user.state)
        user.state = 'newstate'
        self.assertEqual('newstate', user.state)
        user.email = 'newemail'
        self.assertEqual('newemail', user.email)
        user.id = 'newid'
        self.assertEqual('newid', user.id)

    def test_parse_users(self):
        user = User.parse_users(user_json)
        self.assertEqual(1, len(user))
        self.assertEqual('someone@ibm.com', user[0].email)


if __name__ == '__main__':
    unittest.main()
