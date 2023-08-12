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


'''
@bot.callback_query_handler(func=lambda callback: callback.data in ['btn4'])
def add_event(callback):
    inf = []
    for question in slovik:
        sent = bot.send_message(callback.message.chat.id, text=question)
        bot.register_next_step_handler(sent, name)
    event = get_and_add_event(inf)
    print(inf)

def name(message):
    global inf
    message_to_save = message.text
    inf.append(message_to_save)
'''
# Словарь для отслеживания состояний пользователей
user_states = {}


# Класс для представления вопросов
class Question:
    def __init__(self, text, options):
        self.text = text
        self.options = options

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


@bot.callback_query_handler(func=lambda callback: callback.data in ['btn4'])
def start_survey(callback):
    user_id = callback.message.chat.id
    user_states[user_id] = 0  # Установка начального состояния
    question = questions[user_states[user_id]]
    bot.send_message(user_id, question.text)


@bot.callback_query_handler(func=lambda callback: callback.data == 'btn6')
def add_new_theme(callback):
    sent = bot.send_message(callback.message.chat.id, text='Добавте тему')
    bot.register_next_step_handler(sent, review)


@bot.message_handler(func=lambda message: message.text in allthems())
def handle_color(message):
    user_id = message.chat.id
    user_states[user_id] += 1  # Переход к следующему вопросу

    if user_states[user_id] < len(questions):
        question = questions[user_states[user_id]]

    else:
        bot.send_message(user_id, "Спасибо за участие в опросе!")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) is not None)
def handle_question(message):
    user_id = message.chat.id
    user_states[user_id] += 1
    if user_states[user_id] < len(questions):
        question = questions[user_states[user_id]]
        if question.text == 'Выбирите тему':
            active_session = db_session.create_session()
            theme = active_session.query(Theme).filter().all()
            kb = types.InlineKeyboardMarkup(row_width=3)

            for i in theme:
                print(i.id, allthems())
                btn = types.InlineKeyboardButton(text=i.theme_name, callback_data=i.id)
                kb.add(btn)
            bot.send_message(message.chat.id,
                             text=question.text,
                             reply_markup=kb
                             )
        else:
            bot.send_message(user_id, question.text)
    else:
        bot.send_message(user_id, "Спасибо за участие в опросе!")


@bot.callback_query_handler(func=lambda callback: int(callback.data) in allthems())
def print_all_need(callback):
    active_session = db_session.create_session()
    theme = active_session.query(Theme).filter(Theme.id == callback.data).first()
    print(theme)
    bot.send_message(callback.message.chat.id, text=theme.theme_name)



def review(message):
    message_to_save = message.text
    theme = get_and_make_theme(message_to_save)
    bot.send_message(message.chat.id, text=' Добавлена тема: ' + str(theme.theme_name))
    print(message_to_save)


def bot_thread():
    bot.polling()
    bot.polling(none_stop=True)


def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    db_session.global_init(
        sql_type="MYSQL"
    )
    questions = [
        Question("Добавте название", []),
        Question("Добавте описание", []),
        Question("Добавте фото(необязательно)", []),
        Question("Добавте дату", []),
        Question("Добавте ссылку(необязательно)е", []),
        Question("Выбирите тему", allthems())
    ]
    scheduler_thread = threading.Thread(target=scheduler_thread)
    bot_thread = threading.Thread(target=bot_thread)

    scheduler_thread.start()
    bot_thread.start()

    scheduler_thread.join()
    bot_thread.join()
