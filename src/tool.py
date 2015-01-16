#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
import os
import urllib

import globalmaptiles

class simpleapp_tk(Tkinter.Tk):
    
    image = None
    background = None
    panning = False
    coords = []
    moved = []
    
    canvas_width = 256
    canvas_height = 256

    mercator = None
    
    scales = { 17:(100/110) }
    
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
        self.bind("<Key>", self.key)
        self.bind("<ButtonPress-1>", self.press_button)
        self.bind("<ButtonRelease-1>", self.release_button)
    

    def initialize(self):
        self.grid()

        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=0,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set("Hello World")

        button = Tkinter.Button(self,text="Click me !",
                                command=self.OnButtonClick)
        button.grid(column=1,row=0)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable,
                              anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=1,columnspan=2,sticky='EW')
        
        self.coords = (41.406271,2.212483,17)
        self.entryVariable.set(str(self.coords[0]) + "," + str(self.coords[1]) + "," + str(self.coords[2]))

        self.canvas_width = 256
        self.canvas_height = 256
        self.background = Tkinter.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.background.grid(column=0,row=2,columnspan=2)
        self.UpdateCoords(self.entryVariable.get().split(","))
        
        self.background.create_rectangle(100, 100, 20, 20, fill="#ff0000")
        
        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        self.geometry(self.geometry())       
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)
        
        self.coords = [0, 0, 0]
        self.moved = [0, 0]

        self.mercator = globalmaptiles.GlobalMercator()

    def key(self, event):
        print ("pressed", repr(event.char))
    
    def press_button(self, event):
        #frame.focus_set()
        print ("clicked at", event.x, event.y)
        self.coords[0] = event.y
        self.coords[1] = event.x

    def release_button(self, event):
        #frame.focus_set()
        print ("clicked at", event.x, event.y)
        self.moved[0] = event.y - self.coords[0]
        self.moved[1] = - (event.x - self.coords[1])

        print (self.moved)

        old_coords = self.entryVariable.get().split(",")
        print(old_coords)
        lat = float(old_coords[0])
        lon = float(old_coords[1])
        tz = float(old_coords[2])
        mx, my = self.mercator.LatLonToMeters( lat, lon )
        print ("Spherical Mercator (ESPG:900913) coordinates for lat/lon: ")
        print (mx, my)
        tminx, tminy = self.mercator.MetersToTile(mx, my, tz )
        wgsbounds = self.mercator.TileLatLonBounds(tminx, tminy, tz)

        scale_x = (wgsbounds[2] - wgsbounds[0]) / self.canvas_width
        scale_y = (wgsbounds[3] - wgsbounds[1]) / self.canvas_height

        old_coords = self.entryVariable.get().split(",")
        new_coords = [0, 0, 0]
        new_coords[0] = float(old_coords[0]) + float(self.moved[0]) * scale_x
        new_coords[1] = float(old_coords[1]) + float(self.moved[1]) * scale_y
        new_coords[2] = old_coords[2]
        self.UpdateCoords(new_coords)
        self.entryVariable.set(str(new_coords[0]) + "," + str(new_coords[1]) + "," + str(new_coords[2]))

# 0.0000160 coords, 100 pixels
        
    def UpdateCoords(self, coords):
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)
        
        #coords_text = self.entryVariable.get().split(",")
        request = "http://maps.google.com/maps/api/staticmap?center=" + str(coords[0]) + "," + str(coords[1]) + "&zoom=" + str(coords[2]) +"&size=500x500&format=gif&maptype=hybrid&sensor=false"
        urllib.urlretrieve(request, "caca.gif")
        image = Tkinter.PhotoImage(file="./caca.gif")
        self.image = image
        self.background.create_image(250, 250, image=self.image)

        
    def OnButtonClick(self):
        self.labelVariable.set( self.entryVariable.get()+" (You clicked the button)" )
        self.UpdateCoords(self.entryVariable.get().split(","))

    def OnPressEnter(self,event):
        self.labelVariable.set( self.entryVariable.get()+" (You pressed Enter)" )
        self.UpdateCoords(self.entryVariable.get().split(","))

if __name__ == "__main__":
    app = simpleapp_tk(None)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    app.title('my application')
    
    app.mainloop()
