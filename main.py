import threading
import time
import re
import datetime

import schedule
import telebot

import config
import texts
from mailing_services import create_dict_of_users_and_their_posts, get_users_for_mailing, get_posts_for_period
from services import *

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    """Первый запуск бота у пользователя, регистрация пользователя"""
    telegram_id = message.chat.id
    user = get_or_create_user(telegram_id=telegram_id)
    kb = create_main_keyboard(user=user)
    text = texts.START_TEXT_FOR_USERS if not user.admin_level else texts.START_TEXT_FOR_ADMIN
    bot.send_message(telegram_id, text=text, reply_markup=kb)


@bot.callback_query_handler(func=lambda callback: callback.data == 'out')
def start(callback):
    telegram_id = callback.message.chat.id
    user = get_or_create_user(telegram_id=telegram_id)
    kb = create_main_keyboard(user=user)
    text = texts.START_TEXT_FOR_USERS if not user.admin_level else texts.START_TEXT_FOR_ADMIN
    bot.send_message(telegram_id, text=text, reply_markup=kb)


user_states = {}  # Словарь для отслеживания состояний пользователей


class Question:
    """Класс для представления вопросов"""

    def __init__(self, text, options):
        self.text = text
        self.options = options


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_1_event_today')
def events_of_today(callback):
    """Отправляет пользователю список постов с мероприятиями на сегодня"""
    telegram_id = callback.message.chat.id
    all_posts = get_posts_for_period(start_date_of_period=datetime.now(), period_length_in_days=1)
    for post in all_posts:
        send_post(telegram_id=telegram_id, post=post, bot=bot)


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_2_event_week')
def events_of_week(callback):
    """Отправляет пользователю список постов с мероприятиями на неделю вперёд"""
    telegram_id = callback.message.chat.id
    all_posts = get_posts_for_period(start_date_of_period=datetime.now(), period_length_in_days=7)
    for post in all_posts:
        send_post(telegram_id=telegram_id, post=post, bot=bot)


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_3_subscribe_to_theme_for_mailing')
def add_theme_to_mailing(callback):
    """Добавление темы для рассылки"""
    telegram_id = callback.message.chat.id

    kb = create_kb_for_add_theme(telegram_id=telegram_id)
    bot.send_message(telegram_id,
                     text='Выберите интересующую тему для рассылки',
                     reply_markup=kb
                     )


@bot.callback_query_handler(func=lambda callback: 'btnTheme_' in callback.data)
def add_theme(callback):
    """Добавление темы для рассылки"""
    telegram_id = callback.message.chat.id

    user = get_or_create_user(telegram_id)
    add_theme_for_user(user_id=user.id, theme_id=int(str(callback.data).split('_')[-1]))

    kb = create_kb_for_add_theme(telegram_id=telegram_id)
    bot.send_message(telegram_id,
                     text='Выберите интересующую тему для рассылки',
                     reply_markup=kb
                     )


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_6_add_theme')
def add_new_theme(callback):
    """Создание новой темы"""
    telegram_id = callback.message.chat.id

    sent = bot.send_message(telegram_id, text='Введите название новой темы')
    bot.register_next_step_handler(sent, review)


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_8_mailing')
def add_mailing(callback):
    kb = types.InlineKeyboardMarkup(row_width=3)
    btn_daily_mail = types.InlineKeyboardButton(text='Ежедневная рассылка',
                                                callback_data='btn_mail1')
    btn_weakly_mail = types.InlineKeyboardButton(text='Еженедельная рассылка',
                                                 callback_data='btn_mail2')
    btn_not_mailing = types.InlineKeyboardButton(text='Отказаться от рассылки',
                                                 callback_data='btn_mail0')
    kb.add(btn_daily_mail, btn_weakly_mail, btn_not_mailing)
    bot.send_message(callback.message.chat.id, text='Подпишитесь на нужный формат рассылки или откажитесь от нее.',
                     reply_markup=kb)


