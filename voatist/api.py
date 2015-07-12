import time
import os
import json
import sys

import requests

THROTTLE_GROW = 3
THROTTLE_DECAY = 0.8
THROTTLE_MIN = 1.1
THROTTLE_MAX = 275

LOGGING = True


class Api(object):
    def __init__(self, apikey, useragent, username, password, access_token_file, base_url):
        self.apikey = apikey
        self.useragent = useragent
        self.username = username
        self.password = password
        self.access_token_file = access_token_file
        self.base_url = base_url

        self.access_token = None
        if self.access_token_file is not None:
            if os.path.exists(self.access_token_file):
                with open(self.access_token_file) as f:
                    self.access_token = f.read()

        self.next_request_time = 0

        # at 1 per second, throttle is 1
        # at 20 per minute (60/20), throttle is 3
        # at 200 per hour (60*60/200), throttle is 18
        # at 1500 per day (60*60*24/1500), throttle is 60
        # at 3000 per week (60*60*24*7/3000), throttle is 200
        self.throttle = THROTTLE_MIN

    def get(self, path, **params):
        return self.verb("get", path, **params)

    def post(self, path, body, **params):
        return self.verb("post", path, body, **params)

    def put(self, path, body, **params):
        return self.verb("put", path, body, **params)

    def delete(self, path):
        return self.verb("delete", path)

    def authorize(self):
        """ only generate a new access token if necessary """
        self.get("api/v1/u/messages")

    def reauthorize(self):
        """ always generate a new access token """
        return self.verb("reauthorize")

    def verb(self, verb, path, body=None, **params):
        while True:
            while time.time() < self.next_request_time:
                time.sleep(self.next_request_time - time.time())
            self.next_request_time = time.time() + self.throttle

            body = {k: v for k, v in body.items() if v is not None} if body is not None else None
            params = {k: v for k, v in params.items() if v is not None}
            url = "{}/{}".format(self.base_url, path)
            headers = {
                "User-Agent": self.useragent,
                "Voat-ApiKey": self.apikey,
            }
            if self.access_token is not None:
                headers["Authorization"] = "Bearer {}".format(self.access_token)

            if verb == "get":
                res = requests.get(url, params=params, headers=headers)
            elif verb == "post":
                headers["Content-Type"] = "application/json"
                res = requests.post(url, params=params, headers=headers, data=json.dumps(body))
            elif verb == "put":
                headers["Content-Type"] = "application/json"
                res = requests.put(url, params=params, headers=headers, data=json.dumps(body))
            elif verb == "delete":
                res = requests.delete(url, headers=headers)
            elif verb == "reauthorize":
                if self.username is None or self.password is None:
                    raise Exception("Missing credentials")
                if self.access_token_file is None:
                    raise Exception("Unknown access token file")
                body = "grant_type=password&username={}&password={}".format(self.username, self.password)
                res = requests.post(url, headers=headers, data=body)
                if res.status_code == 200:
                    self.access_token = res.json()["access_token"]
                    with open(self.access_token_file, "w") as f:
                        f.write(self.access_token)
                    self.throttle_decay()
                    return

            data = res.json().get("data")
            success = res.json().get("success")
            error = res.json().get("error")

            if res.status_code == 200 and success is True:
                self.throttle_decay()
                return data

            # see if we need to reauth
            if res.status_code == 401 and verb != "reauthorize":
                log("reauthorize", error)
                self.reauthorize()
                continue
            elif res.status_code == 401 and verb == "reauthorize":
                log("reauthorization error", error)

            # see if we need to increase our throttling
            if res.status_code == 429 or (success is False and error["type"] == "ApiThrottleLimit"):
                self.throttle_grow()
                continue

            raise Exception(res, url, params, res.content)

    def throttle_decay(self):
        self.throttle *= THROTTLE_DECAY
        if self.throttle < THROTTLE_MIN:
            self.throttle = THROTTLE_MIN
        else:
            log("backoff to one request every", int(self.throttle), "seconds")

    def throttle_grow(self):
        self.throttle *= THROTTLE_GROW
        if self.throttle > THROTTLE_MAX:
            self.throttle = THROTTLE_MAX
        log("backoff to one request every", int(self.throttle), "seconds", verb, url, error)



def log(*msg):
    if LOGGING is False:
        return
    print(time.time(), "[Api]", *msg, file=sys.stderr)
