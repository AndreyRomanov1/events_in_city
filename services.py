from datetime import datetime
from random import randint

from telebot import types

from db import db_session
from db.mailing_list import MailingList
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
        active_session.add(new_theme)
        active_session.commit()
        theme = list(active_session.query(Theme).filter(Theme.theme_name == theme_name))[0]
        return theme


def get_and_add_event(date, user_id: int, name_event: str, description_event: str, image_event,
                      url, theme_id: int):
    post = Post()
    post.title = name_event
    post.text = description_event
    # post.image = image_event
    post.theme_id = theme_id
    post.user_id = get_or_create_user(telegram_id=user_id).id
    date = date.split('.')
    post.datetime_of_event = datetime(year=int(date[-1]), month=int(date[-2]), day=int(date[-3]), hour=0, minute=0)
    post.url = url
    db_sess = db_session.create_session()
    db_sess.add(post)
    db_sess.commit()


def get_list_all_theme_ids() -> list[int]:
    active_session = db_session.create_session()
    themes = list(map(lambda x: x.id, active_session.query(Theme).filter().all()))
    return themes


def create_main_keyboard(user: User) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=3)
    btn_1_event_today = types.InlineKeyboardButton(text='Мероприятия на сегодня', callback_data='btn_1_event_today')
    btn_2_event_week = types.InlineKeyboardButton(text='Мероприятия на неделю', callback_data='btn_2_event_week')

    btn_8_mailing = types.InlineKeyboardButton(text='Рассылка', callback_data='btn_8_mailing')
    btn_3_subscribe_to_theme_for_mailing = types.InlineKeyboardButton(text='Добавить тему для рассылки',
                                                                      callback_data='btn_3_subscribe_to_theme_for_mailing')
    btn_6_add_theme = types.InlineKeyboardButton(text='Добавить тему', callback_data='btn_6_add_theme')
    btn_4_add_event = types.InlineKeyboardButton(text='Добавить мероприятие', callback_data='btn_4_add_event')

    btn_7_add_admin_1 = types.InlineKeyboardButton(text='Добавить админа 1 уровня',
                                                   callback_data='btn_7_add_admin_1')
    btn_9_add_admin_2 = types.InlineKeyboardButton(text='Добавить админа 2 уровня',
                                                   callback_data='btn_9_add_admin_2')

    kb.add(btn_1_event_today, btn_2_event_week)
    kb.add(btn_8_mailing, btn_3_subscribe_to_theme_for_mailing)

    if user.admin_level >= 1:
        kb.add(btn_6_add_theme, btn_4_add_event)
    if user.admin_level >= 2:
        kb.add(btn_7_add_admin_1, btn_9_add_admin_2)
    return kb


def add_theme_for_user(user_id, theme_id):
    active_session = db_session.create_session()
    mailingList = active_session.query(MailingList).filter(MailingList.user_id == user_id,
                                                           MailingList.theme_id == theme_id)
    if list(mailingList):
        pass
    else:
        new_mailingList = MailingList(
            user_id=user_id,
            theme_id=theme_id
        )
        active_session.add(new_mailingList)
        active_session.commit()


def create_new_admin(referral_code: str, telegram_id: int) -> str:
    active_session = db_session.create_session()
    user = active_session.query(User).filter(User.telegram_id == telegram_id).first()
    referral_user = active_session.query(User).filter(User.referral_code == referral_code)
    if list(referral_user):
        referral_user: User = referral_user[0]
    else:
        return "Неверный код для приглашения"
    if user.admin_level < int(referral_code.split("_")[1]):
        referral_user.referral_code = None
        user.admin_level = int(referral_code.split("_")[1])
        user.referral_user = referral_user.id
        active_session.commit()
        return f"Теперь вы администратор {referral_code.split('_')[1]} уровня"
    else:
        return "Вы уже администратор этого уровня или выше"


def create_referral_code(telegram_id: int, admin_level: int):
    active_session = db_session.create_session()
    user = active_session.query(User).filter(User.telegram_id == telegram_id).first()
    user.referral_code = f"{user.telegram_id}_{admin_level}_{randint(100000, 999999)}"
    active_session.commit()
    return user.referral_code


def create_kb_for_add_theme(telegram_id:int) -> types.InlineKeyboardMarkup:
    active_session = db_session.create_session()
    themes_0 = active_session.query(Theme).filter().all()
    themes_dict = {}
    for theme in themes_0:
        themes_dict[theme.id] = theme.theme_name
    themes = set(map(lambda x: x.id, themes_0))
    user = get_or_create_user(telegram_id)
    us_theme = user.get_themes_for_mailing()
    print(user, themes, us_theme)
    themes -= us_theme
    kb = types.InlineKeyboardMarkup(row_width=3)
    btn = types.InlineKeyboardButton(text='Выйти', callback_data='out')
    kb.add(btn)
    button = []
    for theme in themes:
        btn = types.InlineKeyboardButton(text=themes_dict[theme], callback_data=f'btnTheme_{theme}')
        button.append(btn)
    kb.add(*button)
    return kb
