class ScreenPoint:
    def __init__(self, x, y, rectangle, gpx_point_number):
        self.x = x
        self.y = y
        self.rectangle = rectangle
        self.gpx_point_number = gpx_point_number

    def get(self):
        return self.x, self.y, self.rectangle, self.gpx_point_number

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_rectangle(self):
        return self.rectangle

    def get_gpx_point_number(self):
        return self.gpx_point_number


class ScreenPoints:

    points = []
    rectangles = []
    parent = None
    background = None

    def __init__(self, parent, background, max_points):
        self.parent = parent
        self.background = background
        self.clear()

#    Not really needed now
#    for counter in range(max_points):
#        rectangle = self.background.create_rectangle(0, 0, 0, 0, fill="#ff0000")
#        self.rectangles.append(rectangle)

    def clear(self):
        self.points = []

    def point_at(self, x, y) -> int:
        counter = 0
        for point in self.points:
            px = point.get_x()
            py = point.get_y()
            if abs(px - x) < 8 and abs(py - y) < 8:
                return counter
            counter += 1
        return -1

    def update(self, screen_point_number, gpx_point_number, x_offset, y_offset):

        rectangle = self.background.create_rectangle(
            x_offset - 4,
            y_offset - 4,
            x_offset + 4,
            y_offset + 4,
            fill="#ff0000"
        )

        # If points_in_screen already exists, replace its contents
        # If not, append a new point to points_in_screen

        if screen_point_number == -1 or screen_point_number >= len(self.points):
            found = False
        else:
            found = True

        if found:
            screen_point = self.points[screen_point_number]
            screen_point.rectangle = rectangle
            screen_point.x = x_offset
            screen_point.y = y_offset
        else:
            print("Added point!", screen_point_number, len(self.points))
            screen_point = ScreenPoint(x_offset, y_offset, rectangle, gpx_point_number)
            self.points.append(screen_point)

        return screen_point_number
