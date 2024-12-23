import logging
import matplotlib.pyplot as plt
from io import BytesIO
from bin.entities.geo_point import GeoPoint
from bin.entities.trip import Trip
from bin.entities.trip_forecast import TripForecast
from bin.entities.weather import Weather
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

    def plot_forecast_measure(
        self, trip_forecast: TripForecast, point: GeoPoint, measure: str
    ) -> BytesIO:
        valid_measures = ["temp_min", "temp_max", "wind_speed", "precipitation_mm"]
        if measure not in valid_measures:
            raise ValueError(f"Invalid measure. Choose from {valid_measures}.")

        dates = []
        values = []
        for weather in trip_forecast.forecast[str(point)]:
            dates.append(weather.format_date_short())
            values.append(getattr(weather, measure))

        sorted_data = sorted(zip(dates, values), key=lambda x: x[0])
        dates, values = zip(*sorted_data)

        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, marker="o", label=Weather.get_measure_string(measure))
        plt.title(Weather.get_measure_string(measure))
        plt.xlabel("Дата")
        plt.ylabel(Weather.get_measure_with_units_string(measure))
        plt.grid(True)
        plt.xticks(rotation=45, ha="right")

        image_stream = BytesIO()
        plt.savefig(image_stream, format="png", bbox_inches="tight")
        plt.close()

        image_stream.seek(0)
        return image_stream
