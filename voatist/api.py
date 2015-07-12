import time
import os
import json

import requests

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
        self.throttle = 1.1

    def get(self, path, **params):
        while True:
            while time.time() < self.next_request_time:
                time.sleep(self.next_request_time - time.time())
            # decay thottling
            self.throttle /= 1.3
            if self.throttle < 1.1:
                self.throttle = 1.1
            self.next_request_time = time.time() + self.throttle

            params = {k: v for k, v in params.items() if v is not None}
            url = "{}/{}".format(self.base_url, path)
            headers = {
                "User-Agent": self.useragent,
                "Voat-ApiKey": self.apikey,
            }
            if self.access_token is not None:
                headers["Authorization"] = "Bearer {}".format(self.access_token)
            res = requests.get(url, params=params, headers=headers)
            if res.status_code == 200:
                return res.json()["data"]

            # see if we need to reauth
            if res.status_code == 401:
                self.reauthorize()
                continue

            # see if we need to increase our throttling
            if res.status_code == 429 or res.json()["error"]["type"] == "ApiThrottleLimit":
                self.throttle *= 2
                if self.throttle > 220:
                    self.throttle = 220
                continue

            raise Exception(res, url, params, res.content)

    def post(self, path, data, **params):
        while True:
            while time.time() < self.next_request_time:
                time.sleep(self.next_request_time - time.time())
            # decay thottling
            self.throttle /= 1.3
            if self.throttle < 1.1:
                self.throttle = 1.1
            self.next_request_time = time.time() + self.throttle

            params = {k: v for k, v in params.items() if v is not None}
            url = "{}/{}".format(self.base_url, path)
            headers = {
                "User-Agent": self.useragent,
                "Voat-ApiKey": self.apikey,
                "Content-Type": "application/json",
            }
            if self.access_token is not None:
                headers["Authorization"] = "Bearer {}".format(self.access_token)
            res = requests.post(url, params=params, headers=headers, data=json.dumps(data))

            if res.status_code == 200:
                return res.json()["data"]

            # see if we need to reauth
            if res.status_code == 401:
                self.reauthorize()
                continue

            # see if we need to increase our throttling
            if res.status_code == 429 or res.json()["error"]["type"] == "ApiThrottleLimit":
                self.throttle *= 2
                if self.throttle > 220:
                    self.throttle = 220
                continue

            raise Exception(res, url, params, res.content)

    def put(self, path, data, **params):
        while True:
            while time.time() < self.next_request_time:
                time.sleep(self.next_request_time - time.time())
            # decay thottling
            self.throttle /= 1.3
            if self.throttle < 1.1:
                self.throttle = 1.1
            self.next_request_time = time.time() + self.throttle

            params = {k: v for k, v in params.items() if v is not None}
            url = "{}/{}".format(self.base_url, path)
            headers = {
                "User-Agent": self.useragent,
                "Voat-ApiKey": self.apikey,
                "Content-Type": "application/json",
            }
            if self.access_token is not None:
                headers["Authorization"] = "Bearer {}".format(self.access_token)
            res = requests.put(url, params=params, headers=headers, data=json.dumps(data))

            if res.status_code == 200:
                return res.json()["data"]

            # see if we need to reauth
            if res.status_code == 401:
                self.reauthorize()
                continue

            # see if we need to increase our throttling
            if res.status_code == 429 or res.json()["error"]["type"] == "ApiThrottleLimit":
                self.throttle *= 2
                if self.throttle > 220:
                    self.throttle = 220
                continue

            raise Exception(res, url, params, res.content)

    def delete(self, path, **params):
        while True:
            while time.time() < self.next_request_time:
                time.sleep(self.next_request_time - time.time())
            # decay thottling
            self.throttle /= 1.3
            if self.throttle < 1.1:
                self.throttle = 1.1
            self.next_request_time = time.time() + self.throttle

            params = {k: v for k, v in params.items() if v is not None}
            url = "{}/{}".format(self.base_url, path)
            headers = {
                "User-Agent": self.useragent,
                "Voat-ApiKey": self.apikey,
            }
            if self.access_token is not None:
                headers["Authorization"] = "Bearer {}".format(self.access_token)
            res = requests.delete(url, params=params, headers=headers)
            if res.status_code == 200:
                return

            # see if we need to reauth
            if res.status_code == 401:
                self.reauthorize()
                continue

            # see if we need to increase our throttling
            if res.status_code == 429 or res.json()["error"]["type"] == "ApiThrottleLimit":
                self.throttle *= 2
                if self.throttle > 220:
                    self.throttle = 220
                continue

            raise Exception(res, url, params, res.content)

    def authorize(self):
        """ only generate a new access token if necessary """
        self.get("api/v1/u/messages")

    def reauthorize(self):
        """ always generate a new access token """
        if self.username is None or self.password is None:
            raise Exception("Missing credentials")

        while True:
            while time.time() < self.next_request_time:
                time.sleep(self.next_request_time - time.time())
            # decay thottling
            self.throttle /= 1.3
            if self.throttle < 1.1:
                self.throttle = 1.1
            self.next_request_time = time.time() + self.throttle

            url = "{}/api/token".format(self.base_url)
            headers = {
                "User-Agent": self.useragent,
                "Voat-ApiKey": self.apikey,
            }
            data = "grant_type=password&username={}&password={}".format(self.username, self.password)
            res = requests.post(url, headers=headers, data=data)
            if res.status_code == 200:
                self.access_token = res.json()["access_token"]
                if self.access_token_file is not None:
                    with open(self.access_token_file, "w") as f:
                        f.write(self.access_token)
                return

            # see if we need to increase our throttling
            if res.status_code == 429 or res.json()["error"]["type"] == "ApiThrottleLimit":
                self.throttle *= 2
                if self.throttle > 220:
                    self.throttle = 220
                continue

            raise Exception(res, url, res.content)
