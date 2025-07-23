from datetime import datetime
from pprint import pprint

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext
from config import API_KEY
import messages
import requests

BASE_URL = 'http://api.weatherapi.com/v1'

user_data = {}  # user_id: city_name saqlanadi

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    
    update.message.reply_html(
        messages.welcome_text.format(full_name=user.full_name)
    )

    update.message.reply_html(
        messages.select_category,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton('🌤 Hozirgi ob-havo'), KeyboardButton('📍 Lokatsiya bo\'yicha aniqlash', request_location=True)],
                [KeyboardButton('🕒 Soatlik ob-havo'), KeyboardButton('📅 Haftalik ob-havo')],
                [KeyboardButton('🌐 Hududni o\'zgartirish')],
                [KeyboardButton('📞 Aloqa')]
            ],
            resize_keyboard=True
        )
    )

def send_weather_by_location(update: Update, context: CallbackContext):
    location = update.message.location

    url = f"{BASE_URL}/current.json"
    payload = {
        'key': API_KEY,
        'q': f'{location.latitude},{location.longitude}'
    }
    response = requests.get(url, params=payload)
    data = response.json()
    pprint(data)

    now = datetime.now()

    week_days = {
        1: "Dushanba", 2: "Seshanba", 3: "Chorshanba", 4: "Payshanba",
        5: "Juma", 6: "Shanba", 7: "Yakshanba",
    }
    months = {
        1: "Yanvar", 2: "Fevfral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
        7: "Iyul", 8: "Avgust", 9: "Sentabr", 10: "Obkabr", 11: "Noyabr", 12: "Dekabr",
    }

    update.message.reply_html(
        messages.current_weather.format(
            week_day=week_days[now.weekday() + 1],
            day=now.day,
            month=months[now.month],
            city=data['location']['region'],
            district=data['location']['name'],
            temp_c=data['current']['temp_c'],
            feelslike_c=data['current']['feelslike_c'],
            cloud=data['current']['cloud'],
            humidity=data['current']['humidity'],
            wind_mph=data['current']['wind_mph'],
            pressure_mb=data['current']['pressure_mb']
        )
    )

def ask_location(update: Update, context: CallbackContext):
    location_button = KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[location_button]], resize_keyboard=True, one_time_keyboard=True)
    
    update.message.reply_text("Iltimos, lokatsiyangizni yuboring:", reply_markup=reply_markup)

def current_weather_by_city(update: Update, context: CallbackContext):
    update.message.reply_text("Shahar nomini kiriting:")
    context.user_data['state'] = 'current_weather'

def hourly_weather_by_city(update: Update, context: CallbackContext):
    update.message.reply_text("Soatlik ob-havo uchun shahar nomini kiriting:")
    context.user_data['state'] = 'hourly_weather'

def weekly_weather_by_city(update: Update, context: CallbackContext):
    update.message.reply_text("Haftalik ob-havo uchun shahar nomini kiriting:")
    context.user_data['state'] = 'weekly_weather'

def change_city(update: Update, context: CallbackContext):
    update.message.reply_text("Yangi hudud nomini kiriting:")
    context.user_data['state'] = 'change_city'

def contact_info(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "🌤 Ob-havo botiga hush kelibsiz!\n\n"
        "🚀 Bu bot orqali O'zbekistonning barcha hududlaridagi ob-havo ma'lumotlarini ko'rishingiz mumkin. "
        "Bot sizga foyda keltirsa, biz bundan hursand bo'lamiz.\n\n"
        "Bot orqali siz quyidagi 4 xil ob-havo ma'lumotini olishingiz mumkin:\n"
        "1️⃣ Hozirgi ob-havo (to‘liq ma’lumot)\n"
        "2️⃣ Lokatsiya bo'yicha\n"
        "3️⃣ Haftalik ob-havo\n"
        "4️⃣ Soatlik ob-havo\n\n "
        "📩 Taklif va mulohazalaringiz bo‘lsa 👉 @firdavsbek_abduganiyev ga yuborishingiz mumkin."
    )

def handle_city_input(update: Update, context: CallbackContext):
    city = update.message.text
    state = context.user_data.get('state')

    url = f"{BASE_URL}/forecast.json"
    payload = {
        'key': API_KEY,
        'q': city,
        'days': 7,
        'aqi': 'no',
        'alerts': 'no'
    }
    response = requests.get(url, params=payload)
    data = response.json()

    if state == 'current_weather':
        current = data['current']
        msg = (
            f"🌤 Hozirgi ob-havo: {city.title()}\n"
            f"Harorat: {current['temp_c']}°C\n"
            f"Namlik: {current['humidity']}%\n"
            f"Shamol: {current['wind_kph']} km/h"
        )
        update.message.reply_text(msg)

    elif state == 'hourly_weather':
        hourly = data['forecast']['forecastday'][0]['hour'][:12]  
        msg = f"🕒 Soatlik ob-havo ({city.title()}):\n"
        for h in hourly:
            msg += f"{h['time'].split()[1]}: {h['temp_c']}°C\n"
        update.message.reply_text(msg)

    elif state == 'weekly_weather':
        days = data['forecast']['forecastday']
        msg = f"📅 Haftalik ob-havo ({city.title()}):\n"
        for day in days:
            msg += f"{day['date']}: {day['day']['avgtemp_c']}°C, {day['day']['condition']['text']}\n"
        update.message.reply_text(msg)

    elif state == 'change_city':
        user_data[update.effective_user.id] = city
        update.message.reply_text(f"🌐 Hududingiz {city.title()} ga o‘zgartirildi.")

    else:
        update.message.reply_text("Iltimos, menyudan biror bo‘limni tanlang.")
