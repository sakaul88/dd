class User(object):
    def __init__(self, user_json):
        self.display_name = user_json['display_name']
        self.user_email = user_json['user_email']

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        self._display_name = display_name

    @property
    def user_email(self):
        return self._user_email

    @user_email.setter
    def user_email(self, user_email):
        self._user_email = user_email
