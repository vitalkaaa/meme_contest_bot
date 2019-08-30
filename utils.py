from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker
from telebot import types


@contextmanager
def session_scope(engine):
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.expunge_all()
        session.close()


def vote_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for i in range(7):
        callback_data = f'{i + 1}'
        buttons.append(types.InlineKeyboardButton(text=str(i + 1), callback_data=callback_data))

    keyboard.row(*buttons)
    return keyboard