@bot.callback_query_handler(func=lambda callback: 'btn_mail' in callback.data)
def status_mailing(callback):
    telegram_id = callback.message.chat.id
    if callback.data == 'btn_mail1':
        bot.send_message(telegram_id, 'Вы подписались на ежедневную рассылку. Не забудте зайти и добавить ее темы!')
    elif callback.data == 'btn_mail2':
        bot.send_message(telegram_id, 'Вы подписались на еженедельную рассылку. Не забудте зайти и добавить ее темы!')
    else:
        bot.send_message(telegram_id, 'Вы отказались от рассылки.')
    active_session = db_session.create_session()
    user = active_session.query(User).filter(User.telegram_id == telegram_id).first()
    user.mailing_frequency = callback.data[-1]
    active_session.commit()
    user = get_or_create_user(telegram_id=telegram_id)
    kb = create_main_keyboard(user=user)
    text = texts.START_TEXT_FOR_USERS if not user.admin_level else texts.START_TEXT_FOR_ADMIN
    bot.send_message(telegram_id, text=text, reply_markup=kb)


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_4_add_event')
def start_survey(callback):
    """Создание нового поста о мероприятии"""
    global data
    telegram_id = callback.message.chat.id
    data = [telegram_id]
    user_states[telegram_id] = 0  # Установка начального состояния
    question = questions[user_states[telegram_id]]
    bot.send_message(telegram_id, question.text)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) is not None)
def handle_question(message):
    global data
    data.append(message.text)
    telegram_id = message.chat.id
    user_states[telegram_id] += 1
    if user_states[telegram_id] < len(questions):
        question = questions[user_states[telegram_id]]
        if question.text == 'Выберите тему':
            active_session = db_session.create_session()
            theme = active_session.query(Theme).filter().all()
            kb = types.InlineKeyboardMarkup(row_width=3)

            for i in theme:
                btn = types.InlineKeyboardButton(text=i.theme_name, callback_data=i.id)
                kb.add(btn)
            bot.send_message(telegram_id,
                             text=question.text,
                             reply_markup=kb
                             )
        elif question.text == 'Добавьте название':
            bot.send_message(telegram_id, text=question.text)
            match = re.fullmatch(r"\d\d.\d\d.\d\d\d\d\s\d\d:\d\d", message.text) # DD.MM.YYYY HH:MM
            try:
                day, month, year = map(int, message.text.split()[0].split("."))
                hour, minute = map(int, message.text.split()[1].split(":"))
                print(day,month,year,hour,minute)
                task = datetime(
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute)
            except ValueError:
                match = False
            if not match:
                bot.send_message(telegram_id,
                                 "Из-за некорректного ввода даты или времени пост мероприятия не был сохранён. Попробуйте снова")
                telegram_id = message.chat.id
                user = get_or_create_user(telegram_id=telegram_id)
                kb = create_main_keyboard(user=user)
                text = texts.START_TEXT_FOR_USERS if not user.admin_level else texts.START_TEXT_FOR_ADMIN
                bot.send_message(telegram_id, text=text, reply_markup=kb)
        else:
            bot.send_message(telegram_id, question.text)
    else:
        bot.send_message(telegram_id, "Пост мероприятия сохранён")


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_7_add_admin_1')
def create_referral_code_1(callback):
    telegram_id = callback.message.chat.id
    referral_code = create_referral_code(telegram_id=telegram_id, admin_level=1)
    bot.send_message(telegram_id, text=f"Ваш реферальный код: {referral_code}\nОн работает только на 1 раз. \
    Вы всегда можете забрать права администратора у админов 1 уровня")


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_9_add_admin_2')
def create_referral_code_2(callback):
    telegram_id = callback.message.chat.id
    referral_code = create_referral_code(telegram_id=telegram_id, admin_level=2)
    bot.send_message(telegram_id, text=f"Ваш реферальный код: {referral_code}\nОн работает только на 1 раз. \
    Помните, администратора 2 уровня нельзя удалить вручную")


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_10_remove_admin')
def remove_admin(callback):
    telegram_id = callback.message.chat.id
    active_session = db_session.create_session()
    admins_1_level: list[User] = active_session.query(User).filter(
        User.admin_level == 1
    ).all()
    remove_kb = types.InlineKeyboardMarkup()
    remove_btns = []
    for admin in admins_1_level:
        admin_info = bot.get_chat(admin.telegram_id)
        print(admin_info)
        remove_btns.append(types.InlineKeyboardButton(text=str(admin_info.first_name + " " + admin_info.username),
                                                      callback_data=f'btnRemoveAdmin_{admin.id}'))
    remove_kb.add(*remove_btns)
    bot.send_message(telegram_id,
                     text="Нажмите на имя администратора, которого необходимо удалить",
                     reply_markup=remove_kb
                     )


@bot.callback_query_handler(func=lambda callback: 'btnRemoveAdmin_' in callback.data)
def remove_admin_1_level(callback):
    telegram_id = callback.message.chat.id
    remove_admin_id = int(callback.data.split("_")[-1])
    active_session = db_session.create_session()
    remove_admin: User = active_session.query(User).filter(User.id == remove_admin_id).first()
    remove_admin.admin_level = 0
    active_session.commit()
    bot.send_message(telegram_id, text="Администратор удалён")


