#!/usr/bin/env python3

import os

import voatist

def single_line(*data):
    limit = 60
    news = " ".join([str(s) for s in data]).replace("\n", " ").replace("\r", "")
    if len(news) > limit:
        news = "{}...".format(news[:limit-3])
    print(news)

def main():
    voat = voatist.Voat("voatist", "0.0.1", "X_____X", os.environ.get("VOAT_API_KEY"), os.environ.get("VOAT_API_USERNAME"), os.environ.get("VOAT_API_PASSWORD"), "access_token")

    username = "X_____X"

    for com in voat.comment_stream():
        single_line("[+{} -{}] {}".format(com.upvotes, com.downvotes, com.content))
    print()

    print("{}'s messages:".format(username))
    for msg in voat.user(username).messages():
        print(msg)
        print()

    print("{}'s subscriptions:".format(username))
    one = False
    for sub in voat.user(username).subscriptions():
        if sub.type == "subverse":
            single_line("*", sub)
            if not one:
                for subm in sub.submissions():
                    single_line("  [+{} -{}] {}".format(subm.upvotes, subm.downvotes, subm.title))
                    if not one:
                        for com in subm.comments():
                            single_line("    [+{} -{}] {}".format(com.upvotes, com.downvotes, com.content))
                            one = True
        elif sub.type == "set":
            single_line(">", sub)


if __name__ == "__main__":
    main()
