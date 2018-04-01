from main import Bot

bot = Bot()

try:
	bot.main_loop(5)
except KeyboardInterrupt:
	bot.save()