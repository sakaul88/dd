from orchutils.ibmcloudmodels.account import Account
from orchutils.ibmcloudmodels.region import Region
from orchutils.ibmcloudmodels.user import User


class Target(object):
    def __init__(self, target_json):
        self.account = Account(target_json['account'])
        self.api_endpoint = target_json['api_endpoint']
        self.region = Region(target_json['region'])
        self.user = User(target_json['user'])

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, account):
        self._account = account

    @property
    def api_endpoint(self):
        return self._api_endpoint

    @api_endpoint.setter
    def api_endpoint(self, api_endpoint):
        self._api_endpoint = api_endpoint

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user
