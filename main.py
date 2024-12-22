import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bin.handlers.telegram.get_point import PointHandler
from bin.handlers.telegram.main_handler import MainHandler
from bin.handlers.telegram.weather import WeatherHandler
from bin.services.geo_points.geo_points_service import GeoPointService
from bin.services.geo_points.yandex_geocoder_client import YandexGeocoderClient

# Токен вашего бота
BOT_TOKEN = "7905488641:AAEdGi1LV9BJ2GhmaTMB-s52egGLh0wG-Dw"
GEOCODER_KEY = "40b28dca-6c3e-4564-ad24-2bc3d32bc304"

# Основная функция запуска
async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    yandex_geocoder_client = YandexGeocoderClient(GEOCODER_KEY)
    
    geo_point_service = GeoPointService(repository=yandex_geocoder_client)

    point_handler = PointHandler(geo_point_service=geo_point_service)
    weather_handler = WeatherHandler(point_handler=point_handler)
    main_handler = MainHandler(weather_handler=weather_handler)
    
    dp.include_router(main_handler.router)

    # Запуск polling
    print("Бот запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


# Запуск приложения
if __name__ == "__main__":
    asyncio.run(main())
