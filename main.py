import calendar
import json
import os
import humanize
import praw
import re
import _thread
from datetime import datetime
from praw.exceptions import APIException 

observed_comments = []
last_time = datetime.now()
total_times = 0

user_agent = os.environ['CLIENT_SECRET']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

username = os.environ['REDDIT_USERNAME']
password = os.environ['REDDIT_PASSWORD']

reddit = praw.Reddit(user_agent=user_agent,
                     client_id=client_id,
                     client_secret=client_secret,
                     username=username, password=password)

subreddit = reddit.subreddit('tcss')
p = re.compile(r'overwatch', re.IGNORECASE)

def deal_with(submission):
    global total_times
    global last_time 
    global observed_comments
    
    if submission.id in observed_comments:
        return

    print("---")
    print("OVERWATCH: " + submission.body)
    total_times += 1
    time_since = (datetime.now() - last_time)
    reply = "**Last mention of Overwatch: ~~%s~~ just now.**  \nTotal mentions of OW: %s  \n\n^^I'm ^^a ^^bot. ^^Beep ^^Boop. ^^Owner: ^^tcmalloc" % (time_since, total_times)
    
    print(reply)
    try: 
        submission.reply(reply)

    except APIException:
        print("Encountered API exception while replying")

    last_time = datetime.now()
    observed_comments.reverse()
    observed_comments.append(submission.id)
    observed_comments.reverse()
    del observed_comments[100:]

def watch_comments(reddit, subreddit):
    for submission in subreddit.stream.comments():
        all_text = submission.body
        
        if p.match(all_text):
            deal_with(submission)

try:
    with open("bot.json", "r") as f:
        data = json.load(f)

    observed_comments = data["observed_comments"]
    total_times = data["total_times"]
    last_time = datetime.utcfromtimestamp(int(data["last_time"]))
except IOError:
    print("No past config.")

try:
    watch_comments(reddit, subreddit)
except KeyboardInterrupt:
    print("Saving stats...")

    # reddit will only return the last 100 comments so we don't need to store past that.
    del observed_comments[100:]

    with open("bot.json", "w") as f:
        json.dump({"observed_comments": observed_comments, "total_times": total_times, "last_time": calendar.timegm(last_time.timetuple())}, f, indent="\t")

