from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
from config import TOKEN
import handlers


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', handlers.start))

    dispatcher.add_handler(MessageHandler(Filters.location, handlers.send_weather_by_location))

    dispatcher.add_handler(MessageHandler(Filters.text("🌤 Hozirgi ob-havo"), handlers.current_weather_by_city))
    dispatcher.add_handler(MessageHandler(Filters.text("📍 Lokatsiya bo‘yicha aniqlash"), handlers.ask_location))
    dispatcher.add_handler(MessageHandler(Filters.text("🕒 Soatlik ob-havo"), handlers.hourly_weather_by_city))
    dispatcher.add_handler(MessageHandler(Filters.text("📅 Haftalik ob-havo"), handlers.weekly_weather_by_city))
    dispatcher.add_handler(MessageHandler(Filters.text("🌐 Hududni o'zgartirish"), handlers.change_city))
    dispatcher.add_handler(MessageHandler(Filters.text("📞 Aloqa"), handlers.contact_info))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handlers.handle_city_input))

    updater.start_polling()
    updater.idle()


main()
