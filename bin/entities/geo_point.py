class GeoPoint:
    def __init__(self, latitude: float, longitude: float, city: str):
        self.latitude = latitude
        self.longitude = longitude
        self.city = city

    def __str__(self):
        return f"{self.city} ({self.longitude}, {self.latitude})"
