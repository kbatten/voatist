#!/usr/bin/env python3

import os

import voatist

def main():
    if os.path.exists("access_token"):
        with open("access_token") as f:
            access_token = f.read()
    else:
        access_token = None
    voat = voatist.Voat("voatist", "0.0.1", "X_____X", os.environ.get("VOAT_API_KEY"), os.environ.get("VOAT_API_USERNAME"), os.environ.get("VOAT_API_PASSWORD"), access_token)

    voat.api.authorize()
    with open("access_token", "w") as f:
        f.write(voat.api.access_token)

    username = "X_____X"

    for com in voat.comment_stream():
        print("[+{} -{}] {}".format(com.upvotes, com.downvotes, com.content.replace("\n", " ").replace("\r", "")[:70]), "...")
    print()

    print("{}'s messages:".format(username))
    for msg in voat.user(username).messages():
        print(msg)
        print()

    print("{}'s subscriptions:".format(username))
    one_sub = False
    for sub in voat.user(username).subscriptions():
        if sub.type == "subverse":
            print("*", sub)
            if not one_sub:
                for subm in sub.submissions():
                    print("  [+{} -{}] {}".format(subm.upvotes, subm.downvotes, subm.title))
                    for com in subm.comments():
                        print("    [+{} -{}] {}".format(com.upvotes, com.downvotes, com.content.replace("\n", " ").replace("\r", "")[:66]), "...")
                one_sub = True
        elif sub.type == "set":
            print(">", sub)


if __name__ == "__main__":
    main()
