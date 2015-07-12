from .api import Api

class Voat(object):
    def __init__(self, appid, version, owner, apikey):
        self.appid = appid
        self.version = version
        self.owner = owner
        self.api = Api(apikey, "{}:{} (by @{})".format(appid, version, owner))

    def user(self, username):
        return Voater(self.api, username)


class Voater(object):
    def __init__(self, api, username):
        self.api = api
        self.username = username

    def subscriptions(self):
        subs = []
        for sub in self.api.get("api/v1/u/{}/subscriptions".format(self.username)):
            if sub["type"] == 1:
                subs.append(Subverse(self.api, sub))
            elif sub["type"] == 2:
                subs.append(SubverseSet(self.api, sub))
        return subs


class Subverse(object):
    def __init__(self, api, data):
        self.api = api
        self.name = data["name"]
        self.type = "subverse"

    def __str__(self):
        return self.name

    def submissions(self):
        subms = []
        for subm in self.api.get("api/v1/v/{}".format(self.name)):
            subms.append(Submission(self.api, subm))
        return subms


class SubverseSet(object):
    def __init__(self, api, data):
        self.api = api
        self.name = data["name"]
        self.type = "set"

    def __str__(self):
        return self.name


class Submission(object):
    def __init__(self, api, data):
        self.api = api
        self.id = data["id"]
        self.subverse = data["subverse"]
        self.title = data["title"]
        self.upvotes = data["upVotes"]
        self.downvotes = data["downVotes"]

    def comments(self):
        coms = []
        for com in self.api.get("api/v1/v/{}/{}/comments".format(self.subverse, self.id)):
            coms.append(Comment(self.api, com))
        return coms


class Comment(object):
    def __init__(self, api, data):
        self.api = api
        self.upvotes = data["upVotes"]
        self.downvotes = data["downVotes"]
        self.content = data["content"]
