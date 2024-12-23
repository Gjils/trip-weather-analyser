from bin.entities.geo_point import GeoPoint
from bin.entities.trip import Trip
from bin.entities.weather import Weather


class TripForecast:
    def __init__(self, trip: Trip, forecast: dict[GeoPoint, list[Weather]]):
        self.trip = trip
        self.forecast = forecast
