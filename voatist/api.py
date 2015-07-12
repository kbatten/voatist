import time

import requests

class Api(object):
    def __init__(self, apikey, useragent):
        self.apikey = apikey
        self.useragent = useragent
        self.next_request_time = 0
        self.base_url = "https://fakevout.azurewebsites.net"
        self.throttle = 1.1

    def get(self, path, **params):
        while True:
            while time.time() < self.next_request_time:
                print("sleeping for {} seconds".format(self.next_request_time - time.time()))
                time.sleep(self.next_request_time - time.time())
            # decay thottling
            self.throttle /= 2
            if self.throttle < 1.1:
                self.throttle = 1.1
            self.next_request_time = time.time() + self.throttle

            params = {k: v for k, v in params.items() if v is not None}
            url = "{}/{}".format(self.base_url, path)
            headers = {
                "User-Agent": self.useragent,
                "Voat-ApiKey": self.apikey,
            }
            res = requests.get(url, params=params, headers=headers)
            if res.status_code != 200:
                raise Exception(res, res.content)

            json = res.json()
            if json["success"]:
                return res.json()["data"]

            if json["error"]["type"] == "ApiThrottleLimit":
                self.throttle *= 2
                continue

            raise Exception(json["error"]["type"], json["error"]["message"])

    
