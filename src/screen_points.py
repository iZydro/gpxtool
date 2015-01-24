class ScreenPoints:

    points = []
    parent = None
    background = None

    def __init__(self, parent, background):
        self.parent = parent
        self.background = background
        self.clear()

    def clear(self):
        self.points = []

    def point_at(self, x, y):
        for point in self.points:
            px = point["x"]
            py = point["y"]
            if abs(px - x) < 4 and abs(py - y) < 4:
                return point
        return None

    def update(self, gpx_point, x_offset, y_offset):

        rectangle = self.background.create_rectangle(
            x_offset - 4,
            y_offset - 4,
            x_offset + 4,
            y_offset + 4,
            fill="#ff0000"
        )

        # If points_in_screen already exists, replace its contents
        # If not, append a new point to points_in_screen
        found = self.parent.find(self.points, "gpxpoint", gpx_point)
        point = {"x": x_offset, "y": y_offset, "rectangle": rectangle, "gpxpoint": gpx_point}
        if found != -1:
            self.points[found] = point
        else:
            self.points.append(point)
