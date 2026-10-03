import os
import time
import requests
import schedule
import threading
from telebot import TeleBot
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot 24/7 faol ishlamoqda!"

TOKEN = "8981237576:AAGaSmGul81AH7oKz5aKGYH1Aay0r-Jebig"
bot = TeleBot(TOKEN)

LOCATIONS = {
    "Pastdarg'om": {"lat": 39.560, "lng": 66.690},
    "Ishtixon": {"lat": 39.966, "lng": 66.486},
    "Kattaqo'rg'on": {"lat": 39.897, "lng": 66.257}
}

user_settings = {}

def get_prayer_times(lat, lng):
    try:
        url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lng}&method=3"
        res = requests.get(url).json()
        if res and "data" in res:
            t = res["data"]["timings"]
            return {
                "Bomdod": t["Fajr"],
                "Peshin": t["Dhuhr"],
                "Asr": t["Asr"],
                "Shom": t["Maghrib"],
                "Xufton": t["Isha"]
            }
    except Exception as e:
        print("Xatolik:", e)
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_settings[chat_id] = "Pastdarg'om"
    
    msg = (
        "Assalomu alaykum! 🕌 Namoz vaqtlari eslatuvchi botga xush kelibsiz.\n\n"
        "Hozirgi tanlangan hudud: **Pastdarg'om**\n\n"
        "Hududni o'zgartirish uchun buyruqlardan birini tanlang:\n"
        "/pastdargom - Pastdarg'om tumani\n"
        "/ishtixon - Ishtixon tumani\n"
        "/kattaqorgan - Kattaqo'rg'on tumani"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['pastdargom', 'ishtixon', 'kattaqorgan'])
def set_location(message):
    chat_id = message.chat.id
    cmd = message.text.replace("/", "")
    
    if cmd == "pastdargom":
        user_settings[chat_id] = "Pastdarg'om"
    elif cmd == "ishtixon":
        user_settings[chat_id] = "Ishtixon"
    elif cmd == "kattaqorgan":
        user_settings[chat_id] = "Kattaqo'rg'on"
        
    bot.reply_to(message, f"✅ Hudud muvaffaqiyatli o'zgartirildi: **{user_settings[chat_id]}**", parse_mode="Markdown")

def check_and_notify():
    current_time = time.strftime("%H:%M")
    
    for chat_id, region in user_settings.items():
        coords = LOCATIONS[region]
        times = get_prayer_times(coords["lat"], coords["lng"])
        
        if times:
            for prayer_name, prayer_time in times.items():
                if current_time == prayer_time:
                    text = f"🕌 **{region} tumani**\n\n**{prayer_name}** namozi vaqti bo'ldi! ({prayer_time})\n\n*Namozni o'z vaqtida ado etishingizni so'raymiz.*"
                    bot.send_message(chat_id, text, parse_mode="Markdown")

schedule.every(1).minutes.do(check_and_notify)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
