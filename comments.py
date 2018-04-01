from datetime import datetime
import re
from praw.exceptions import APIException 

p = re.compile(r'overwatch', re.IGNORECASE)

class CommentHandler:
	def __init__(self, total_times=0, last_time=datetime.utcfromtimestamp(0), last_checked=datetime.now(), blocked_users=[]):
		self.total_times = total_times
		self.last_time = last_time
		self.last_checked = last_checked
		self.blocked_users = blocked_users
		print(self.blocked_users)

	def handle_comment(self, submission):
		if submission.author.name in self.blocked_users:
			return
		
		print("---")
		print("Post (" + submission.author.name + "): " + submission.body)
		
		self.total_times += 1
		time_since = (datetime.now() - self.last_time)
		
		# TODO: Store this better
		reply = "**Last mention of Overwatch: ~~%s~~ just now.**  \nTotal mentions of OW: %s  \n\n^^I'm ^^a ^^bot. ^^Beep ^^Boop. ^^Owner: ^^tcmalloc" % (time_since, self.total_times)
		
		print(reply)
		try: 
			submission.reply(reply)
			pass
		except APIException:
			print("Encountered API exception while replying")

		self.last_time = datetime.now()

	def handle(self, subreddit):
		print("Checking Comments...")
		# work back through new till we get to one before the last checked time
   
		# while we're still checking for stuff
		isChecking = True

		# get comments
		# caveat: praw doesn't let us specify an offset, so if a lot of commenting happens in a short space of time, 
		# 			some may be missed
		comments = subreddit.comments()
	 
		for comment in comments:
			# for each one, check if they're from before when we last checked
			created = datetime.fromtimestamp(int(comment.created_utc))
			if created <= self.last_checked:
				# if so, we're done. break out both loops
				break

			# otherwise, do our usual checking
			self.handle_comment(comment)
		# once we've exited we've either checked all the comments given, or we've reached the last comment we checked.
		# either way, we're done here.

		# update the last checked time
		self.last_checked = datetime.now()

