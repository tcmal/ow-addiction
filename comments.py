from datetime import datetime
import re
from praw.exceptions import APIException 

p = re.compile(r'overwatch', re.IGNORECASE)

class CommentHandler:
	def __init__(self, username, total_times=0, last_time=datetime.now(), last_checked=datetime.now(), blocked_users=[], debug=False):
		self.username = username
		self.total_times = total_times
		self.last_time = last_time
		self.last_checked = last_checked
		self.blocked_users = blocked_users
		self.debug = debug

	def handle_comment(self, submission):
		if not p.match(submission.body):
			return
		self._debug("---")
		self._debug("Post (" + submission.author.name + "): " + submission.body)
		
		self.total_times += 1
		time_since = (datetime.now() - self.last_time)
		
		# TODO: Store this better
		reply = "**Last mention of Overwatch: ~~%s~~ just now.**  \nTotal mentions of OW: %s  \n\n^^I'm ^^a ^^bot. ^^Beep ^^Boop. ^^Owner: ^^tcmalloc" % (time_since, self.total_times)
		
		self._debug(reply)
		try: 
			if submission.author.name in self.blocked_users:
				self._debug("Blocked: Don't reply")
				return
			else:
				# get the top-most comment
				ancestor = submission
				refresh_counter = 0
				while not ancestor.is_root:
					ancestor = ancestor.parent()
					if refresh_counter % 9 == 0:
						ancestor.refresh()
					refresh_counter += 1

				# check if any of the replies are ours
				replies = ancestor.replies.list()
				ours = [x for x in replies if x.author.name == self.username]
				print(ours)	
				# if not, reply 
				if len(ours) < 1:
					self._debug("Seems fine. Reply")
					if not self.debug:
						submission.reply(reply)
				else:
					self._debug("Already replied to this thread.")
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
			if created < self.last_checked:
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
