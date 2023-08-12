from datetime import datetime

from db import db_session
from db.post import Post
from db.theme import Theme
from db.user import User


def get_or_create_user(telegram_id: int) -> User:
    """Возвращает пользователя по telegram_id и создаёт его, если его нет"""
    active_session = db_session.create_session()
    user = active_session.query(User).filter(User.telegram_id == telegram_id)
    if list(user):
        return user[0]
    else:
        new_user = User(
            telegram_id=telegram_id,
        )
        active_session.add(new_user)
        active_session.commit()
        user = list(active_session.query(User).filter(User.telegram_id == telegram_id))[0]
        return user


def get_and_make_theme(theme_name: str) -> Theme:
    active_session = db_session.create_session()
    theme = active_session.query(Theme).filter(Theme.theme_name == theme_name)
    if list(theme):
        return theme[0]
    else:
        new_theme = Theme(
            theme_name=theme_name,
        )
        print(new_theme)
        active_session.add(new_theme)
        active_session.commit()
        theme = list(active_session.query(Theme).filter(Theme.theme_name == theme_name))[0]
        return theme


def get_and_add_event(user_id: int, name_event: str, description_event: str, image_event, date,
                      url, theme_id: int):
    post = Post()
    post.title = name_event
    post.text = description_event
    # post.image = image_event
    post.theme_id = theme_id
    post.user_id = user_id
    date = date.split('.')
    post.datetime_of_event = datetime(year=int(date[-1]), month=int(date[-2]), day=int(date[-3]), hour=0, minute=0)
    post.url = url
    db_sess = db_session.create_session()
    db_sess.add(post)
    db_sess.commit()


def allthems():
    active_session = db_session.create_session()
    themes = active_session.query(Theme).filter().all()
    themelist = []
    for i in themes:
        themelist.append(i.id)
    return themelist
