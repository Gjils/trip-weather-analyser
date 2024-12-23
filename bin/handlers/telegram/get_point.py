import logging
from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import yaml

from bin.services.geo_points.geo_points_service import GeoPointService

with open("bin/handlers/dictionary/dictionary.yaml", "r", encoding="utf-8") as file:
    messages = yaml.safe_load(file)["choose_point"]


class PointHandler:
    class FSM(StatesGroup):
        waiting_type = State()
        waiting_long = State()
        waiting_lat = State()
        waiting_city = State()
        waiting_confirm = State()
        waiting_error = State()

    def __init__(self, geo_point_service: GeoPointService):
        self.geo_point_service = geo_point_service

        self.router = Router()
        self.router.callback_query.register(self.handle_type, self.FSM.waiting_type)
        self.router.message.register(self.handle_long, self.FSM.waiting_long)
        self.router.message.register(self.handle_lat, self.FSM.waiting_lat)
        self.router.message.register(self.handle_city, self.FSM.waiting_city)
        self.router.callback_query.register(
            self.handle_confirm, self.FSM.waiting_confirm
        )
        self.router.callback_query.register(self.handle_error, self.FSM.waiting_error)

    async def entry_point(self, message_or_callback, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=messages["cords"], callback_data="cords")],
                [InlineKeyboardButton(text=messages["city"], callback_data="city")],
            ]
        )

        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(messages["method"], reply_markup=keyboard)
        elif isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.edit_text(
                messages["method"], reply_markup=keyboard
            )
        logging.info("send choose method")
        await state.set_state(self.FSM.waiting_type)
        logging.info("set waiting for answer state")

    async def handle_type(self, callback_query: types.CallbackQuery, state: FSMContext):
        logging.info("got answer: " + callback_query.data)
        method = callback_query.data
        await state.update_data(method=method)
        if method == "cords":
            await self.ask_cordinates_long(callback_query, state)
        elif method == "city":
            await self.ask_city(callback_query, state)

    async def ask_cordinates_long(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        await callback_query.message.edit_text(messages["enter_long"])
        logging.info("ask for long")
        await state.set_state(self.FSM.waiting_long)
        logging.info("waiting for long state")

    async def handle_long(self, message: types.Message, state: FSMContext):
        logging.info("got long: " + message.text)
        await state.update_data(long=message.text)
        await self.ask_cordinates_lat(message, state)

    async def ask_cordinates_lat(self, message: types.Message, state: FSMContext):
        await message.answer(messages["enter_lat"])
        logging.info("ask for long")
        await state.set_state(self.FSM.waiting_lat)
        logging.info("waiting for lat state")

    async def handle_lat(self, message: types.Message, state: FSMContext):
        logging.info("got lat: " + message.text)
        await state.update_data(lat=message.text)
        await self.ask_confirm(message, state)

    async def ask_city(self, callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_text(messages["enter_city"])
        logging.info("ask for city")
        await state.set_state(self.FSM.waiting_city)
        logging.info("waiting for city state")

    async def handle_city(self, message: types.Message, state: FSMContext):
        logging.info("got city: " + message.text)
        await state.update_data(city=message.text)
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
        method = await state.get_value("method")
        state_data = await state.get_data()
        if method == "cords":
            long = state_data["long"]
            lat = state_data["lat"]
            try:
                point = self.geo_point_service.get_point_by_coordinates(lat, long)
            except Exception as e:
                logging.error(e)
                await self.ask_error(message, state)
                return
        if method == "city":
            city = state_data["city"]
            try:
                point = self.geo_point_service.get_point_by_city(city)
            except Exception as e:
                logging.error(e)
                await self.ask_error(message, state)
                return

        await state.update_data(point=point)
        await message.answer(
            messages["confirm_message"].format(
                long=point.longitude, lat=point.latitude, city=point.city
            ),
            reply_markup=keyboard,
        )
        await state.set_state(self.FSM.waiting_confirm)

    async def handle_confirm(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        logging.info("got confirm: " + callback_query.data)
        status = callback_query.data
        if status == "confirm":
            await (await state.get_value("succes_callback"))(callback_query, state)
        elif status == "cancel":
            await (await state.get_data("cancel_callback")).succes_callback(
                callback_query, state
            )

    async def ask_error(self, message: types.Message, state: FSMContext):
        logging.info("got error")
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=messages["error_message_try_again"],
                        callback_data="try_again",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["error_message_cancel"], callback_data="cancel"
                    )
                ],
            ]
        )
        await message.answer(messages["error_message"], reply_markup=keyboard)
        await state.set_state(self.FSM.waiting_error)

    async def handle_error(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        logging.info("got error status: " + callback_query.data)
        if callback_query.data == "try_again":
            await self.entry_point(callback_query, state)
        elif callback_query.data == "cancel":
            await (await state.get_value("cancel_callback"))(callback_query, state)
