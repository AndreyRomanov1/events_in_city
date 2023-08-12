import telebot
from telebot import types

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
    if user.is_admin:
        kb.add(btn1, btn2, btn3, btn4, btn5)
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


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    if callback.data == 'btn1':
        bot.send_message(callback.message.chat.id, 'daily_news')
    elif callback.data == 'btn2':
        bot.send_message(callback.message.chat.id, 'weakly_news')
    elif callback.data == 'btn3':
        kb = types.InlineKeyboardMarkup(row_width=3)
        btn4 = types.InlineKeyboardButton(text='Спорт', callback_data='sport')
        btn5 = types.InlineKeyboardButton(text='Музыка', callback_data='music')
        btn6 = types.InlineKeyboardButton(text='Экология', callback_data='eco')
        kb.add(btn4, btn5, btn6)
        bot.send_message(callback.message.chat.id,
                         text='Выберите интересующие темы',
                         reply_markup=kb
                         )


if __name__ == '__main__':
    db_session.global_init(
        sql_type="MYSQL"
    )
    bot.polling()
