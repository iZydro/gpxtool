#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import tkinter
import os
import urllib.request
import configparser

import globalmaptiles
import gpxread
import screen_points
import helpers


class WGS84Coordinates():

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def get_lat_lon(self):
        return self.lat, self.lon


class CanvasCoordinates():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_x_y(self):
        return self.x, self.y


class GPXTool(tkinter.Tk):

    image = None
    background = None

    distance_box = None
    time_box = None
    dist_box = None
    speed_box = None

    panning = False
    top = 0
    left = 0
    bottom = 0
    right = 0

    scale_x = 0
    scale_y = 0

    PAN_MODE = 0
    MOVE_POINT_MODE = 1

    pressed_canvas_coordinates = None
    moved_canvas_coordinates = None
    motion_mode = PAN_MODE
    screen_point_selected = None

    wgs84_coordinates = None
    zoom = 1

    canvas_width = 640
    canvas_height = 640

    gpx_read = None
    mercator = None
    screen_points = None
    gpx_points = []
    gpx_points_number = 0

    lat_box = None
    lon_box = None

    config = None

    def __init__(self, parent):

        try:
            os.stat("../tmp")
        except:
            os.mkdir("../tmp")

        config = configparser.ConfigParser()
        config.read("../tmp/config.ini")
        if "files" not in config:
            config.add_section("files")
        if "last_file" not in config["files"]:
            config["files"]["last_file"] = "/Users/isidro/Desktop/mine/tmp_track/activity_37192771.gpx"
        with open('../tmp/config.ini', 'w') as configfile:
            config.write(configfile)

        tkinter.Tk.__init__(self, parent)

        self.parent = parent

        self.grid()

        self.columnconfigure(0, pad=0)
        self.columnconfigure(1, pad=0)
        self.rowconfigure(0, pad=0)
        self.rowconfigure(1, pad=0)
        self.rowconfigure(2, pad=0)
        self.rowconfigure(3, pad=0)

        self.bind("<Key>", self.key)

        self.entryVariable = tkinter.StringVar()
        self.entry = tkinter.Entry(self, textvariable=self.entryVariable)
        self.entry.grid(column=0, row=0, sticky='EW')
        self.entry.bind("<Return>", self.on_press_enter)
        self.entryVariable.set("Hello World")

        self.canvas_width = 640
        self.canvas_height = 640
        self.background = tkinter.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.background.grid(column=1, row=2, rowspan=100)

        button = tkinter.Button(self, text="Click me !",
                                command=self.on_button_click)
        button.grid(column=1, row=0)

        self.labelVariable = tkinter.StringVar()
        label = tkinter.Label(self, textvariable=self.labelVariable,
                              anchor="w", fg="white", bg="blue")
        label.grid(column=0, row=1, columnspan=2, sticky='EW')

        self.mercator = globalmaptiles.GlobalMercator()

        self.gpx_read = gpxread.GPXRead()
        self.gpx_points = self.gpx_read.read_points(config["files"]["last_file"])
        self.gpx_points_number = len(self.gpx_points)

        self.screen_points = screen_points.ScreenPoints(self, self.background, len(self.gpx_read.points))

        # Center the map on the initial coordinates of the track
        starting_point = self.gpx_read.get_starting_point()
        self.wgs84_coordinates = WGS84Coordinates(lat=starting_point.get_lat(), lon=starting_point.get_lon())
        self.zoom = 17
        self.set_entry_variable(self.wgs84_coordinates, self.zoom)

        self.distance_box = tkinter.Label(self, height=1, width=64, bg="#00ff00")
        self.distance_box.config(text="Total:" + str(self.gpx_read.calculate_total_distance()))
        self.distance_box.config(anchor="w")
        self.distance_box.grid(column=0, row=2, pady=0, padx=0)

        points_box = tkinter.Label(self, height=1, width=64, bg="#ff0000")
        points_box.config(text="Points:" + str(len(self.gpx_read.points)))
        points_box.config(anchor="w")
        points_box.grid(column=0, row=3, pady=0, padx=0)

        self.lat_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Lat:" + "dummy")
        self.lat_box.config(anchor="w")
        self.lat_box.grid(column=0, row=4, pady=0, padx=0)

        self.lon_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Lon:" + "dummy")
        self.lon_box.config(anchor="w")
        self.lon_box.grid(column=0, row=5, pady=0, padx=0)

        self.time_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Time:" + "dummy")
        self.time_box.config(anchor="w")
        self.time_box.grid(column=0, row=6, pady=0, padx=0)

        self.dist_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Dist:" + "dummy")
        self.dist_box.config(anchor="w")
        self.dist_box.grid(column=0, row=7, pady=0, padx=0)

        self.speed_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Speed:" + "dummy")
        self.speed_box.config(anchor="w")
        self.speed_box.grid(column=0, row=8, pady=0, padx=0)

        self.number_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Point #:" + "dummy")
        self.number_box.config(anchor="w")
        self.number_box.grid(column=0, row=9, pady=0, padx=0)

        self.update_wgs84_coordinates_from_text_and_download_map(self.entryVariable.get().split(","))

        self.calculate_scale()
        self.draw_points()

        self.background.bind("<ButtonPress-1>", self.press_button)
        self.background.bind("<ButtonRelease-1>", self.release_button)
        self.background.bind("<B1-Motion>", self.motion_button)

        self.background.bind("<ButtonPress-2>", self.press_right_button)

        self.background.bind("<Motion>", self.motion)

        self.grid_columnconfigure(0, weight=1)
        self.resizable(True, False)
        self.update()
        self.geometry(self.geometry())

        self.canvas_coordinates = CanvasCoordinates(0, 0)
        self.pressed_canvas_coordinates = CanvasCoordinates(0, 0)
        self.moved_canvas_coordinates = CanvasCoordinates(0, 0)
        self.top_left = [0, 0]
        self.bottom_right = [0, 0]

    def set_entry_variable(self, wgs84_coordinates, zoom):
        value = str(wgs84_coordinates.lat) + "," + str(wgs84_coordinates.lon) + "," + str(zoom)
        self.entryVariable.set(value)

    def set_entry_variable_from_text(self, values_array):
        value = str(values_array[0]) + "," + str(values_array[1]) + "," + str(values_array[2])
        self.entryVariable.set(value)

    def key(self, event):
        print("pressed", repr(event.char))
        if event.char == "+":
            self.change_zoom(1)
        elif event.char == "-":
            self.change_zoom(-1)

    def press_button(self, event):
        print("clicked at", event.x, event.y)

        screen_point_found = self.screen_points.point_at(event.x, event.y)
        if screen_point_found != -1:
            self.motion_mode = self.MOVE_POINT_MODE
            self.screen_point_selected = screen_point_found
        else:
            self.motion_mode = self.PAN_MODE

        self.pressed_canvas_coordinates.y = event.y
        self.pressed_canvas_coordinates.x = event.x
        self.background.focus_set()

    def motion_button(self, event):

        if self.motion_mode == self.PAN_MODE:
            self.moved_canvas_coordinates.y = + (event.y - self.pressed_canvas_coordinates.y)
            self.moved_canvas_coordinates.x = - (event.x - self.pressed_canvas_coordinates.x)
            old_coordinates = WGS84Coordinates(self.wgs84_coordinates.lat, self.wgs84_coordinates.lon)

            new_wsg84_coordinates = WGS84Coordinates(0, 0)
            new_wsg84_coordinates.lon = old_coordinates.lon + float(self.moved_canvas_coordinates.x) * self.scale_y
            new_wsg84_coordinates.lat = old_coordinates.lat + float(self.moved_canvas_coordinates.y) * self.scale_x

            self.lat_box.config(text="Lat:" + str(new_wsg84_coordinates.lat))
            self.lon_box.config(text="Lon:" + str(new_wsg84_coordinates.lon))

            self.background.delete(tkinter.ALL)
            self.background.create_image(self.canvas_width / 2 - self.moved_canvas_coordinates.x,
                                         self.canvas_height / 2 + self.moved_canvas_coordinates.y,
                                         image=self.image)

        if self.motion_mode == self.MOVE_POINT_MODE:
            self.moved_canvas_coordinates.y = - event.y
            self.moved_canvas_coordinates.x = + event.x

            old_coordinates = WGS84Coordinates(self.bottom, self.left)  # self.wgs84_coordinates.lat, self.wgs84_coordinates.lon)

            new_wsg84_coordinates = WGS84Coordinates(0, 0)
            new_wsg84_coordinates.lon = old_coordinates.lon + float(self.moved_canvas_coordinates.x) * self.scale_y
            new_wsg84_coordinates.lat = old_coordinates.lat + float(self.moved_canvas_coordinates.y) * self.scale_x

            self.background.delete(self.screen_points.points[self.screen_point_selected].get_rectangle())

            self.gpx_points[self.screen_points.points[self.screen_point_selected].get_gpx_point_number()].lat = new_wsg84_coordinates.lat
            self.gpx_points[self.screen_points.points[self.screen_point_selected].get_gpx_point_number()].lon = new_wsg84_coordinates.lon

            self.draw_point(self.screen_point_selected)

            self.update_point_data(self.screen_point_selected)

            total_distance = self.gpx_read.calculate_total_distance()
            self.distance_box.config(text="Dist:" + str(total_distance))

    def release_button(self, event):

        if self.motion_mode == self.PAN_MODE:
            self.moved_canvas_coordinates.y = + (event.y - self.pressed_canvas_coordinates.y)
            self.moved_canvas_coordinates.x = - (event.x - self.pressed_canvas_coordinates.x)

            old_coordinates = WGS84Coordinates(self.wgs84_coordinates.lat, self.wgs84_coordinates.lon)

            new_wsg84_coordinates = WGS84Coordinates(0, 0)
            new_wsg84_coordinates.lon = old_coordinates.lon + float(self.moved_canvas_coordinates.x) * self.scale_y
            new_wsg84_coordinates.lat = old_coordinates.lat + float(self.moved_canvas_coordinates.y) * self.scale_x

            self.set_entry_variable(new_wsg84_coordinates, self.zoom)
            self.update_wgs84_coordinates_and_download_map(new_wsg84_coordinates, self.zoom)
            self.calculate_scale()
            self.draw_points()

    def press_right_button(self, event):

        self.moved_canvas_coordinates.y = - (event.y - self.canvas_height / 2)
        self.moved_canvas_coordinates.x = + (event.x - self.canvas_width / 2)

        old_coordinates = WGS84Coordinates(self.wgs84_coordinates.lat, self.wgs84_coordinates.lon)

        new_wsg84_coordinates = WGS84Coordinates(0, 0)
        new_wsg84_coordinates.lon = old_coordinates.lon + float(self.moved_canvas_coordinates.x) * self.scale_y
        new_wsg84_coordinates.lat = old_coordinates.lat + float(self.moved_canvas_coordinates.y) * self.scale_x

        self.set_entry_variable(new_wsg84_coordinates, self.zoom)
        self.update_wgs84_coordinates_and_download_map(new_wsg84_coordinates, self.zoom)
        self.calculate_scale()
        self.draw_points()

    def motion(self, event):

        screen_point_found = self.screen_points.point_at(event.x, event.y)
        if screen_point_found != -1:
            # Fill to green point under cursor
            self.background.itemconfigure(self.screen_points.points[screen_point_found].get_rectangle(), fill="#00ff00")

        if self.screen_points.highlighted != -1 and self.screen_points.highlighted != screen_point_found:
            # Fill to red previous highlighted point (if existed)
            self.background.itemconfigure(self.screen_points.points[self.screen_points.highlighted].get_rectangle(), fill="#ff0000")

        if screen_point_found != -1:
            # Update current highlighted point
            self.screen_points.highlighted = screen_point_found
            self.update_point_data(screen_point_found)

        self.moved_canvas_coordinates.y = - event.y
        self.moved_canvas_coordinates.x = + event.x

        old_coordinates = WGS84Coordinates(self.wgs84_coordinates.lat, self.wgs84_coordinates.lon)

        new_wsg84_coordinates = WGS84Coordinates(0, 0)
        new_wsg84_coordinates.lon = old_coordinates.lon + float(self.moved_canvas_coordinates.x) * self.scale_y
        new_wsg84_coordinates.lat = old_coordinates.lat + float(self.moved_canvas_coordinates.y) * self.scale_x

        self.lat_box.config(text="Lat:" + str(new_wsg84_coordinates.lat))
        self.lon_box.config(text="Lon:" + str(new_wsg84_coordinates.lon))

    def calculate_scale(self):
        old_coordinates = self.entryVariable.get().split(",")
        lat = float(old_coordinates[0])
        lon = float(old_coordinates[1])
        tz = float(old_coordinates[2])
        mx, my = self.mercator.LatLonToMeters(lat=lat, lon=lon)
        current_tile_x, current_tile_y = self.mercator.MetersToTile(mx, my, tz)
        wgs_bounds = self.mercator.TileLatLonBounds(current_tile_x, current_tile_y, tz)

        self.scale_x = (wgs_bounds[2] - wgs_bounds[0]) / 256
        self.scale_y = (wgs_bounds[3] - wgs_bounds[1]) / 256

        self.left = lon - (self.canvas_width / 2) * self.scale_y
        self.right = lon + (self.canvas_width / 2) * self.scale_y
        self.top = lat - (self.canvas_height / 2) * self.scale_x
        self.bottom = lat + (self.canvas_height / 2) * self.scale_x

    def update_wgs84_coordinates_and_download_map(self, wsg84_coordinates, zoom):

        self.wgs84_coordinates = wsg84_coordinates
        self.zoom = zoom

        self.update_wgs84_coordinates_from_text_and_download_map(
            [
                str(wsg84_coordinates.lat),
                str(wsg84_coordinates.lon),
                str(zoom)
            ]
        )

    def update_wgs84_coordinates_from_text_and_download_map(self, text_array):

        self.wgs84_coordinates.lat = float(text_array[0])
        self.wgs84_coordinates.lon = float(text_array[1])
        self.zoom = int(text_array[2])

        request = "http://maps.google.com/maps/api/staticmap?center="
        request += str(text_array[0]) + "," + str(text_array[1])
        request += "&zoom=" + str(text_array[2])
        request += "&size=" + str(self.canvas_width)
        request += "x"
        request += str(self.canvas_height)
        request += "&format=gif&maptype=hybrid&sensor=false"
        request += "&key=AIzaSyBOP8yEyxoR2jYdYBf4th6hSgdaUeWsBx0"
        print(request)
        try:
            urllib.request.urlretrieve(request, "../tmp/caca.gif")
            image = tkinter.PhotoImage(file="../tmp/caca.gif")
            self.image = image
        except:
            self.image = None
            pass
        self.background.delete(tkinter.ALL)

        if self.image:
            self.background.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.image)

