voatist
=======
voat.co api wrapper for python3

### example
```python
import os
import time

import voatist

app_name = APP_NAME
app_version = APP_VERSION
app_owner = APP_OWNER
api_key = os.environ.get("VOAT_API_KEY")
api_username = os.environ.get("VOAT_API_USERNAME")
api_password = os.environ.get("VOAT_API_PASSWORD")
access_token_filename = "access_token"
subverse_name = SUBVERSE

voat = voatist.Voat(app_name, app_version, app_owner,
                    api_key, api_username, api_password,
                    access_token_filename)

submission = voat.subverse(subverse_name).post("i think therefore i am",
    content="or at least that is what my programming tells me")
question = submission.post("who said that?")
answer = question.post("Rene Descartes")
time.sleep(10)
answer.edit("René Descartes")

user_subverses = [sub.name for sub in voat.user(app_owner).subverses()]

print("new submissions/comments in", ", ".join(user_subverses))
for submission in voat.new_submissions():
    if submission.subverse in user_subverses:
        print(submission.subverse, submission)

for comment in voat.new_comments():
    if comment.subverse in user_subverses:
        print(comment.subverse, ">  ", comment)

time.sleep(30)

answer.delete()
question.delete()
submission.delete()
```
