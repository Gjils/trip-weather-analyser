import requests


class YandexGeocoderClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://geocode-maps.yandex.ru/1.x/"

    def get_city_by_coordinates(self, latitude: float, longitude: float) -> str:
        """
        Возвращает название города по заданным координатам.
        """
        params = {
            "apikey": self.api_key,
            "geocode": f"{longitude},{latitude}",
            "format": "json",
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        try:
            city = data["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"
            ]["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"][
                "AdministrativeArea"
            ][
                "AdministrativeAreaName"
            ]
            return city
        except (IndexError, KeyError) as e:
            raise ValueError(
                "Не удалось получить название города по координатам."
            ) from e

    def get_coordinates_by_city(self, city_name: str) -> tuple:
        """
        Возвращает координаты города в виде кортежа (широта, долгота).
        """
        params = {
            "apikey": self.api_key,
            "geocode": city_name,
            "format": "json",
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        try:
            coordinates = data["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"
            ]["Point"]["pos"]
            longitude, latitude = map(float, coordinates.split())
            return latitude, longitude
        except (IndexError, KeyError) as e:
            raise ValueError("Не удалось получить координаты города.") from e
