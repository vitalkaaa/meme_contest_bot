import os

from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv('../')
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)
exit(0)
bot = TeleBot(BOT_TOKEN)


@bot.message_handler(content_types=['text', 'video', 'photo', 'document'])
def message_handler(message):
    bot.send_message(message.chat.id, message.text)

bot.polling(none_stop=True)
