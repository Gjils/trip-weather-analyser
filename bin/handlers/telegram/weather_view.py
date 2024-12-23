import logging
from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import yaml

with open("bin/handlers/dictionary/dictionary.yaml", "r", encoding="utf-8") as file:
    messages = yaml.safe_load(file)["weather_view"]

logging.basicConfig(level=logging.INFO)


class WeatherViewHandler:
    class FSM(StatesGroup):
        waiting_point = State()
        waiting_date = State()
        waiting_measure = State()
        showing_info = State()

    def __init__(self):
        self.router = Router()
        self.router.callback_query.register(self.handle_point, self.FSM.waiting_point)
        self.router.callback_query.register(self.handle_date, self.FSM.waiting_date)
        self.router.callback_query.register(
            self.handle_measure, self.FSM.waiting_measure
        )
        self.router.callback_query.register(self.handle_back, self.FSM.showing_info)

    async def entry_point(self, message_or_callback, state: FSMContext):
        trip_forecast = await state.get_value("trip_forecast")
        points = trip_forecast.trip.get_points()
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=str(point), callback_data=str(index))]
                for index, point in enumerate(points)
            ]
            + [[InlineKeyboardButton(text=messages["end"], callback_data="end")]]
        )
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(messages["point"], reply_markup=keyboard)
        elif isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.edit_text(
                messages["point"], reply_markup=keyboard
            )
        logging.info("send choose point")
        await state.set_state(self.FSM.waiting_point)
        logging.info("set waiting for choose point state")

    async def handle_point(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        trip_forecast = await state.get_value("trip_forecast")
        points = trip_forecast.trip.get_points()
        answer = callback_query.data
        logging.info("got choose point: " + answer)
        if answer == "end":
            await callback_query.answer(messages["goodbye"])
            await callback_query.message.delete()
            await state.clear()
        else:
            if not answer.isdigit() or int(answer) not in range(len(points)):
                await callback_query.message.answer("Команда не распознана")
                return
            choosen_point = points[int(answer)]
            await state.update_data(point=choosen_point)
            await self.ask_date(callback_query, state)

    async def ask_date(self, callback_query: types.CallbackQuery, state: FSMContext):
        await state.update_data(back_callback=self.entry_point)
        trip_forecast = await state.get_value("trip_forecast")
        choosen_point = await state.get_value("point")
        forecast = trip_forecast.forecast[str(choosen_point)]
        await state.update_data(forecast=forecast)

        if trip_forecast.forecast[str(choosen_point)] is None:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=messages["back"], callback_data="back")]
                ]
            )
            await state.set_state(self.FSM.showing_info)
            logging.info("set showing info state")
            await callback_query.message.edit_text(
                messages["forecast_error"], reply_markup=keyboard
            )
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Все даты", callback_data="all")]
            ]
            + [
                [
                    InlineKeyboardButton(
                        text=str(forecast.format_date()), callback_data=str(index)
                    )
                ]
                for index, forecast in enumerate(
                    trip_forecast.forecast[str(choosen_point)]
                )
            ]
            + [[InlineKeyboardButton(text=messages["back"], callback_data="back")]]
        )

        await callback_query.message.edit_text(
            messages["date"].format(choosen_point), reply_markup=keyboard
        )
        logging.info("ask for date")
        await state.set_state(self.FSM.waiting_date)
        logging.info("waiting for date state")

    async def handle_date(self, callback_query: types.CallbackQuery, state: FSMContext):
        await state.update_data(back_callback=self.ask_date)
        answer = callback_query.data
        forecast = await state.get_value("forecast")
        logging.info("got choose date: " + answer)
        if answer == "back":
            await self.entry_point(callback_query, state)
        elif answer == "all":
            await self.ask_measure(callback_query, state)
        else:
            if not answer.isdigit() or int(answer) not in range(len(forecast)):
                await callback_query.answer(messages["command_error"])
                return
            await state.update_data(date_forecast=forecast[int(answer)])
            await self.show_day_forecast(callback_query, state)

    async def show_day_forecast(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=messages["back"], callback_data="back")]
            ]
        )
        date_forecast = await state.get_value("date_forecast")
        if date_forecast is None:
            await callback_query.message.edit_text(
                messages["forecast_error"], reply_markup=keyboard
            )
            return
        await callback_query.message.edit_text(
            str(date_forecast), reply_markup=keyboard
        )
        await state.set_state(self.FSM.showing_info)
        logging.info("set showing info state")

    async def ask_measure(self, callback_query: types.CallbackQuery, state: FSMContext):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=messages["min_temp"], callback_data="min_temp"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["max_temp"], callback_data="max_temp"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["wind_speed"], callback_data="wind_speed"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=messages["precipitation_mm"],
                        callback_data="precipitation_mm",
                    )
                ],
                [InlineKeyboardButton(text=messages["back"], callback_data="back")],
            ]
        )
        await callback_query.message.edit_text(
            messages["measure"], reply_markup=keyboard
        )
        logging.info("ask for measure")
        await state.set_state(self.FSM.waiting_measure)
        logging.info("waiting for measure state")

    async def handle_measure(
        self, callback_query: types.CallbackQuery, state: FSMContext
    ):
        await state.update_data(back_callback=self.ask_measure)
        logging.info("got measure: " + callback_query.data)
        await state.update_data(measure=callback_query.data)
        await self.ask_additional_points(callback_query, state)

    async def handle_back(self, callback_query: types.CallbackQuery, state: FSMContext):
        logging.info("got back: " + callback_query.data)
        callback = await state.get_value("back_callback")
        try:
            await callback(callback_query, state)
        except Exception as e:
            logging.error(e)
            await self.entry_point(callback_query, state)
