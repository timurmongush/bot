import os
import telebot
import json
import socket

# Принудительно использовать IPv4 (иногда помогает с таймаутами)
socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

# Вставь сюда токен своего бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: переменная окружения BOT_TOKEN не установлена!")

bot = telebot.TeleBot(BOT_TOKEN)

# Загрузка JSON с маршрутами
try:
    with open("country_routes.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        # Если JSON — список словарей, объединяем их в один словарь
        if isinstance(data, list):
            ROUTES = {}
            for item in data:
                if isinstance(item, dict):
                    ROUTES.update(item)
        elif isinstance(data, dict):
            ROUTES = data
        else:
            print("Неверный формат JSON")
            ROUTES = {}
except Exception as e:
    print("Ошибка при загрузке JSON:", e)
    ROUTES = {}

# Выводим список стран в базе
print("Страны в базе:", list(ROUTES.keys()))

# Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id,"Привет! 👋\nНапиши название страны, и я дам маршрут путешествия.")

# Обработка любых сообщений
@bot.message_handler(func=lambda m: True)
def send_route(message):
    country_input = message.text.strip().lower()
    matched_country = None

    # Поиск страны без учета регистра
    for key in ROUTES.keys():
        if key.lower() == country_input:
            matched_country = key
            break

    if not matched_country:
        bot.send_message(message.chat.id, "❌ Такой страны нет в базе.")
        return

    days = ROUTES[matched_country]
    text = f"✈ Маршрут по стране {matched_country}:\n\n"

    for day, info in days.items():
        text += f"День {day}: {info['city']}\n"
        text += "Достопримечательности:\n"
        for place in info["attractions"]:
            text += "- " + place + "\n"
        text += "\n"

    bot.send_message(message.chat.id, text)

# Запуск бота с увеличенным таймаутом
bot.polling(none_stop=True, timeout=300, long_polling_timeout=300)
