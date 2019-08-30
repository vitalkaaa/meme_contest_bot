import os

from handlers import meme_handler, vote_handler

import telebot

from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(content_types=['text', 'video', 'photo'])
def message_handler(message):
    meme_handler(bot, message)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Коллбеки на кнопки"""
    vote_handler(bot, call)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
