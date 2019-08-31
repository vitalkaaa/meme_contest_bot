import os

from meme_bot import MemeBot
from models import init_models

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = MemeBot(BOT_TOKEN)


@bot.message_handler(content_types=['text', 'video', 'photo', 'document'])
def message_handler(message):
    bot.meme_handler(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.vote_handler(call)


if __name__ == '__main__':
    init_models()

    bot.run_pooling()
    bot.run_scheduler()


