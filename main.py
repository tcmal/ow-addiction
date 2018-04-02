import json
import praw
import os
import time
from datetime import datetime
import calendar

from comments import CommentHandler
from messages import MessageHandler

class Bot:
	def __init__(self, debug=False, user_agent=None, client_id=None, client_secret=None, username=None, password=None, subreddit=None):

		self.debug = debug
		self.reddit = praw.Reddit(user_agent=user_agent,
				client_id=client_id,
				client_secret=client_secret,
				username=username, password=password)

		self.subreddit = self.reddit.subreddit(subreddit)

		try:
			with open("bot.json", "r") as f:
				data = json.load(f)

			if username not in data["blocked_users"]:
				data["blocked_users"].append(username)

			self.comment_handler = CommentHandler(self.reddit.user.me().name, data["total_times"], 
					datetime.utcfromtimestamp(int(data["last_time"])), 
					datetime.utcfromtimestamp(int(data["last_checked"])), 
					data["blocked_users"],
					self.debug)

			self.message_handler = MessageHandler(self.comment_handler, datetime.utcfromtimestamp(data["last_checked_msg"]), self.debug)

			print("Loaded past config.")

		except IOError:
			print("No past config.")
			self.comment_handler = CommentHandler(self.reddit.user.me().name, self.debug)
			self.message_handler = MessageHandler(self.comment_handler, None, self.debug)

	def save(self):
		total_times = self.comment_handler.total_times
		last_time = self.comment_handler.last_time
		last_checked = self.comment_handler.last_checked
		last_checked_msg = self.message_handler.last_checked
		blocked_users = self.comment_handler.blocked_users

		with open("bot.json", "w") as f:
			json.dump({"blocked_users": blocked_users, 
				"total_times": total_times, 
				"last_time": calendar.timegm(last_time.timetuple()), 
				"last_checked": calendar.timegm(last_checked.timetuple()),
				"last_checked_msg": calendar.timegm(last_checked_msg.timetuple())}, 
				f, indent="\t")

			print("Saved config.")

	def main_loop(self, delay):
		i = 0
		while True:
			# save every 5 loops
			if i >= 5:
				self.save()
				i = 0 
			
			# handle new messages
			self.message_handler.handle(self.reddit)
			# handle new comments
			self.comment_handler.handle(self.subreddit)
			
			i += 1

			# delay before looping again
			time.sleep(delay)
