from .api import Api

class Voat(object):
    def __init__(self, appid, version, owner, apikey, username=None, password=None, access_token_file=None, base_url="https://fakevout.azurewebsites.net"):
        self.appid = appid
        self.version = version
        self.owner = owner
        self.api = Api(apikey, "{}:{} (by @{})".format(appid, version, owner), username, password, access_token_file, base_url)

    def user(self, username):
        return Voater(self.api, username)

    def subverse(self, name):
        return Subverse.from_name(self.api, name)

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

    @classmethod
    def from_name(cls, api, name):
        return cls(api, {"name": name})

    def submissions(self):
        subms = []
        for subm in self.api.get("api/v1/v/{}".format(self.name)):
            subms.append(Submission(self.api, subm))
        return subms

    def post(self, title, url=None, content=None):
        data = {
            "title": title,
        }
        if url is not None:
            data["url"] = url
        if content is not None:
            data["content"] = content

        subm = self.api.post("api/v1/v/{}".format(self.name), data)
        return Submission(self.api, subm)


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
        self.comment_count = data["commentCount"]
        self.date = data["date"]
        self.upvotes = data["upVotes"]
        self.downvotes = data["downVotes"]
        self.last_edit_date = data["lastEditDate"]
        self.views = data["views"]
        self.username = data["userName"]
        self.subverse = data["subverse"]
        self.thumbnail = data["thumbnail"]
        self.title = data["title"]
        self.type = data["type"]
        self.url = data.get("url")
        self.content = data.get("content")
        self.formatted_content = data.get("formattedContent")

    def __str__(self):
        return "[+{} -{}] @{} {}\n{}\n{}".format(self.upvotes, self.downvotes, self.username, self.title, self.url, self.content)

    def comments(self):
        coms = []
        for com in self.api.get("api/v1/v/{}/{}/comments".format(self.subverse, self.id)):
            coms.append(Comment(self.api, com))
        return coms

    def post(self, value):
        com = self.api.post("api/v1/v/{}/{}/comment".format(self.subverse, self.id), {"value": value})
        return Comment(self.api, com)


class Comment(object):
    def __init__(self, api, data):
        self.api = api
        self.id = data["id"]
        self.parent_id = data["parentID"]
        self.submission_id = data["submissionID"]
        self.subverse = data["subverse"]
        self.date = data["date"]
        self.last_edit_data = data["lastEditDate"]
        self.upvotes = data["upVotes"]
        self.downvotes = data["downVotes"]
        self.username = data["userName"]
        self.child_count = data["childCount"]
        self.level = data["level"]
        self.content = data["content"]
        self.formatted_content = data["formattedContent"]

    def __str__(self):
        return "[+{} -{}] @{}\n{}".format(self.upvotes, self.downvotes, self.username, self.content)


class Message(object):
    def __init__(self, api, data):
        self.api = api
        self.sender = data["sender"]
        self.subject = data["subject"]
        self.content = data["content"]

    def __str__(self):
        return "FROM: {}\nSUBJ: {}\n{}".format(self.sender, self.subject, self.content)
