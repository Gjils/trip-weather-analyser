from bin.entities.geo_point import GeoPoint


class Trip:
    def __init__(
        self,
        start: GeoPoint,
        end: GeoPoint,
        additional_points: list[GeoPoint],
        duration: int,
    ):
        self.start = start
        self.end = end
        self.additional_points = additional_points
        self.duration = duration

    def get_points(self):
        if self.additional_points is None:
            self.additional_points = []
        return [self.start] + self.additional_points + [self.end]
