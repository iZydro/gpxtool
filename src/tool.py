#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
import os
import urllib

import globalmaptiles


class GPXTool(Tkinter.Tk):
    
    image = None
    background = None
    panning = False
    coordinates = []
    moved = []
    
    canvas_width = 256
    canvas_height = 256

    mercator = None
    
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent

        self.grid()

        self.bind("<Key>", self.key)

        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self, textvariable=self.entryVariable)
        self.entry.grid(column=0, row=0, sticky='EW')
        self.entry.bind("<Return>", self.on_press_enter)
        self.entryVariable.set("Hello World")

        button = Tkinter.Button(self, text="Click me !",
                                command=self.on_button_click)
        button.grid(column=1, row=0)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self, textvariable=self.labelVariable,
                              anchor="w", fg="white", bg="blue")
        label.grid(column=0, row=1, columnspan=2, sticky='EW')
        
        self.coordinates = (41.406271, 2.212483, 17)
        self.set_entry_variable(self.coordinates)

        self.canvas_width = 640
        self.canvas_height = 640
        self.background = Tkinter.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.background.grid(column=0, row=2, columnspan=2)
        self.update_coordinates(self.entryVariable.get().split(","))

        self.background.create_rectangle(100, 100, 20, 20, fill="#ff0000")
        
        self.background.bind("<ButtonPress-1>", self.press_button)
        self.background.bind("<ButtonRelease-1>", self.release_button)
        self.background.bind("<B1-Motion>", self.motion_button)

        self.grid_columnconfigure(0, weight=1)
        self.resizable(True, False)
        self.update()
        self.geometry(self.geometry())       

        self.coordinates = [0, 0, 0]
        self.moved = [0, 0]

        self.mercator = globalmaptiles.GlobalMercator()

    def set_entry_variable(self, values_array):
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
        self.coordinates[0] = event.y
        self.coordinates[1] = event.x
        self.background.focus_set()

    def motion_button(self, event):
        print ("motion at", event.x, event.y)
        self.moved[0] = event.y - self.coordinates[0]
        self.moved[1] = - (event.x - self.coordinates[1])
        self.background.delete(Tkinter.ALL)
        self.background.create_image(self.canvas_width / 2 - self.moved[1],
                                     self.canvas_height / 2 + self.moved[0],
                                     image=self.image)

    def release_button(self, event):
        print ("clicked at", event.x, event.y)
        self.moved[0] = event.y - self.coordinates[0]
        self.moved[1] = - (event.x - self.coordinates[1])

        print (self.moved)

        old_coordinates = self.entryVariable.get().split(",")
        print(old_coordinates)
        lat = float(old_coordinates[0])
        lon = float(old_coordinates[1])
        tz = float(old_coordinates[2])
        mx, my = self.mercator.LatLonToMeters(lat, lon)
        print ("Spherical Mercator (ESPG:900913) coordinates for lat/lon: ")
        print (mx, my)
        current_tile_x, current_tile_y = self.mercator.MetersToTile(mx, my, tz)
        wgs_bounds = self.mercator.TileLatLonBounds(current_tile_x, current_tile_y, tz)

        scale_x = (wgs_bounds[2] - wgs_bounds[0]) / 256
        scale_y = (wgs_bounds[3] - wgs_bounds[1]) / 256

        old_coordinates = self.entryVariable.get().split(",")
        new_coordinates = [0, 0, 0]
        new_coordinates[0] = float(old_coordinates[0]) + float(self.moved[0]) * scale_x
        new_coordinates[1] = float(old_coordinates[1]) + float(self.moved[1]) * scale_y
        new_coordinates[2] = old_coordinates[2]
        self.update_coordinates(new_coordinates)
        self.set_entry_variable(new_coordinates)

    def update_coordinates(self, coordinates):

        request = "http://maps.google.com/maps/api/staticmap?center="
        request += str(coordinates[0]) + "," + str(coordinates[1]) + "&zoom=" + str(coordinates[2])
        request += "&size=" + str(self.canvas_width)
        request += "x"
        request += str(self.canvas_height)
        request += "&format=gif&maptype=hybrid&sensor=false"
        request += "&key=AIzaSyBOP8yEyxoR2jYdYBf4th6hSgdaUeWsBx0"
        print(request)
        urllib.urlretrieve(request, "caca.gif")
        image = Tkinter.PhotoImage(file="./caca.gif")
        self.image = image
        self.background.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.image)

    def change_zoom(self, offset):
        new_coordinates = self.entryVariable.get().split(",")
        zoom = int(new_coordinates[2])
        zoom += offset
        new_coordinates[2] = zoom
        self.update_coordinates(new_coordinates)
        self.entryVariable.set(str(new_coordinates[0]) + "," + str(new_coordinates[1]) + "," + str(new_coordinates[2]))

    def on_button_click(self):
        self.labelVariable.set(self.entryVariable.get() + " (You clicked the button)")
        self.update_coordinates(self.entryVariable.get().split(","))
        print("Focus get " + self.focus_get())

    def on_press_enter(self, event):
        self.labelVariable.set(self.entryVariable.get() + " (You pressed Enter)" + event.char)
        self.update_coordinates(self.entryVariable.get().split(","))

if __name__ == "__main__":
    app = GPXTool(None)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    app.title('Zydro GPX tool')
    
    app.mainloop()
