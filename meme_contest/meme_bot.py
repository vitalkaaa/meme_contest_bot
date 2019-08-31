import time
from datetime import datetime, timedelta
from threading import Thread

import schedule
import telebot
from models import Meme, Vote, User
from telebot.apihelper import ApiException

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


class MemeBot(telebot.TeleBot):
    def __init__(self, token):
        super(MemeBot, self).__init__(token=token)

    def command_handler(self, message):
        chat_id = str(message.chat.id)

        if message.text.split(' ')[0].startswith('/rating'):
            self.send_message(chat_id, User.get_rating(chat_id), parse_mode='HTML')

    def meme_handler(self, message: telebot.types.Message):
        telegram_id = message.from_user.id
        chat_id = str(message.chat.id)
        msg_id = message.message_id
        username = '@' + message.from_user.username if message.from_user.username else message.from_user.first_name

        get_cached_meme_posted_at(chat_id, telegram_id)
        if (datetime.utcnow() - last_meme_posted_at_cache[chat_id][telegram_id]).seconds > 10:
            if message.content_type != 'text':
                last_meme_posted_at_cache[chat_id][telegram_id] = datetime.utcnow().replace(microsecond=0)
                user = User(telegram_id, chat_id, username).save_if_not_exists()
                Meme(user.id, msg_id, chat_id).save()
                self.send_message(chat_id, 'Mark this meme',
                                  reply_to_message_id=msg_id,
                                  reply_markup=vote_keyboard())
            else:
                if message.text.startswith('/'):
                    self.command_handler(message)

    def vote_handler(self, call: telebot.types.CallbackQuery):
        telegram_id = call.from_user.id
        chat_id = str(call.message.chat.id)
        msg_id = call.message.message_id
        mark = int(call.data)
        username = '@' + call.from_user.username if call.from_user.username else call.from_user.first_name

        user = User.get(chat_id, telegram_id)
        if not user:
            user = User(telegram_id, chat_id, username).save()

        meme = Meme.get_meme(chat_id, msg_id)
        if meme and not Vote.is_voted(user.id, meme.id):
            Vote(user.id, meme.id, mark).save()
            self.answer_callback_query(call.id, text='You voted')
        else:
            self.answer_callback_query(call.id, text='You have already voted')

    def send_daily_results(self):
        medals = ['🥇', '🥈', '🥉']
        for chat_id in Vote.get_chat_ids():
            for top in Vote.get_daily_rating(chat_id):
                for i, t in enumerate(top[:3]):
                    User.add_points(t[2], 3 - i)
                    try:
                        self.send_message(chat_id, f'{medals[i]} <b>+{3 - i}</b> баллa',
                                          reply_to_message_id=t[0] - 1, parse_mode='HTML')
                    except ApiException as err:
                        print(err)

            try:
                self.send_message(chat_id, User.get_rating(chat_id), parse_mode='HTML')
            except ApiException as err:
                print(err)

    def run_scheduler(self):
        def scheduler_worker():
            # schedule.every(4).seconds.do(self.send_daily_results)
            schedule.every().day.at("00:00").do(self.send_daily_results)

            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = Thread(target=scheduler_worker, args=())
        thread.daemon = True
        thread.run()

    def run_pooling(self):
        self.polling(none_stop=True, interval=0)
