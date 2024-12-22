import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

import yaml

from bin.handlers.telegram.weather import WeatherHandler

with open("bin/handlers/dictionary/dictionary.yaml", "r", encoding="utf-8") as file:
    messages = yaml.safe_load(file)

logging.basicConfig(level=logging.INFO)

class MainHandler:
    def __init__(self, weather_handler: WeatherHandler):
        self.weather_handler = weather_handler

        self.router = Router()
        self.router.include_router(self.weather_handler.router)
        self.router.message.register(self.handle_start, Command("start"))
        self.router.message.register(self.handle_help, Command("help"))
        self.router.message.register(self.handle_weather, Command("weather"))

    async def handle_start(self, message: Message):
        logging.info("start command")
        await message.reply(messages["start"])

    async def handle_help(self, message: Message):
        logging.info("help command")
        await message.reply(messages["help"])

    async def handle_weather(self, message: Message, state: FSMContext):
        logging.info("weather command")
        await self.weather_handler.entry_point(message, state)
