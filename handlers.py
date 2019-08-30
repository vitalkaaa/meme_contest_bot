from datetime import datetime, timedelta

import telebot

from models import Meme, Vote
from utils import vote_keyboard

last_meme_posted_at_cache = dict()


def get_cached_meme_posted_at(chat_id, user_id):
    if not last_meme_posted_at_cache.get(chat_id):
        last_meme_posted_at_cache[chat_id] = dict()

    if not last_meme_posted_at_cache[chat_id].get(user_id):
        last_meme = Meme.get_last_meme(chat_id, user_id)
        if last_meme:
            last_meme_posted_at_cache[chat_id][user_id] = last_meme.posted_at
        else:
            last_meme_posted_at_cache[chat_id][user_id] = datetime.now() - timedelta(hours=1)


def meme_handler(bot: telebot.TeleBot, message: telebot.types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = message.message_id

    get_cached_meme_posted_at(chat_id, user_id)
    if (datetime.utcnow() - last_meme_posted_at_cache[chat_id][user_id]).seconds > 10:
        if message.content_type != 'text':
            last_meme_posted_at_cache[chat_id][user_id] = datetime.utcnow().replace(microsecond=0)
            Meme(user_id, msg_id, chat_id).save()
            bot.send_message(chat_id, 'Mark this meme',
                             reply_to_message_id=msg_id,
                             reply_markup=vote_keyboard())


def vote_handler(bot, call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    mark = int(call.data)

    if not Vote.is_voted(user_id, chat_id, msg_id):
        Vote(user_id, chat_id, msg_id, mark).save()
        bot.answer_callback_query(call.id, text='You voted')
    else:
        bot.answer_callback_query(call.id, text='You have already voted')
