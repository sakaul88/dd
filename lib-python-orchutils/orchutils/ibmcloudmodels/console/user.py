class User(object):
    def __init__(self, user_json):
        self.state = user_json['state']
        self.email = user_json['user_email']
        self.id = user_json['user_id']

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @classmethod
    def parse_users(self, users_json):
        """
        Helper method to parse a list of access groups dictionaries.
        This method simply iterates over the list, instantiating an acces group object for each dictionary.
        Args:
            user_jsons: A list of access group dictionaries from the ibmcloud cli
        Returns: A list of AccessGroup objects
        """
        users = []
        for user_json in users_json:
            users.append(User(user_json))
        return users
