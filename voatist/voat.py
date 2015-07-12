from .api import Api

class Voat(object):
    def __init__(self, appid, version, owner, apikey, username=None, password=None, access_token_file=None, base_url="https://fakevout.azurewebsites.net"):
        self.appid = appid
        self.version = version
        self.owner = owner
        self.api = Api(apikey, "{}:{} (by @{})".format(appid, version, owner), username, password, access_token_file, base_url)

    def user(self, username):
        return Voater(self.api, username)

    def comment_stream(self):
        coms = []
        for com in self.api.get("api/v1/stream/comments"):
            coms.append(Comment(self.api, com))
        return coms


class Voater(object):
    def __init__(self, api, username):
        self.api = api
        self.username = username

    def messages(self):
        msgs = []
        for msg in self.api.get("api/v1/u/messages", type=31, state=3):
            msgs.append(Message(self.api, msg))
        return msgs

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


class Message(object):
    def __init__(self, api, data):
        self.api = api
        self.sender = data["sender"]
        self.subject = data["subject"]
        self.content = data["content"]

    def __str__(self):
        return "FROM: {}\nSUBJECT: {}\n{}".format(self.sender, self.subject, self.content)
