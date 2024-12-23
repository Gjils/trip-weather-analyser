import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bin.handlers.telegram.fallback import FallbackHandler
from bin.handlers.telegram.get_point import PointHandler
from bin.handlers.telegram.main_handler import MainHandler
from bin.handlers.telegram.weather import WeatherHandler
from bin.handlers.telegram.weather_view import WeatherViewHandler
from bin.services.geo_points.geo_points_service import GeoPointService
from bin.services.geo_points.yandex_geocoder_client import YandexGeocoderClient
from bin.services.weather.weather_service import WeatherService
from bin.services.weather.yandex_weather_client import YandexWeatherClient

import locale

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

logging.basicConfig(level=logging.INFO)

# Токен вашего бота
BOT_TOKEN = "7905488641:AAEdGi1LV9BJ2GhmaTMB-s52egGLh0wG-Dw"
GEOCODER_KEY = "40b28dca-6c3e-4564-ad24-2bc3d32bc304"
WEATHER_KEY = "17a7092b-6af1-4a42-b451-0036be640009"


# Основная функция запуска
async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    yandex_geocoder_client = YandexGeocoderClient(GEOCODER_KEY)
    yandex_weather_client = YandexWeatherClient(WEATHER_KEY)

    geo_point_service = GeoPointService(repository=yandex_geocoder_client)
    weather_service = WeatherService(repository=yandex_weather_client)

    fallback_handler = FallbackHandler()
    point_handler = PointHandler(geo_point_service=geo_point_service)
    weather_view_handler = WeatherViewHandler(weather_service=weather_service)
    weather_handler = WeatherHandler(
        point_handler=point_handler,
        weather_view_handler=weather_view_handler,
        weather_service=weather_service,
    )
    main_handler = MainHandler(
        weather_handler=weather_handler, fallback_handler=fallback_handler
    )

    dp.include_router(main_handler.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
