import requests
from datetime import datetime

from bin.entities.geo_point import GeoPoint
from bin.entities.weather import Weather


def condition_to_russian(condition):
    conditions = {
        "clear": "Ясно",
        "partly-cloudy": "Малооблачно",
        "cloudy": "Облачно с прояснениями",
        "overcast": "Пасмурно",
        "drizzle": "Морось",
        "rain": "Дождь",
        "snow": "Снег",
        "snow-showers": "Снегопад",
        "sleet": "Град",
        "wind": "Ветер",
        "fog": "Туман",
        "haze": "Туман",
        "wet-snow": "Дождь со снегом",
    }
    return conditions.get(condition, condition.capitalize())


class YandexWeatherClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weather.yandex.ru/v2/forecast"

    def get_weather_forecast(self, point: GeoPoint, days: int) -> list:
        if not (1 <= days <= 7):
            raise ValueError("Количество дней должно быть от 1 до 7.")

        headers = {
            "X-Yandex-API-Key": self.api_key,
        }
        params = {
            "lat": point.latitude,
            "lon": point.longitude,
            "lang": "ru_RU",
            "limit": days,
        }
        response = requests.get(self.base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        try:
            for day in data["forecasts"]:
                forecast_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
                temp_min = day["parts"]["day"]["temp_min"]
                temp_max = day["parts"]["day"]["temp_max"]
                condition = condition_to_russian(day["parts"]["day"]["condition"])
                wind_speed = day["parts"]["day"]["wind_speed"]
                precipitation_mm = day["parts"]["day"]["prec_mm"]

                weather_forecast = Weather(
                    point=point,
                    date=forecast_date,
                    temp_min=temp_min,
                    temp_max=temp_max,
                    wind_speed=wind_speed,
                    precipitation_mm=precipitation_mm,
                    condition=condition,
                )

                forecasts.append(weather_forecast)
        except KeyError as e:
            raise ValueError("Не удалось получить данные прогноза погоды.") from e

        return forecasts
