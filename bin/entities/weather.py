from datetime import date

from bin.entities.geo_point import GeoPoint


class Weather:
    def __init__(
        self,
        point: GeoPoint,
        date: date,
        temp_min: float,
        temp_max: float,
        wind_speed: float,
        precipitation_mm: float,
        condition: str,
    ):
        self.point = point
        self.date = date
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.wind_speed = wind_speed
        self.precipitation_mm = precipitation_mm
        self.condition = condition

    def __str__(self):
        return (
            f"🌍 {str(self.point)}\n"
            f"🗓️ {self.format_date()}:\n\n"
            f"🌡️ Температура: от {self.temp_min}°C до {self.temp_max}°C\n"
            f"💨 Ветер: {self.wind_speed} м/с\n"
            f"🌧️ Осадки: {self.precipitation_mm} мм\n"
            f"️☀️ Условия: {self.condition}"
        )

    def format_date(self):
        return self.date.strftime("%-d %B %Y")