@bot.callback_query_handler(func=lambda callback: 'btnAddToFavourite_' in callback.data)
def add_post_to_favourite(callback):
    telegram_id = callback.message.chat.id
    user = get_or_create_user(telegram_id=telegram_id)
    active_session = db_session.create_session()
    favourite = Favourite(user_id=user.id, post_id=callback.data.split("_")[-1])
    active_session.add(favourite)
    active_session.commit()


@bot.callback_query_handler(func=lambda callback: 'btnRemoveFromFavourite_' in callback.data)
def delete_from_favourite(callback):
    telegram_id = callback.message.chat.id
    user = get_or_create_user(telegram_id=telegram_id)
    active_session = db_session.create_session()
    favourite = active_session.query(Favourite).filter(Favourite.user_id == user.id,
                                                       Favourite.post_id == callback.data.split("_")[-1]).first()
    active_session.delete(favourite)
    active_session.commit()


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_11_favourite_posts_user')
def favourite_posts_user(callback):
    telegram_id = callback.message.chat.id
    user = get_or_create_user(telegram_id=telegram_id)
    favourite_post_ids = user.get_favourite_post_ids()
    print(favourite_post_ids)
    active_session = db_session.create_session()
    posts = active_session.query(Post).filter(Post.id.in_(favourite_post_ids)).all()
    for post in posts:
        send_post(telegram_id=telegram_id, post=post, bot=bot)


@bot.callback_query_handler(func=lambda callback: int(callback.data) in get_list_all_theme_ids())
def print_all_need(callback):
    global data
    telegram_id = callback.message.chat.id
    active_session = db_session.create_session()
    theme = active_session.query(Theme).filter(Theme.id == callback.data).first()
    data.append(theme.id)
    bot.send_message(telegram_id, text=theme.theme_name)
    get_and_add_event(*data)
    bot.send_message(telegram_id, text='Ваше мероприятие было добавлено')


def review(message):
    telegram_id = message.chat.id
    message_to_save = message.text
    theme = get_and_make_theme(message_to_save)
    bot.send_message(telegram_id, text=' Добавлена тема: ' + str(theme.theme_name))


@bot.message_handler(func=lambda message: message.text and message.text.startswith("/admin "))
def create_new_admin_handler(message):
    """Добавление уровня администратора при верном реферальном коде"""
    telegram_id = message.chat.id
    referral_code = message.text.split()[1]
    answer_message = create_new_admin(referral_code=referral_code, telegram_id=telegram_id)
    bot.send_message(telegram_id, text=answer_message)


def bot_thread():
    """Поток телеграм бота"""
    bot.polling(none_stop=True)


def scheduler_thread():
    """Поток для выполнения рассылок по расписанию"""
    while True:
        schedule.run_pending()
        time.sleep(1)


def send_daily_message():
    """Ежедневная рассылка"""
    mailing(
        type_mailing=1,
        period_length_in_days=1
    )


def send_weekly_message():
    """Еженедельная рассылка"""
    mailing(
        type_mailing=2,
        period_length_in_days=7
    )


def mailing(type_mailing: int, period_length_in_days: int):
    """Рассылает всем пользователям списки постов с мероприятиями по интересным для них темам"""
    dict_of_users_and_their_posts = create_dict_of_users_and_their_posts(
        users_for_mailing=get_users_for_mailing(type_mailing=type_mailing),
        all_posts=get_posts_for_period(start_date_of_period=datetime.now(), period_length_in_days=period_length_in_days)
    )
    for user, posts in dict_of_users_and_their_posts.items():
        for post in posts:
            send_post(telegram_id=user.telegram_id, post=post, bot=bot)


schedule.every().monday.at("10:00").do(send_weekly_message)
schedule.every().day.at("10:00").do(send_daily_message)

if __name__ == '__main__':
    db_session.global_init(
        sql_type="MYSQL"
    )
    questions = [
        Question("Добавьте дату и время в формате дд.мм.гггг чч:мм", []),
        Question("Добавьте название", []),
        Question("Добавьте описание", []),
        Question("Добавьте фото", []),
        Question("Добавьте ссылку(необязательно)", []),
        Question("Выберите тему", get_list_all_theme_ids())
    ]
    scheduler_thread = threading.Thread(target=scheduler_thread)
    bot_thread = threading.Thread(target=bot_thread)

    scheduler_thread.start()
    bot_thread.start()

    scheduler_thread.join()
    bot_thread.join()
