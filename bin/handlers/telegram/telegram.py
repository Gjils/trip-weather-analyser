from aiogram import Router, Dispatcher
from aiogram.types import Message

import yaml

with open("bin/handlers/dictionary/dictionary.yaml", "r", encoding="utf-8") as file:
    messages = yaml.safe_load(file)


class TelegramHandler:
    def __init__(self, weather_service, dispatcher: Dispatcher):
        self.dp = dispatcher
        self.weather_service = weather_service

        self.dp.message.register(self.handle_message, commands=["start"])
        self.dp.message.register(self.handle_message, commands=["help"])

    def handle_start(self, message: Message):
        message.reply(messages["start"])

    def handle_help(self, message: Message):
        message.reply(messages["help"])
