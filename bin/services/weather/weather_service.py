import logging
from bin.entities.trip import Trip
from bin.entities.trip_forecast import TripForecast
from bin.services.weather.yandex_weather_client import YandexWeatherClient


class WeatherService:
    def __init__(self, repository: YandexWeatherClient):
        self.repository = repository

    def get_weather_in_trip(self, trip: Trip):
        points = [trip.start] + trip.additional_points + [trip.end]
        forecast = {}
        for point in points:
            try:
                forecast[str(point)] = self.repository.get_weather_forecast(
                    point=point, days=trip.duration
                )
            except Exception as e:
                logging.error(e)
                forecast[str(point)] = None

        return TripForecast(trip, forecast)
