from handlers import meme_handler, vote_handler

import telebot

BOT_TOKEN = '936423319:AAHIzkoM_Sos-epjSngJDGv_YJTAS6Bv9oo'
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
