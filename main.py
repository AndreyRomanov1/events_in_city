from db import db_session
import telebot
from telebot import types

bot = telebot.TeleBot('6692859743:AAETsyB1WGxOXaZg6SBeeONZNeeQFGkEEqw')


@bot.message_handler(commands=['start'])
def start(message):
    id_for_bd = message.from_user.id
    print(id_for_bd)
    kb = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton(text='Мероприятия на сегодня', callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text='Мероприятия на неделю', callback_data='btn2')
    btn3 = types.InlineKeyboardButton(text='Подписаться на рассылку', callback_data='btn3')
    kb.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     'Привет! Я телеграм бот "". Я могу делать рассылки про события в Екатеринбурге или могу рассказать про то, какие мероприятия будут в ближайшие дни. Что ты хочешь сделать?', reply_markup= kb
                     )

@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    if callback.data == 'btn1':
        bot.send_message(callback.message.chat.id, 'daily_news')
    elif callback.data == 'btn2':
        bot.send_message(callback.message.chat.id, 'weakly_news')
    elif callback.data == 'btn3':
        kb = types.InlineKeyboardMarkup(row_width=3)
        btn4 = types.InlineKeyboardButton(text='Спорт', callback_data='btn4')
        btn5 = types.InlineKeyboardButton(text='Музыка', callback_data='btn5')
        btn6 = types.InlineKeyboardButton(text='Экология', callback_data='btn6')
        kb.add(btn4, btn5, btn6)
        bot.send_message(callback.message.chat.id,
                         'Выбирите интересующие темы',
                         reply_markup=kb
                         )

bot.polling()
if __name__ == '__main__':
    db_session.global_init(
        sql_type="sqlite"
    )
