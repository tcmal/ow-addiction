from main import Bot

bot = Bot(True)

try:
	bot.main_loop(10)
except KeyboardInterrupt:
	bot.save()
