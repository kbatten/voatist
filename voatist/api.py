import time
import os
import json
import sys

import requests

THROTTLE_GROW = 3
THROTTLE_DECAY = 0.8
THROTTLE_MIN = 1.1
THROTTLE_MAX = 275
THROTTLE_RETRY = 10  # always wait at least this many seconds after error

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

        self.rate_limiter = RateLimiterSimple(THROTTLE_MIN,
                                              THROTTLE_MAX,
                                              THROTTLE_DECAY,
                                              THROTTLE_GROW,
                                              THROTTLE_RETRY)

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
        return self.verb("reauthorize", "api/token")

    def verb(self, verb, path, body=None, **params):
        while True:
            self.rate_limiter.request()

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
                    self.rate_limiter.success()
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
                self.next_request_time += THROTTLE_RETRY
                self.throttle_grow()
                continue

            raise Exception(res, url, params, res.content)


class RateLimiterSimple
    def __init__(self, delay_min, delay_max, decay, grow):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.decay = decay
        self.grow = grow
        self.delay = delay_min
        self.next_request_time = 0

    def request(self):
        while time.time() < self.next_request_time:
            time.sleep(self.next_request_time - time.time())
        self.next_request_time = time.time() + self.delay
        self.delay_decay()

    def throttled(self):
        self.delay_grow()

    def delay_decay(self):
        should_log = self.throttle > THROTTLE_MIN
        self.throttle *= THROTTLE_DECAY
        if self.throttle < THROTTLE_MIN:
            self.throttle = THROTTLE_MIN
        if should_log:
            log("backoff up to one request per", int(self.throttle), "seconds")

    def delay_grow(self):
        self.throttle *= THROTTLE_GROW
        if self.throttle > THROTTLE_MAX:
            self.throttle = THROTTLE_MAX
        log("backoff down to one request per", int(self.throttle), "seconds")


class RateLimiter(object):
    """
    two modes
    1 - always go as fast as possible up to the breakpoint
        first 20 requests in a minute go at 1 per second, but the next request
        then has to wait till that minute is up before it can do anything
    2 - smoothly move between throttle points
        total delay should be the same as the first mode
    """
    def __init__(self):
        # at 1 per second, throttle is 1 step is 0.210527
        # at 20 per minute (60/20), throttle is 3
        # at 200 per hour (60*60/200), throttle is 18
        # at 1500 per day (60*60*24/1500), throttle is 60
        # at 3000 per week (60*60*24*7/3000), throttle is 200
        self.limits = [
            (1, 1),
            (20, 60),
            (200, 3600),
            (1500, 86400),
            (3000, 604800),
        ]
        self.requests = []
        self.throttles = []
        self.next_request_time = 0
        self.delay = 1
        self.delay_on_throttle = 10

    def request(self):
        while time.time() < self.next_request_time:
            time.sleep(self.next_request_time - time.time())

        cur_time = time.time
        self.requests.append(cur_time)

        # trim requests that are too old
        for start_index, req_time in enumerate(self.requests):
            if cur_time - req_time < self.limits[-1][1]:
                break
        self.requests = self.requests[start_index:]

        # calculate delay based on number of requests and throttles
        num_reqs = len(self.requests)
        num_throts = len(self.throttles)

        # find which two limits we are between
        for high_index, high_limit, high_delay in enumerate(self.limits):
            if high_limit <= num_reqs:
                break
        if high_index == 0:
            self.delay = high_delay
        else:
            low_limit, low_age = self.limits[high_index-1]
            
        # calculate a rate based on how close we are to each one
        self.next_request_time = time.time() + self.delay

    def throttled(self):
        """ outside throttling """
        self.next_request_time += self.delay_on_throttle
        self.throttles.append(time.time())
        log("throttling,", len(self.throttles), "throttles,", self.delay, "second delay")



def log(*msg):
    if LOGGING is False:
        return
    print(time.time(), "[Api]", *msg, file=sys.stderr)
