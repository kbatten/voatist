#!/usr/bin/env python3

import os

import voatist

def main():
    voat = voatist.Voat("voatist", "0.0.1", "X_____X", os.environ.get("VOAT_API_KEY"))

    username = "X_____X"
    print("{}'s subscriptions:".format(username))
    for v in voat.user(username).subscriptions():
        print("*", v["name"])

if __name__ == "__main__":
    main()
