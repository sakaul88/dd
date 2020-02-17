import unittest

from orchutils.ibmcloudmodels.user import User

user_json = {
    'display_name': 'alan.byrne@ie.ibm.com',
    'user_email': 'mail@ie.ibm.com'
}


class TestUser(unittest.TestCase):
    def test_constructor(self):
        user = User(user_json)
        self.assertEqual('alan.byrne@ie.ibm.com', user.display_name)
        self.assertEqual('mail@ie.ibm.com', user.user_email)

    def test_properties(self):
        user = User(user_json)
        self.assertEqual('alan.byrne@ie.ibm.com', user.display_name)
        user.display_name = 'newname'
        self.assertEqual('newname', user.display_name)
        user.user_email = 'value'
        self.assertEqual('value', user.user_email)


if __name__ == '__main__':
    unittest.main()
