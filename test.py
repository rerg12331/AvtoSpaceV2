import telebot
import json
import datetime
import time
from telebot import types
from config import token, api_key
from bot.get_locations import get_nearest_gas_stations_yandex
from bot.key_board_menu import generate_menu
from requests.exceptions import ConnectionError, Timeout, RequestException
from bot.db import session, User, Location

bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def main(message):
    existing_user = session.query(User).filter_by(user_id=message.from_user.id).first()
    if existing_user is None:
        date_time = datetime.datetime.fromtimestamp(message.date)
        new_user = User(
            user_id = message.from_user.id,
            name = message.from_user.first_name,
            username = message.from_user.username,
            chat_id = message.chat.id,
            location_latitude = None,
            location_longitude = None,
            date_registered = date_time.strftime('%Y-%m-%d %H:%M:%S')
        )

        # Добавление пользователя в базу данных
        session.add(new_user)
        session.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    search = types.KeyboardButton('🔎 Найти заправку', request_location=True)
    markup.row(search)
    bot.reply_to(message, 
        "Добро пожаловать в <b>AvtoSpace</b> — Поиск бензиновых и электрозаправок! 🚗⚡️\n\n"
        "Я ваш виртуальный помощник, который поможет вам быстро и легко найти ближайшие АЗС.\n\n"
        "С <b>AvtoSpace</b> вы сможете:\n\n"
        "<em><u>• Найти ближайшие бензиновые и электрозаправки.</u></em>\n"
        "<em><u>• Узнать текущие цены на топливо и зарядные станции.</u></em>\n"
        "<em><u>• Построить оптимальный маршрут до выбранной станции.</u></em>\n\n"
        "Давайте начнем ваше путешествие с комфорта и уверенностью! Напишите мне, что вам нужно, и я помогу вам найти лучшую заправку.",
        parse_mode='html',
        reply_markup=markup
        )

@bot.message_handler(content_types=['location'])
def location(message):
    user = session.query(User).filter_by(user_id=message.from_user.id).first()
    if user:
        # Обновление значений location_latitude и location_longitude
        user.location_latitude = message.location.latitude
        user.location_longitude = message.location.longitude
        session.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    benz = types.KeyboardButton('⛽️ Бензиновые')
    elecro = types.KeyboardButton('⚡️ Электро')
    markup.row(benz,elecro)
    # message_info = f"Текущее местоположение: {message.location.latitude}, {message.location.longitude}"
    bot.send_message(message.chat.id, reply_markup=markup) # , message_info

@bot.message_handler(content_types=['text'])
def location(message):
    if message.text == '⛽️ Бензиновые' or message.text == '⚡️ Электро':
        user = session.query(User).filter_by(user_id=message.from_user.id).first()
        text = "Заправка" if message.text == "⛽️ Бензиновые" else "Электрозаправка" if message.text == "⚡️ Электро" else "Заправка"
        info = get_nearest_gas_stations_yandex(api_key, user.location_latitude, user.location_longitude, text)

        user_locations = session.query(Location).filter_by(user_id=message.from_user.id).first()
        if user_locations is None:
            new_location = Location(user_id=message.from_user.id, data=info)
            session.add(new_location)
            session.commit()
        else:
            user_locations.data = info
            session.commit()
        bot.send_message(message.chat.id, "Выберите заправку:", reply_markup=generate_menu(start_index=0, items = info))

@bot.callback_query_handler(func=lambda call: call.data.startswith('item_') or call.data.startswith('next_') or call.data.startswith('back_'))
def handle_callback(call):
    location = session.query(Location).filter_by(user_id=call.from_user.id).first()
    info = location.data
    if call.data.startswith("item_"):
        item_index = int(call.data.split("_")[1])
        print(item_index)
        bot.answer_callback_query(call.id, f"Вы выбрали: {info[item_index]['name']}")
        info_text = (
            f"⚡️: <b>{info[item_index]['name']}</b>\n\n"
            f"📍 <b>Адрес</b>: <code>{info[item_index]['address']}</code>\n\n"
            f"🕒 <b>Время работы</b>: {info[item_index]['hours']}\n\n"
            f"☎️ <b>Контакты</b>: <code>{info[item_index]['phone']}</code>\n\n"
            f"👣 <b>На расстоянии</b>: {info[item_index]['distance']} km"
        )
        inline_keyboard = types.InlineKeyboardMarkup()
        location_button = types.InlineKeyboardButton("Показать локацию", callback_data=f"show-location_{item_index}")
        inline_keyboard.row(location_button)
        bot.send_message(call.message.chat.id, info_text, parse_mode="HTML", reply_markup=inline_keyboard)

    elif call.data.startswith("next_"):
        start_index = int(call.data.split("_")[1]) + 5
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=generate_menu(start_index, items = info))
    elif call.data.startswith("back_"):
        start_index = int(call.data.split("_")[1]) - 5
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=generate_menu(start_index, items = info))

@bot.callback_query_handler(func=lambda call: call.data.startswith('show-location_'))
def show_location_handler(call):
    location = session.query(Location).filter_by(user_id=call.from_user.id).first()
    info = location.data
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    search = types.KeyboardButton('🔎 Найти заправку', request_location=True)
    markup.row(search)
    item_index = int(call.data.split("_")[1])
    bot.send_location(call.message.chat.id, info[item_index]['coordinates'][1], info[item_index]['coordinates'][0], reply_markup=markup)
    

def jopa():
    try:
        bot.polling(non_stop=True)
    except (ConnectionError, Timeout, RequestException) as e:
        print(f"Ошибка подключения: {e}. Попробую еще раз через 5 секунд.")
    except KeyboardInterrupt:
        print("Завершение работы...")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}. Попробую еще раз через 5 секунд.")

if __name__ == '__main__':
    jopa()

