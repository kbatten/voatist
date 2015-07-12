from .api import Api

class Voat(object):
    def __init__(self, appid, version, owner, apikey):
        self.appid = appid
        self.version = version
        self.owner = owner
        self.api = Api(apikey, "{}:{} (by @{})".format(appid, version, owner))

    def user(self, username):
        return Voater(username, self.api)

class Voater(object):
    def __init__(self, username, api):
        self.username = username
        self.api = api

    def subscriptions(self):
        return self.api.get("api/v1/u/{}/subscriptions".format(self.username))
