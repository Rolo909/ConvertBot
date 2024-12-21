import telebot
import requests
import json
from telebot import types
from forex_python.converter import CurrencyCodes

bot = telebot.TeleBot('7333928559:AAHwR4VLS9bpiAywyyyxUt6_j4c_x0gi6Ro')
API = '0a66c16de1ffc590c50bbf91d03b5830'
value = 0
length = 0
heavy = 0
units = {'мм': 0.1,
         'см': 1,
         'дц': 10,
         'м': 100,
         'км': 1000,
         }

weights = {'г': 0.1,
           'кг': 100,
           'ц': 10000,
           'т': 100000,
           }

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width = 2)
    btn1 = types.InlineKeyboardButton('Вес', callback_data = 'вес')
    btn2 = types.InlineKeyboardButton('Длина', callback_data='длина')
    btn3 = types.InlineKeyboardButton('Валюта', callback_data='валюта')
    btn4 = types.InlineKeyboardButton('Погода', callback_data='weather')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Выбери , что хочешь перевести или узнать', reply_markup = markup)

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '</b>Help</b> information', parse_mode='html')

@bot.callback_query_handler(func = lambda call :True)
def callback(call):
    if call.data == 'длина':
        bot.send_message(call.message.chat.id, "Введите значение длины")
        bot.register_next_step_handler(call.message, length_1)
    elif call.data == 'вес':
        bot.send_message(call.message.chat.id, "Введите значение веса")
        bot.register_next_step_handler(call.message, weight_1)
    elif call.data == 'валюта':
        bot.send_message(call.message.chat.id, "Введите значение валюты")
        bot.register_next_step_handler(call.message, currency_1)
    elif call.data == 'weather':
        bot.send_message(call.message.chat.id, "Введите город , в котором хотите узнать погоду")
        bot.register_next_step_handler(call.message, weather)

def currency_1(message):
    global value
    try:
        value = float(message.text)
        if value > 0:
            bot.send_message(message.chat.id,
                             "Введите сообщение по примеру: '(тип вашей валюты) (в которую нужно конвертировать)' ")
            bot.register_next_step_handler(message, currency_2)
        else:
            bot.send_message(message.chat.id, "Введите корректное значение валюты")
            bot.register_next_step_handler(message, currency_1)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное значение валюты. Пожалуйста, введите число.")
        bot.register_next_step_handler(message, currency_1)

def currency_2(message):
    global value
    vl = message.text.upper().split(' ')

    # Проверяем, что валюты введены корректно
    currency_codes = CurrencyCodes()
    if not currency_codes.get_symbol(vl[0]):
        bot.send_message(message.chat.id,
                         'Некорректное название валюты. Пожалуйста, введите правильное название валюты.')
        bot.register_next_step_handler(message, currency_2)
        return

    url = f"https://api.exchangerate-api.com/v4/latest/{vl[0]}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if len(vl) == 2 and vl[1] in data.get('rates', {}):
            exchange_rate = data['rates'][vl[1]]
            res = exchange_rate * value
            bot.send_message(message.chat.id, f'Равно {round(res, 2)} {vl[1]}')
        else:
            bot.send_message(message.chat.id, 'Некорректное название валюты для конвертации.')
            bot.register_next_step_handler(message, currency_1)
    else:
        bot.send_message(message.chat.id,
                         'Некорректный формат ввода или ошибка при получении данных. Пожалуйста, попробуйте еще раз.')
        bot.register_next_step_handler(message, currency_1)

def weight_1(message):
    global heavy
    try:
        heavy = float(message.text)
        if heavy > 0:
            bot.send_message(message.chat.id,
                             "Введите сообщение по примеру: '(тип вашего веса) (в который нужно конвертировать)' ")
            bot.register_next_step_handler(message, weight_2)
        else:
            bot.send_message(message.chat.id, "Введите корректное значение веса")
            bot.register_next_step_handler(message, weight_1)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное значение веса. Пожалуйста, введите число.")
        bot.register_next_step_handler(message, weight_1)

def weight_2(message):
    global weights, heavy
    we = message.text.lower().split(' ')

    if len(we) == 2:  # Проверка наличия двух элементов в списке
        if we[0] in weights and we[1] in weights:
            res = heavy * weights[we[0]] / weights[we[1]]
            bot.send_message(message.chat.id, f'Равно {res} {we[1]}')
        else:
            bot.send_message(message.chat.id,
                             'Неподдерживаемые единицы измерения. Пожалуйста, выберите из: г, кг, ц, т.')
            bot.register_next_step_handler(message, length_2)
    else:
        bot.send_message(message.chat.id,
                         'Некорректный формат ввода. Пожалуйста, введите две единицы измерения через пробел.')
        bot.register_next_step_handler(message, length_2)

def length_1(message):
    global length
    try:
        length = float(message.text)
        if length > 0:
            bot.send_message(message.chat.id, "Введите сообщение по примеру: '(тип вашей длины) (в которую нужно конвертировать)' ")
            bot.register_next_step_handler(message, length_2)
        else:
            bot.send_message(message.chat.id, "Введите корректное значение длины")
            bot.register_next_step_handler(message, length_1)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное значение длины. Пожалуйста, введите число.")
        bot.register_next_step_handler(message, length_1)

def length_2(message):
    global units, length
    un = message.text.lower().split(' ')

    if len(un) == 2:  # Проверка наличия двух элементов в списке
        if un[0] in units and un[1] in units:
            res = length * units[un[0]] / units[un[1]]
            bot.send_message(message.chat.id, f'Равно {res} {un[1]}')
        else:
            bot.send_message(message.chat.id,
                             'Неподдерживаемые единицы измерения. Пожалуйста, выберите из: мм, см, дц, м, км.')
            bot.register_next_step_handler(message, length_2)
    else:
        bot.send_message(message.chat.id,
                         'Некорректный формат ввода. Пожалуйста, введите две единицы измерения через пробел.')
        bot.register_next_step_handler(message, length_2)

def weather(message):
    global API
    city = message.text.strip().lower()
    url = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if url.status_code == 200:
        data = json.loads(url.text)
        bot.send_message(message.chat.id, f'В {message.text.strip()} {data["main"]["temp"]} градусов')
    else:
        bot.reply_to(message, 'Введите город корректно')
        bot.register_next_step_handler(message, weather)

def run_bot():
    while True:
        try:
            print("Бот запущен и работает...")
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Перезапуск бота через 5 секунд...")
            import time
            time.sleep(2)

if __name__ == "__main__":
    run_bot()

