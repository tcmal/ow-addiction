import json
import praw
import os
import time
from datetime import datetime
import calendar

from comments import CommentHandler

class Bot:
	def __init__(self, debug=False, user_agent=os.environ['USER_AGENT'], client_id=os.environ['CLIENT_ID'], 
				client_secret=os.environ['CLIENT_SECRET'], username=os.environ['REDDIT_USERNAME'],
				password=os.environ['REDDIT_PASSWORD'], subreddit=os.environ['SUBREDDIT']):
		
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

			self.comment_handler = CommentHandler(data["total_times"], 
				datetime.utcfromtimestamp(int(data["last_time"])), 
				datetime.utcfromtimestamp(int(data["last_checked"])), 
				data["blocked_users"],
				self.debug)

			print("Loaded past config.")
		
		except IOError:
			print("No past config.")
			self.comment_handler = CommentHandler()
	
	def save(self):
		total_times = self.comment_handler.total_times
		last_time = self.comment_handler.last_time
		last_checked = self.comment_handler.last_checked
		blocked_users = self.comment_handler.blocked_users

		with open("bot.json", "w") as f:
			json.dump({"blocked_users": blocked_users, 
				"total_times": total_times, 
				"last_time": calendar.timegm(last_time.timetuple()), 
				"last_checked": calendar.timegm(last_checked.timetuple())}, 
				f, indent="\t")

		print("Saved config.")

	def main_loop(self, delay):
		while True:
			# handle new messages
			# TODO
			# handle new comments
			self.comment_handler.handle(self.subreddit)

			# delay before looping again
			time.sleep(delay)