#!/usr/bin/env python3

import os

import voatist

def main():
    voat = voatist.Voat("voatist", "0.0.1", "X_____X", os.environ.get("VOAT_API_KEY"))

    username = "X_____X"
    print("{}'s subscriptions:".format(username))
    one_sub = False
    for sub in voat.user(username).subscriptions():
        if sub.type == "subverse":
            print("*", sub)
            if not one_sub:
                for subm in sub.submissions():
                    print("  [+{} -{}] {}".format(subm.upvotes, subm.downvotes, subm.title))
                    for com in subm.comments():
                        print("    [+{} -{}] {}".format(com.upvotes, com.downvotes, com.content[:20]), "...")
                one_sub = True
        elif sub.type == "set":
            print(">", sub)


if __name__ == "__main__":
    main()
