from bin.entities.geo_point import GeoPoint
from bin.services.geo_points.yandex_geocoder_client import YandexGeocoderClient


class GeoPointService:
    def __init__(self, repository: YandexGeocoderClient):
        self.repository = repository

    def get_point_by_coordinates(self, latitude: float, longitude: float):
        city = self.repository.get_city_by_coordinates(latitude, longitude)
        return GeoPoint(latitude=latitude, longitude=longitude, city=city)
    
    def get_point_by_city(self, city: str):
        latitude, longitude = self.repository.get_coordinates_by_city(city)
        return GeoPoint(latitude=latitude, longitude=longitude, city=city)