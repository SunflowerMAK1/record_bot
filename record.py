import telebot
import json
from datetime import date, timedelta
from telebot import types

TOKEN = "7941943733:AAGVwKT4qLTyvr_FSxE7m2K-T4NEW0yMn7A"
bot = telebot.TeleBot(TOKEN)

months = {
    "01": "января", "02": "февраля", "03": "марта", "04": "апреля", "05": "мая", "06": "июня", "07": "июля", "08": "августа",
    "09": "сентября", "10": "октября", "11": "ноября", "12": "декабря"
}

@bot.message_handler(commands=["start"])
def start(incoming_message):
    bot.send_message(incoming_message.chat.id, "Здравствуйте! Введите команду /show_dates чтобы увидеть свободные даты")

@bot.message_handler(commands=["show_dates"])
def show_dates(incoming_message):
    keyboard = generate_date_keyboard()
    bot.send_message(incoming_message.chat.id,"Выберите день:", reply_markup=keyboard)

def generate_date_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    days = []
    for i in range(7):
        days.append(date.today() + timedelta(days=3 + i))
    for day in days:
        callback_data = f"day:{day}"
        day = callback_data[-2:] + " " + months[callback_data[-5:-3]]
        button = types.InlineKeyboardButton(f"{day}", callback_data=callback_data)
        keyboard.add(button)
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def handle_click(call):
    if call.data.startswith("day"):
        date = call.data.split(":")[1]
        date = date[-2:] + " " + months[date[-5:-3]]
        bot.send_message(call.message.chat.id, f"Вы выбрали дату: {date}")
        bot.send_message(call.message.chat.id, "Выберите время:", reply_markup=generate_time_keyboard(f"{date}"))
    if call.data.startswith("time"):
        time = call.data.split(":")[1] + ":" + call.data.split(":")[2]
        date = call.data.split(":")[3]
        add_appointment(date, time, call.message.chat.id)
        bot.send_message(call.message.chat.id, f"Вы записаны на: {time} {date}")


def add_appointment(date, time, client):
    with open("records.json", "r", encoding="utf-8") as file:
        records = json.load(file)
    new_record = {
      "date": date,
      "time": time,
      "client": client
    }
    records["appointments"].append(new_record)
    with open("records.json", "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)



def generate_time_keyboard(date):
    keyboard = types.InlineKeyboardMarkup()
    times = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    with open("records.json", "r", encoding="utf-8") as file:
        records = json.load(file)
    for record in records["appointments"]:
        if record["date"] == date:
            times.remove(record["time"])
    for time in times:
        callback_data = f"time:{time}:{date}"
        button = types.InlineKeyboardButton(f"{time}", callback_data=callback_data)
        keyboard.add(button)
    return keyboard

@bot.message_handler(commands=["my_record"])
def my_record(call):
    with open("records.json", "r", encoding="utf-8") as file:
        records = json.load(file)
    for record in records["appointments"]:
        if record["client"] == call.chat.id:
            time = record["time"]
            date = record["date"]
    try:
        bot.send_message(call.chat.id, f"Здравствуйте! Вы записаны на:\n{time} {date}")
    except UnboundLocalError:
        bot.send_message(call.chat.id, f"Здравствуйте! У Вас ещё нет записи\nВведите команду /show_dates чтобы увидеть свободные даты.")

bot.infinity_polling()