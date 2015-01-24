class ScreenPoint:
    def __init__(self, x, y, rectangle, gpx_point):
        self.x = x
        self.y = y
        self.rectangle = rectangle
        self.gpx_point = gpx_point

    def get(self):
        return self.x, self.y, self.rectangle, self.gpx_point

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_rectangle(self):
        return self.rectangle

    def get_gpx_point(self):
        return self.gpx_point


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

    def point_at(self, x, y) -> ScreenPoint:
        for point in self.points:
            px = point.get_x()
            py = point.get_y()
            if abs(px - x) < 8 and abs(py - y) < 8:
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
        found = self.find_gpx_value(gpx_point)
        screen_point = ScreenPoint(x_offset, y_offset, rectangle, gpx_point)
        if found != -1:
            self.points[found] = screen_point
        else:
            self.points.append(screen_point)

        return screen_point

    def find_gpx_value(self, value):
        index = 0
        for item in self.points:
            if item.get_gpx_point() == value:
                return index
            index += 1
        return -1
