import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from telegram import CallbackQuery
import yaml

with open("bin/handlers/dictionary/dictionary.yaml", "r", encoding="utf-8") as file:
    messages = yaml.safe_load(file)


class FallbackHandler:
    def __init__(self):
        self.router = Router()
        self.router.message.register(self.handle_fallback)
        self.router.callback_query.register(self.handle_unknown_callback)

    async def handle_fallback(self, message: Message):
        logging.info("got fallback: " + message.text if message.text else "")
        try:
            await message.delete()
        except TelegramBadRequest:
            pass

    async def handle_unknown_callback(callback_query: CallbackQuery):
        logging.info("unknown callback: " + callback_query.data)()
        await callback_query.answer(text=messages["command_error"], show_alert=True)