#        self.lat_box.config(text=self.wgs84_coordinates.lat)
#        self.lon_box.config(text=self.wgs84_coordinates.lon)

    def update_point_data(self, screen_point):
        time, distance = self.gpx_read.calculate_point_data(self.screen_points.points[screen_point].get_gpx_point_number())
        self.dist_box.config(text="Dist: " + helpers.to_decimal(distance, 3))
        self.time_box.config(text="Time: " + str(time))
        self.speed_box.config(text="Speed: " + helpers.to_decimal(distance / time.seconds) + " m/s")
        self.number_box.config(text="Point #" + helpers.to_decimal(self.screen_points.points[screen_point].get_gpx_point_number(), 0))

    def change_zoom(self, offset):
        new_coordinates = self.entryVariable.get().split(",")
        zoom = int(new_coordinates[2])
        zoom += offset
        new_coordinates[2] = zoom
        self.set_entry_variable_from_text(new_coordinates)
        self.update_wgs84_coordinates_from_text_and_download_map(new_coordinates)
        self.calculate_scale()
        self.draw_points()

    def on_button_click(self):
        self.labelVariable.set(self.entryVariable.get() + " (You clicked the button)")
        self.update_wgs84_coordinates_from_text_and_download_map(self.entryVariable.get().split(","))
        self.calculate_scale()
        self.draw_points()

    def on_press_enter(self, event):
        self.labelVariable.set(self.entryVariable.get() + " (You pressed Enter)" + event.char)
        self.update_wgs84_coordinates_from_text_and_download_map(self.entryVariable.get().split(","))
        self.calculate_scale()
        self.draw_points()

    def draw_points(self):
        self.screen_points.clear()
        for gpx_point_num in range(self.gpx_points_number):
            self.draw_point(-1, gpx_point_num)

    def draw_point(self, screen_point_number, gpx_point_number=None):
        old_lat = self.wgs84_coordinates.lat
        old_lon = self.wgs84_coordinates.lon

        if screen_point_number == -1:
            # Use the new GPX point passed as parameter
            pass
        else:
            # Get GPX point from already existing Screen Point
            gpx_point_number = self.screen_points.points[screen_point_number].get_gpx_point_number()

        lon = self.gpx_points[gpx_point_number].lon
        lat = self.gpx_points[gpx_point_number].lat
        if self.left < lon < self.right and self.top < lat < self.bottom:
            x_offset = self.canvas_width / 2 + (lon - old_lon) / self.scale_y
            y_offset = self.canvas_height / 2 + (old_lat - lat) / self.scale_x
            return self.screen_points.update(screen_point_number, gpx_point_number, x_offset, y_offset)

if __name__ == "__main__":
    app = GPXTool(None)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    app.title('Zydro GPX tool')

    app.mainloop()
