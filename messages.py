from datetime import datetime
import re

p = re.compile(r'blockme', re.IGNORECASE)

class MessageHandler:
	def __init__(self, comment_handler, last_checked=datetime.now(), debug=False):
		self.comment_handler = comment_handler
		self.last_checked = last_checked or datetime.now()
		self.debug = debug

	def handle(self, r):
		self._debug("Checking messages...")
		# check through our pms
		messages = r.inbox.messages()

		for message in messages:
			# stop if we've checked this one already
			if not message.author or message.author.name == r.user.me().name:
				continue
			if datetime.utcfromtimestamp(int(message.created_utc)) <= self.last_checked:
				break
			# if someone's asked us to block them
			if p.match(message.subject):
				# tell the comment handler
				self.comment_handler.block_user(message.author)

				# then message them back
				self.confirm_block(r, message.author)
			else:
				print("Unrecognised message (/u/" + message.author.name + "): " + message.subject + ": " + message.body)
		self.last_checked = datetime.now()

	def confirm_block(self, r, u):
		u.message("Blocked Successfully", "I won't reply to you anymore, but I'll still change the counter when you mention overwatch. ;)")	

	# logs if we're currently debugging
	def _debug(self, msg):
		if self.debug:
			print(msg)
