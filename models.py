from datetime import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from utils import session_scope

Base = declarative_base()
engine = create_engine('sqlite:///db.sqlite', echo=False)


class Meme(Base):
    __tablename__ = 'memes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    posted_at = Column(DateTime)
    user_id = Column(Integer)
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
                print('saving')
                session.commit()

    @staticmethod
    def get_last_meme(chat_id=None, user_id=None):
        with session_scope(engine) as session:
            query = session.query(Meme)

            if user_id is not None:
                query = query.filter(Meme.user_id == user_id)

            if chat_id is not None:
                query = query.filter(Meme.chat_id == chat_id)

            print('getting last meme')
            last_meme = query.order_by(Meme.posted_at.desc()).first()
            return last_meme


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    voted_at = Column(DateTime)
    user_id = Column(Integer)
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
            session.commit()

    @staticmethod
    def is_voted(user_id, chat_id, msg_id):
        with session_scope(engine) as session:
            query = session.query(Vote).filter_by(user_id=user_id, chat_id=chat_id, msg_id=msg_id)
            is_marked = query.count() > 0
            return is_marked

# Создание таблицы
if __name__ == '__main__':
    Base.metadata.create_all(engine)

