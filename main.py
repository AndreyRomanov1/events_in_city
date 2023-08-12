import time
from datetime import datetime

import telebot
from telebot import types
import schedule
import threading

import config
from mailing_services import create_dict_of_users_and_their_posts, get_users_for_mailing, get_posts_for_period
from services import *

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    tg_id = message.from_user.id
    user = get_or_create_user(telegram_id=tg_id)
    kb = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton(text='Мероприятия на сегодня', callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text='Мероприятия на неделю', callback_data='btn2')
    btn3 = types.InlineKeyboardButton(text='Подписаться на рассылку', callback_data='btn3')
    btn4 = types.InlineKeyboardButton(text='Добавить мероприятие', callback_data='btn4')
    btn5 = types.InlineKeyboardButton(text='Посмотреть статистику', callback_data='btn5')
    btn6 = types.InlineKeyboardButton(text='Добавить тему', callback_data='btn6')
    if user.is_admin:
        kb.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.chat.id,
                         text='Привет! Я телеграм бот "", а вы мой администратор. Я могу делать рассылки про события в Екатеринбурге или могу рассказать про то, какие мероприятия будут в ближайшие дни. Что ты хочешь сделать?',
                         reply_markup=kb
                         )
    else:
        kb.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id,
                         text='Привет! Я телеграм бот "". Я могу делать рассылки про события в Екатеринбурге или могу рассказать про то, какие мероприятия будут в ближайшие дни. Что ты хочешь сделать?',
                         reply_markup=kb
                         )


@bot.callback_query_handler(func=lambda callback: callback.data in ['btn1', 'btn2', 'btn3'])
def check_callback_data(callback):
    if callback.data == 'btn1':
        bot.send_message(callback.message.chat.id, 'daily_news')
    elif callback.data == 'btn2':
        bot.send_message(callback.message.chat.id, 'weakly_news')
    elif callback.data == 'btn3':
        active_session = db_session.create_session()
        theme = active_session.query(Theme).filter().all()
        kb = types.InlineKeyboardMarkup(row_width=3)
        for i in theme:
            print(i.theme_name)
            btn = types.InlineKeyboardButton(text=i.theme_name, callback_data='btnx')
            kb.add(btn)
        bot.send_message(callback.message.chat.id,
                         text='Выберите интересующие темы',
                         reply_markup=kb
                         )


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn6')
def add_new_theme(callback):
    sent = bot.send_message(callback.message.chat.id, text='Добавте тему')
    bot.register_next_step_handler(sent, review)


def review(message):
    message_to_save = message.text
    theme = get_and_make_theme(message_to_save)
    print(message_to_save)


def bot_thread():
    db_session.global_init(
        sql_type="MYSQL"
    )
    bot.polling(none_stop=True)


def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)


def send_daily_message():
    mailing(
        type_mailing=1,
        period_length_in_days=1
    )


def send_weekly_message():
    mailing(
        type_mailing=2,
        period_length_in_days=7
    )


def mailing(type_mailing: int, period_length_in_days: int):
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
    scheduler_thread = threading.Thread(target=scheduler_thread)
    bot_thread = threading.Thread(target=bot_thread)

    scheduler_thread.start()
    bot_thread.start()

    scheduler_thread.join()
    bot_thread.join()
