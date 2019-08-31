import os

from dotenv import load_dotenv

from meme_bot import MemeBot

load_dotenv('../')
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = MemeBot(BOT_TOKEN)


@bot.message_handler(content_types=['text', 'video', 'photo', 'document'])
def message_handler(message):
    bot.meme_handler(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.vote_handler(call)


if __name__ == '__main__':
    bot.run_pooling()
    bot.run_scheduler()


