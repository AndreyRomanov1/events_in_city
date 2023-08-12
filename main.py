import threading
import time

import schedule
import telebot

import config
from mailing_services import create_dict_of_users_and_their_posts, get_users_for_mailing, get_posts_for_period
from services import *
import texts

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    tg_id = message.from_user.id
    user = get_or_create_user(telegram_id=tg_id)
    kb = create_main_keyboard(admin_level=user.admin_level)
    text = texts.START_TEXT_FOR_USERS if not user.admin_level else texts.START_TEXT_FOR_ADMIN
    bot.send_message(message.chat.id, text=text, reply_markup=kb)


user_states = {}  # Словарь для отслеживания состояний пользователей


class Question:
    """Класс для представления вопросов"""

    def __init__(self, text, options):
        self.text = text
        self.options = options


# @bot.callback_query_handler(
#     func=lambda callback: callback.data in ['btn_3_subscribe_to_mailing'])
# def check_callback_data(callback):
#     if callback.data == 'btn_3_subscribe_to_mailing':


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_1_event_today')
def events_of_today(callback):
    """Отправляет пользователю список постов с мероприятиями на сегодня"""
    all_posts = get_posts_for_period(start_date_of_period=datetime.now(), period_length_in_days=1)
    for post in all_posts:
        bot.send_message(callback.message.chat.id, post.print_post())


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_2_event_week')
def events_of_week(callback):
    """Отправляет пользователю список постов с мероприятиями на неделю вперёд"""
    all_posts = get_posts_for_period(start_date_of_period=datetime.now(), period_length_in_days=7)
    for post in all_posts:
        bot.send_message(callback.message.chat.id, post.print_post())


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_3_subscribe_to_mailing')
def add_theme_to_mailing(callback):
    """Добавление темы для рассылки"""
    active_session = db_session.create_session()
    themes = active_session.query(Theme).filter().all()
    kb = types.InlineKeyboardMarkup(row_width=3)
    for theme in themes:
        print(theme.theme_name)
        btn = types.InlineKeyboardButton(text=theme.theme_name, callback_data=f'btnTheme_{theme.id}')
        kb.add(btn)
    bot.send_message(callback.message.chat.id,
                     text='Выберите интересующую тему для рассылки',
                     reply_markup=kb
                     )


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_6_add_theme')
def add_new_theme(callback):
    """Создание новой темы"""
    sent = bot.send_message(callback.message.chat.id, text='Введите название новой темы')
    bot.register_next_step_handler(sent, review)


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn_4_add_event')
def start_survey(callback):
    """Создание нового поста о мероприятии"""
    global data
    user_id = callback.message.chat.id
    data = [user_id]
    user_states[user_id] = 0  # Установка начального состояния
    question = questions[user_states[user_id]]
    bot.send_message(user_id, question.text)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) is not None)
def handle_question(message):
    global data
    data.append(message.text)
    user_id = message.chat.id
    user_states[user_id] += 1
    if user_states[user_id] < len(questions):
        question = questions[user_states[user_id]]
        if question.text == 'Выберите тему':
            active_session = db_session.create_session()
            theme = active_session.query(Theme).filter().all()
            kb = types.InlineKeyboardMarkup(row_width=3)

            for i in theme:
                btn = types.InlineKeyboardButton(text=i.theme_name, callback_data=i.id)
                kb.add(btn)
            bot.send_message(message.chat.id,
                             text=question.text,
                             reply_markup=kb
                             )
        else:
            bot.send_message(user_id, question.text)
    else:
        bot.send_message(user_id, "Пост мероприятия сохранён")


@bot.callback_query_handler(func=lambda callback: int(callback.data) in get_list_all_theme_ids())
def print_all_need(callback):
    global data
    active_session = db_session.create_session()
    theme = active_session.query(Theme).filter(Theme.id == callback.data).first()
    data.append(theme.id)
    bot.send_message(callback.message.chat.id, text=theme.theme_name)
    print(data)
    get_and_add_event(*data)
    bot.send_message(callback.message.chat.id, text='Ваше мероприятие было добавлено')


def review(message):
    message_to_save = message.text
    theme = get_and_make_theme(message_to_save)
    bot.send_message(message.chat.id, text=' Добавлена тема: ' + str(theme.theme_name))
    print(message_to_save)


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
            bot.send_message(user.telegram_id, post.print_post())


schedule.every().monday.at("10:00").do(send_weekly_message)
schedule.every().day.at("10:00").do(send_daily_message)

if __name__ == '__main__':
    db_session.global_init(
        sql_type="MYSQL"
    )
    questions = [
        Question("Добавьте название", []),
        Question("Добавьте описание", []),
        Question("Добавьте фото(необязательно)", []),
        Question("Добавьте дату", []),
        Question("Добавьте ссылку(необязательно)е", []),
        Question("Выберите тему", get_list_all_theme_ids())
    ]
    scheduler_thread = threading.Thread(target=scheduler_thread)
    bot_thread = threading.Thread(target=bot_thread)

    scheduler_thread.start()
    bot_thread.start()

    scheduler_thread.join()
    bot_thread.join()
