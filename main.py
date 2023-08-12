import time

import telebot
from telebot import types
import schedule
import threading

import config
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


if __name__ == '__main__':
    db_session.global_init(
        sql_type="MYSQL"
    )
    bot.polling()


def bot_thread():
    bot.polling(none_stop=True)


def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

def send_weekly_message():
    chat_id = '880739918'
    message = "Привет! Еженедельное сообщение."
    bot.send_message(chat_id, message)

# schedule.every(5).seconds.do(send_weekly_message)

if __name__ == '__main__':
    db_session.global_init(
        sql_type="MYSQL"
    )
    bot_thread = threading.Thread(target=bot_thread)
    scheduler_thread = threading.Thread(target=scheduler_thread)

    bot_thread.start()
    scheduler_thread.start()

    bot_thread.join()
    scheduler_thread.join()