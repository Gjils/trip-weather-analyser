import asyncio
from aiogram import F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from telegram import CallbackQuery

from bin.handlers.telegram.get_point import PointHandler
from bin.handlers.telegram.trip_weather import TripWeatherHandler

# Токен вашего бота
BOT_TOKEN = "7905488641:AAEdGi1LV9BJ2GhmaTMB-s52egGLh0wG-Dw"

# Основная функция запуска
async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    async def succes_callback(callback_query: CallbackQuery, point: dict):
        await callback_query.message.edit_text(point["city"] + " " + point["long"] + " " + point["lat"])

    # Пример регистрации дополнительных маршрутов
    point_handler = PointHandler()
    weather_handler = TripWeatherHandler(point_handler=point_handler)
    dp.include_router(point_handler.router)
    dp.include_router(weather_handler.router)

    @dp.message(F.text == "Начать задание")
    async def start_task_handler(message: Message, state):
        """Пример вызова FSM из команды"""
        await weather_handler.entry_point(message, state)

    @dp.message(F.text == "1")
    async def start_task_handler(message: Message, state):
        """Пример вызова FSM из команды"""
        await weather_handler.entry_point(message, state)

    # Запуск polling
    print("Бот запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


# Запуск приложения
if __name__ == "__main__":
    asyncio.run(main())
