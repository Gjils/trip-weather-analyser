import logging
from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage

import yaml

from bin.entities.geo_point import GeoPoint

with open("bin/handlers/dictionary/dictionary.yaml", "r", encoding="utf-8") as file:
    messages = yaml.safe_load(file)["choose_point"]

point_router = Router()

logging.basicConfig(level=logging.INFO)


class PointHandler:
    class FSM(StatesGroup):
        type_selected = State()
        get_coordinates_long = State()
        get_coordinates_lat = State()
        get_city = State()
        confirm = State()

    def __init__(self, storage: MemoryStorage):
        self.storage = storage
        self.router = Router()
        self.router.callback_query.register(self.type_selected, self.FSM.type_selected)
        self.router.message.register(
            self.get_coordinates_long, self.FSM.get_coordinates_long
        )
        self.router.message.register(
            self.get_coordinates_lat, self.FSM.get_coordinates_lat
        )
        self.router.message.register(self.get_city, self.FSM.get_city)

    async def entry_point(self, message_or_callback, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=messages["cords"], callback_data="cords")],
                [InlineKeyboardButton(text=messages["city"], callback_data="city")],
            ]
        )

        # Универсальная отправка сообщения
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(messages["method"], reply_markup=keyboard)
        elif isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.answer(
                messages["method"], reply_markup=keyboard
            )
        logging.info("send choose method")
        await state.set_state(self.FSM.type_selected)
        logging.info("set waiting for answer state")

    async def type_selected(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        logging.info("got answer: " + callback_query.data)
        method = callback_query.data
        if method == "cords":
            await self.ask_cordinates_long(callback_query, state)
        elif method == "city":
            await self.ask_city(callback_query, state)

    async def ask_cordinates_long(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        await callback_query.message.edit_text(messages["enter_long"])
        logging.info("ask for long")
        await state.set_state(self.FSM.get_coordinates_long)
        logging.info("waiting for long state")

    async def get_coordinates_long(self, message: types.Message, state: FSMContext):
        logging.info("got long: " + message.text)
        await self.ask_cordinates_lat(message, state)

    async def ask_cordinates_lat(self, message: types.Message, state: FSMContext):
        await message.answer(messages["enter_lat"])
        logging.info("ask for long")
        await state.set_state(self.FSM.get_coordinates_lat)
        logging.info("waiting for lat state")

    async def get_coordinates_lat(self, message: types.Message, state: FSMContext):
        logging.info("got lat: " + message.text)
        await self.ask_confirm(message, state)

    async def ask_city(self, callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_text(messages["enter_city"])
        logging.info("ask for city")
        await state.set_state(self.FSM.get_city)
        logging.info("waiting for city state")

    async def get_city(self, message: types.Message, state: FSMContext):
        logging.info("got city: " + message.text)
        await self.ask_confirm(message, state)

    async def ask_confirm(self, message: types.Message, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=messages["confirm_button"], callback_data="confirm"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["cancel_button"], callback_data="cancel"
                    )
                ],
            ]
        )
        await message.answer(messages["confirm_message"], reply_markup=keyboard)
        await state.set_state(self.FSM.confirm)
