from datetime import datetime, timedelta

import os
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from utils import session_scope

print('connect to DB')
Base = declarative_base()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")


engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}', echo=False)
# engine = create_engine('sqlite:///db.sqlite', echo=False)


class Meme(Base):
    __tablename__ = 'memes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    posted_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    msg_id = Column(Integer)
    chat_id = Column(Integer)

    def __init__(self, user_id, msg_id, chat_id):
        self.posted_at = datetime.utcnow().replace(microsecond=0)
        self.user_id = user_id
        self.msg_id = msg_id
        self.chat_id = chat_id

    def save(self):
        with session_scope(engine) as session:
                session.add(self)
                print('detect meme')
                session.commit()
        return self

    @staticmethod
    def get_meme(chat_id, msg_id):
        with session_scope(engine) as session:
            return session.query(Meme).filter_by(chat_id=chat_id, msg_id=msg_id).first()

    @staticmethod
    def get_last_meme(chat_id=None, user_id=None):
        with session_scope(engine) as session:
            query = session.query(Meme)

            if user_id is not None:
                query = query.filter(Meme.user_id == user_id)

            if chat_id is not None:
                query = query.filter(Meme.chat_id == chat_id)

            last_meme = query.order_by(Meme.posted_at.desc()).first()
            return last_meme


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    voted_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    msg_id = Column(Integer)
    chat_id = Column(Integer)
    mark = Column(Integer)

    def __init__(self, user_id, chat_id, msg_id, mark):
        self.voted_at = datetime.utcnow().replace(microsecond=0)
        self.user_id = user_id
        self.chat_id = chat_id
        self.msg_id = msg_id
        self.mark = mark

    def save(self):
        with session_scope(engine) as session:
            session.add(self)
            print('voted', self.msg_id)
            session.commit()
        return self

    @staticmethod
    def is_voted(user_id, chat_id, msg_id):
        with session_scope(engine) as session:
            query = session.query(Vote).filter_by(user_id=user_id, chat_id=chat_id, msg_id=msg_id)
            is_marked = query.count() > 0
            return is_marked

    @staticmethod
    def get_chat_ids():
        with session_scope(engine) as session:
            chats = session.query(Vote.chat_id).group_by(Vote.chat_id).all()
            return [chat_id[0] for chat_id in chats]

    @staticmethod
    def get_votes(chat_id):
        with session_scope(engine) as session:
            chats = session.query(Vote).filter_by(chat_id=chat_id).all()
            return chats

    @staticmethod
    def get_daily_rating(chat_id):
        with session_scope(engine) as session:
            query = session.query(Vote.msg_id, func.avg(Vote.mark), Vote.user_id).filter_by(chat_id=chat_id)
            query = query.filter(Vote.chat_id == chat_id, Vote.voted_at > datetime.utcnow() - timedelta(hours=24))
            query = query.group_by(Vote.mark)
            query = query.order_by(func.avg(Vote.mark))
            yield query.all()[::-1]


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    registred_at = Column(DateTime)
    telegram_id = Column(Integer)
    chat_id = Column(Integer)
    points = Column(Integer, default=0)
    username = Column(String)

    def __init__(self, telegram_id, chat_id, username):
        self.registred_at = datetime.utcnow().replace(microsecond=0)
        self.points = 0
        self.username = username
        self.telegram_id = telegram_id
        self.chat_id = chat_id

    def save(self):
        with session_scope(engine) as session:
            session.add(self)
            print('new user', self.id)
            session.commit()
        return self

    def save_if_not_exists(self):
        if not User.is_exists(self.chat_id, self.telegram_id):
            return User(self.telegram_id, self.chat_id, self.username).save()
        else:
            return self

    @staticmethod
    def get(chat_id, telegram_id):
        with session_scope(engine) as session:
            return session.query(User).filter_by(chat_id=chat_id, telegram_id=telegram_id).first()

    @staticmethod
    def get_rating(chat_id):
        with session_scope(engine) as session:
            return session.query(User).filter_by(chat_id=chat_id).order_by(User.points).all()

    @staticmethod
    def is_exists(chat_id, telegram_id):
        with session_scope(engine) as session:
            user = session.query(User).filter_by(telegram_id=telegram_id, chat_id=chat_id).first()
            return user is not None

    @staticmethod
    def add_points(user_id, points):
        with session_scope(engine) as session:
            user = session.query(User).filter_by(id=user_id).first()
            user.points += points


# Создание таблицы
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    # for vote in Vote.get_votes(-364882467):
    #     print(vote.user_id, vote.mark, vote.chat_id, vote.msg_id)
