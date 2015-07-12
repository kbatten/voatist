#!/usr/bin/env python3

import os
import time

import voatist

POST=False

def single_line(*data):
    limit = 60
    news = " ".join([str(s) for s in data]).replace("\n", " ").replace("\r", "")
    if len(news) > limit:
        news = "{}...".format(news[:limit-3])
    print(news)

def main():
    voat = voatist.Voat("voatist", "0.0.1", "X_____X", os.environ.get("VOAT_API_KEY"), os.environ.get("VOAT_API_USERNAME"), os.environ.get("VOAT_API_PASSWORD"), "access_token")

    username = "X_____X"
    subverse = "XvvvvvX"

    if POST:
        subm = voat.subverse(subverse).post("test post", content="ping")
        print(subm)
        com = subm.post("pong")
        print(com)
        time.sleep(30)
        com.edit("gnop")
        subm.edit(title="best post", content="gnip")
        time.sleep(30)
        com.delete()
        time.sleep(15)
        subm.delete()
        return

    for com in voat.submission_stream():
        single_line(com)
    print()

    for com in voat.comment_stream():
        single_line(com)
    print()

    print("{}'s messages:".format(username))
    for msg in voat.user(username).messages():
        print(msg)
        print()

    print("{}'s subscriptions:".format(username))
    one = False
    for sub in voat.user(username).subverses():
            single_line("*", sub)
            if not one:
                for subm in sub.submissions():
                    single_line(" ", subm)
                    if not one:
                        for com in subm.comments():
                            single_line("   ", com)
                            one = True
    for subset in voat.user(username).sets():
        single_line(">", subset)


if __name__ == "__main__":
    main()
