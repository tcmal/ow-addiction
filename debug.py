from main import Bot
import os

bot = Bot(user_agent=os.environ['USER_AGENT'], client_id=os.environ['CLIENT_ID'], 
            client_secret=os.environ['CLIENT_SECRET'], username=os.environ['REDDIT_USERNAME'],
            password=os.environ['REDDIT_PASSWORD'], subreddit=os.environ['SUBREDDIT'], debug=True)

try:
	bot.main_loop(10)
except KeyboardInterrupt:
	bot.save()
