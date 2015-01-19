#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import tkinter
import os
import urllib.request

import globalmaptiles
import gpxread


class WGS84Coordinates():

    lat = 0
    lon = 0

    def __init__(self, val_lat, val_lon):
        self.lat = val_lat
        self.lon = val_lon

    def get_lat_lon(self):
        return self.lat, self.lon


class CanvasCoordinates():

    x = 0
    y = 0

    def __init__(self, val_x, val_y):
        self.x = val_x
        self.y = val_y

    def get_x_y(self):
        return self.x, self.y


class GPXTool(tkinter.Tk):

    image = None
    background = None
    panning = False
    top = 0
    left = 0
    bottom = 0
    right = 0

    scale_x = 0
    scale_y = 0

    pressed_canvas_coordinates = None
    moved_canvas_coordinates = None
    wgs84_coordinates = None
    zoom = 1

    canvas_width = 640
    canvas_height = 640

    gpx_read = None
    mercator = None
    points = []

    lat_box = None
    lon_box = None

    def __init__(self, parent):
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

        button = tkinter.Button(self, text="Click me !",
                                command=self.on_button_click)
        button.grid(column=1, row=0)

        self.labelVariable = tkinter.StringVar()
        label = tkinter.Label(self, textvariable=self.labelVariable,
                              anchor="w", fg="white", bg="blue")
        label.grid(column=0, row=1, columnspan=2, sticky='EW')

        self.mercator = globalmaptiles.GlobalMercator()

        self.gpx_read = gpxread.GPXRead()
        self.points = self.gpx_read.read_points()

        # Center the map on the initial coordinates of the track
        starting_point = self.gpx_read.get_starting_point()
        self.wgs84_coordinates = WGS84Coordinates(starting_point["lat"], starting_point["lon"])
        self.zoom = 17
        self.set_entry_variable(self.wgs84_coordinates, self.zoom)

        distance_box = tkinter.Label(self, height=1, width=64, bg="#00ff00", text="Total:" + str(self.gpx_read.calculate_total_distance()))
        distance_box.config(anchor="w")
        distance_box.grid(column=0, row=2, pady=0, padx=0)

        points_box = tkinter.Label(self, height=1, width=64, bg="#ff0000", text="Points:" + str(len(self.gpx_read.points)))
        points_box.config(anchor="w")
        points_box.grid(column=0, row=3, pady=0, padx=0)

        self.lat_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Lat:" + "dummy")
        self.lat_box.config(anchor="w")
        self.lat_box.grid(column=0, row=4, pady=0, padx=0)

        self.lon_box = tkinter.Label(self, height=1, width=64, bg="#8080ff", text="Lon:" + "dummy")
        self.lon_box.config(anchor="w")
        self.lon_box.grid(column=0, row=5, pady=0, padx=0)

        self.canvas_width = 640
        self.canvas_height = 640
        self.background = tkinter.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.background.grid(column=1, row=2, rowspan=100)
        self.update_wgs84_coordinates_from_text_and_download_map(self.entryVariable.get().split(","))

        self.calculate_scale()
        self.draw_points()

        self.background.bind("<ButtonPress-1>", self.press_button)
        self.background.bind("<ButtonRelease-1>", self.release_button)
        self.background.bind("<B1-Motion>", self.motion_button)

        self.background.bind("<ButtonPress-2>", self.press_right_button)

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
        print ("pressed", repr(event.char))
        if event.char == "+":
            self.change_zoom(1)
        elif event.char == "-":
            self.change_zoom(-1)

    def press_button(self, event):
        print ("clicked at", event.x, event.y)
        self.pressed_canvas_coordinates.y = event.y
        self.pressed_canvas_coordinates.x = event.x
        self.background.focus_set()

    def motion_button(self, event):
        print ("motion at", event.x, event.y)
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

    def release_button(self, event):
        print ("released at", event.x, event.y)
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
        print ("Right clicked at", event.x, event.y)
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

    def calculate_scale(self):
        old_coordinates = self.entryVariable.get().split(",")
        lat = float(old_coordinates[0])
        lon = float(old_coordinates[1])
        tz = float(old_coordinates[2])
        mx, my = self.mercator.LatLonToMeters(lat, lon)
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
        urllib.request.urlretrieve(request, "caca.gif")
        image = tkinter.PhotoImage(file="./caca.gif")
        self.image = image
        self.background.delete(tkinter.ALL)
        self.background.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.image)

#        self.lat_box.config(text=self.wgs84_coordinates.lat)
#        self.lon_box.config(text=self.wgs84_coordinates.lon)

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
        old_coordinates = self.entryVariable.get().split(",")
        old_lat = float(old_coordinates[0])
        old_lon = float(old_coordinates[1])

        for point in self.points:
            lon = float(point["lon"])
            lat = float(point["lat"])
            if self.left < lon < self.right and self.top < lat < self.bottom:
                x_offset = self.canvas_width / 2 + (lon - old_lon) / self.scale_y
                y_offset = self.canvas_height / 2 + (old_lat - lat) / self.scale_x

                self.background.create_rectangle(x_offset - 4,
                                                 y_offset - 4,
                                                 x_offset + 4,
                                                 y_offset + 4,
                                                 fill="#ff0000")

if __name__ == "__main__":
    app = GPXTool(None)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    app.title('Zydro GPX tool')

    app.mainloop()
