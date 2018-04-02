from datetime import datetime
import re
from praw.exceptions import APIException 

p = re.compile(r'overwatch', re.IGNORECASE)

class CommentHandler:
	def __init__(self, total_times=0, last_time=datetime.now(), last_checked=datetime.now(), blocked_users=[], debug=False):
		self.total_times = total_times
		self.last_time = last_time
		self.last_checked = last_checked
		self.blocked_users = blocked_users
		self.debug = debug

	def handle_comment(self, submission):
		
		self._debug("---")
		self._debug("Post (" + submission.author.name + "): " + submission.body)
		
		self.total_times += 1
		time_since = (datetime.now() - self.last_time)
		
		# TODO: Store this better
		reply = "**Last mention of Overwatch: ~~%s~~ just now.**  \nTotal mentions of OW: %s  \n\n^^I'm ^^a ^^bot. ^^Beep ^^Boop. ^^Owner: ^^tcmalloc" % (time_since, self.total_times)
		
		self._debug(reply)
		try: 
			if not self.debug:
				if submission.author.name in self.blocked_users:
					self._debug("Blocked: Don't reply")
					return
				else:
					submission.reply(reply)
		except APIException:
			self._debug("Encountered API exception while replying")

		self.last_time = datetime.now()

	def handle(self, subreddit):
		self._debug("Checking Comments...")
		# work back through comments till we get to one before the last checked time

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

	# logs if we're currently debugging
	def _debug(self, msg):
		if self.debug:
			print(msg)

	def block_user(self, user):
		if user.name not in self.blocked_users:
			self._debug("Blocking /u/" + user.name)
			self.blocked_users.append(user.name)
