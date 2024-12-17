from bin.entities.geo_point import GeoPoint
from bin.entities.time_interval import TimeInterval

class Trip:
  def __init__(self, start: GeoPoint, end: GeoPoint, between: list[GeoPoint], date: TimeInterval):
    self.start = start
    self.end = end
    self.between = between
    self.date = date