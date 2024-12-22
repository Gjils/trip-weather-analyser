import logging
from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import yaml

from bin.handlers.telegram.get_point import PointHandler

with open("bin/handlers/dictionary/dictionary.yaml", "r", encoding="utf-8") as file:
    messages = yaml.safe_load(file)["trip_weather"]

point_router = Router()

logging.basicConfig(level=logging.INFO)


class TripWeatherHandler:
    class FSM(StatesGroup):
        waiting_starting_point = State()
        waiting_ending_point = State()
        waiting_additional_points = State()
        waiting_start_time = State()
        waiting_duration = State()
        waiting_time_interval = State()
        waiting_finish = State()

    def __init__(self, point_handler: PointHandler):
        self.point_handler = point_handler

        self.router = Router()
        self.router.callback_query.register(
            self.handle_starting_point, self.FSM.waiting_starting_point
        )
        self.router.callback_query.register(
            self.handle_ending_point, self.FSM.waiting_ending_point
        )
        self.router.callback_query.register(
            self.handle_additional_points, self.FSM.waiting_additional_points
        )
        self.router.callback_query.register(self.handle_start_time, self.FSM.waiting_start_time)

    async def entry_point(self, message_or_callback, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=messages["confirm_starting_point"], callback_data="confirm"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["cancel_starting_point"], callback_data="cancel"
                    )
                ],
            ]
        )

        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(
                messages["starting_point"], reply_markup=keyboard
            )
        elif isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.answer(
                messages["starting_point"], reply_markup=keyboard
            )
        logging.info("send start message")
        await state.set_state(self.FSM.waiting_starting_point)
        logging.info("set waiting for start point status")

    async def handle_starting_point(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        logging.info("got start point status: " + callback_query.data)
        status = callback_query.data
        if status == "confirm":
            await state.update_data(succes_callback=self.get_starting_point)
            await state.update_data(cancel_callback=self.entry_point)
            await self.point_handler.entry_point(callback_query, state)
        elif status == "cancel":
            await callback_query.message.delete()
            await state.clear()

    async def get_starting_point(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        start_point = await state.get_value("point")
        await state.update_data(start_point=start_point)
        await self.ask_ending_point(callback_query, state)

    async def ask_ending_point(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=messages["confirm_ending_point"], callback_data="confirm"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["cancel_ending_point"], callback_data="cancel"
                    )
                ],
            ]
        )
        await callback_query.message.edit_text(
            messages["ending_point"], reply_markup=keyboard
        )
        logging.info("ask for ending point")
        await state.set_state(self.FSM.waiting_ending_point)
        logging.info("waiting for ending point state")

    async def handle_ending_point(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        logging.info("got ending point status: " + callback_query.data)
        status = callback_query.data
        if status == "confirm":
            await state.update_data(succes_callback=self.get_ending_point)
            await state.update_data(cancel_callback=self.ask_ending_point)
            await self.point_handler.entry_point(callback_query, state)
        elif status == "cancel":
            await callback_query.message.delete()
            await state.clear()
            
    async def get_ending_point(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        end_point = await state.get_value("point")
        await state.update_data(end_point=end_point)
        await self.ask_additional_points(callback_query, state)

    async def ask_additional_points(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        additional_points = await state.get_value("additional_points")
        if additional_points is None:
            additional_points = []
        route = {
            "start_point": (await state.get_value("start_point"))["city"],
            "end_point": (await state.get_value("end_point"))["city"],
            "points": "".join([f"• {item['city']}\n" for item in additional_points])
        }
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=messages["add_point"], callback_data="add_point"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["continue"], callback_data="continue"
                    )
                ],
            ]
        )
        await callback_query.message.edit_text(
            messages["additional_points"].format(**route), reply_markup=keyboard
        )
        logging.info("ask for ending point")
        await state.set_state(self.FSM.waiting_additional_points)
        logging.info("waiting for ending point state")

    async def handle_additional_points(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        logging.info("got additional points status: " + callback_query.data)
        status = callback_query.data
        if status == "add_point":
            await state.update_data(succes_callback=self.get_additional_point)
            await state.update_data(cancel_callback=self.ask_additional_points)
            await self.point_handler.entry_point(callback_query, state)
        elif status == "continue":
            await self.ask_start_time(callback_query, state)
    
    async def get_additional_point(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        additional_point = await state.get_value("point")
        additional_points = await state.get_value("additional_points")
        if additional_points is None:
            additional_points = []
        additional_points.append(additional_point)
        await state.update_data(additional_points=additional_points)
        await self.ask_additional_points(callback_query, state)

    async def ask_start_time(self, callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_text(messages["start_time"])
        logging.info("ask for start time")
        await state.set_state(self.FSM.waiting_time_intervals)
        logging.info("waiting for start time state")
        
    async def handle_start_time(self, message: types.Message, state: FSMContext):
        logging.info("got start time: " + message.text)
        await state.update_data(start_time=message.text)
        await self.ask_duration(message, state)
    
    async def ask_duration(self, callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_text(messages["duration"])
        logging.info("ask duration")
        await state.set_state(self.FSM.waiting_duration)
        logging.info("waiting for duration state")

    