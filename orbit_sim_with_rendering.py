from tkinter import *
import time
import random
import math
from decimal import *
import multiprocessing

#Made by Crisian Bicheru 2018
#Uses Newtonian Physics
#Render Version
#This Version Sacrifices Speed For Reducing Energy Drift
#Object Orbits Are Rendered And Played Back Once Objects Complete Their Full Orbit
###################################################################################

WIDTH = 1300              #resolution, 
HEIGHT = 1000

dT = 0.0003               #delay between frames, <0.0005 is optimal since this is a render.
                          #changing this in-sim results in interesting behaviour when dT is high
blackHoleMass = 10000000  #default mass of black hole
gravConstant = 1          #default gravitational constant
ox = 0                    #default spawn offset x
oy = 0                    #default spawn offset y
spawnSpeedX = 0           #default spawn speed (x direction)
spawnSpeedY = 0           #default spawn speed (y direction)
playbackRate = 1          #default playback rate (must be an int currently {otherwise you have to approximate})
triggerDistance = 1       #you can set this lower if you also set dT lower (you have to raise it if you raise dT), if you set this too low the code may not detect an elapsed orbit
decimalPrecision = 100    #number of significant figures used in calculations
enableMultiprocessing = 1 #self-explanatory, 1=on, 0=off


unrenderedSpheres = 0
lines = []
toggle = 0
timeToggle = 0
frozen = []
getcontext().prec = decimalPrecision


def asin(x):
    global decimalPrecision
    p = 0
    for n in range(decimalPrecision):
        try:
            p += Decimal(1)/Decimal(2**(2*n))*Decimal(math.factorial(2*n))/(Decimal(math.factorial(n))**Decimal(2))*Decimal(x**(2*n+1))/Decimal(2*n+1)
        except:
            break
        
    return p


def cos(x):
    global decimalPrecision
    p = 0
    for n in range(decimalPrecision):
        try:
            p += Decimal(((-1)**n)*(x**(2*n)))/(Decimal(math.factorial(2*n)))
        except:
            break
    return p

class Ball:
    def __init__(self):
        global unrenderedSpheres
        self.size = random.randrange(20, 30)
        self.shape = canvas.create_oval(ox, oy, self.size+ox, self.size+oy, fill="red")
        self.speedx = spawnSpeedX
        self.speedy = spawnSpeedY
        self.t = 0
        self.delayt = 0
        self.dT = dT
        
        self.startX = ox+self.size/2
        self.startY = oy+self.size/2
        self.actX = Decimal(self.startX)
        self.actY = Decimal(self.startY)
        
        self.frame = -1
        self.frames = 0
        self.boundUnlock = 0
        self.renderComplete = 0
        self.renderedFrames = {}
        unrenderedSpheres += 1
        menu().update()

    def update(self):
        if self.dT == 0:
            pass
        else:
            global dT, planets, unrenderedSpheres, triggerDistance
            if self.renderComplete == 0:
                self.t += self.dT
                centerX = self.actX
                centerY = self.actY
                if centerY - Decimal(HEIGHT)/Decimal(2) > 0:
                    gravMagnitude = Decimal(Decimal(gravConstant)*Decimal(blackHoleMass))/Decimal((Decimal(centerX)-Decimal(WIDTH)/Decimal(2))**Decimal(2)+Decimal(Decimal(centerY)-Decimal(HEIGHT)/Decimal(2))**Decimal(2))
                    aByc = Decimal((Decimal(centerX)-Decimal(WIDTH)/Decimal(2)))/Decimal(Decimal((Decimal(centerX)-Decimal(WIDTH)/Decimal(2))**Decimal(2)+(Decimal(centerY)-Decimal(HEIGHT)/Decimal(2))**Decimal(2))**Decimal(0.5))
                    gravXacceleration = -(gravMagnitude*(aByc))
                    gravYacceleration = -(gravMagnitude*cos(asin(aByc)))
                        
                else:
                    gravMagnitude = Decimal(Decimal(gravConstant)*Decimal(blackHoleMass))/Decimal((Decimal(centerX)-Decimal(WIDTH)/Decimal(2))**Decimal(2)+Decimal(Decimal(centerY)-Decimal(HEIGHT)/Decimal(2))**Decimal(2))
                    aByc = Decimal((Decimal(centerX)-Decimal(WIDTH)/Decimal(2)))/Decimal(Decimal((Decimal(centerX)-Decimal(WIDTH)/Decimal(2))**Decimal(2)+(Decimal(centerY)-Decimal(HEIGHT)/Decimal(2))**Decimal(2))**Decimal(0.5))
                    gravXacceleration = -(gravMagnitude*(aByc))
                    gravYacceleration = (gravMagnitude*cos(asin(aByc)))

                #black hole collision
                if abs(centerX-Decimal(WIDTH)/Decimal(2)) < (15+self.size/2) and abs(centerY-Decimal(HEIGHT)/Decimal(2)) < (15+self.size/2):
                    canvas.delete(self.shape)
                    planets.remove(self)
                    unrenderedSpheres += -1
                    menu().update()
                
                dy = (Decimal(self.speedy)*Decimal(self.dT))+Decimal(0.5)*gravYacceleration*Decimal(self.dT)**2
                dx = (Decimal(self.speedx)*Decimal(self.dT))+Decimal(0.5)*gravXacceleration*Decimal(self.dT)**2
                self.speedy = Decimal(self.speedy)+gravYacceleration*Decimal(self.dT)
                self.speedx = Decimal(self.speedx)+gravXacceleration*Decimal(self.dT)
                
                canvas.move(self.shape, dx, dy)
                
                
                self.renderedFrames[round(self.t/self.dT)-1] = [centerY, centerX]

                if self.boundUnlock == 0:
                    if abs(centerX-Decimal(self.startX)) > 10:
                        self.boundUnlock = 1
                
                #recording trigger
                if abs(centerX-Decimal(self.startX)) < triggerDistance and abs(centerY-Decimal(self.startY)) < triggerDistance and self.boundUnlock == 1:
                    self.renderComplete = 1
                    unrenderedSpheres += -1
                    self.frames = len(self.renderedFrames)
                    canvas.itemconfig(self.shape, fill="green")
                    menu().update()

                    

                self.actX = centerX + dx
                self.actY = centerY + dy
            else:
                global playbackRate
                self.frame += playbackRate
                self.frame = self.frame % self.frames
                centerX = self.actX
                centerY = self.actY
                y = self.renderedFrames[self.frame][0]
                x = self.renderedFrames[self.frame][1]
                dy = y-self.actY
                dx = x-self.actX
                canvas.move(self.shape, dx, dy)
                self.actX = centerX + dx
                self.actY = centerY + dy
        

class blackHole:
    def __init__(self):
        self.size = 30
        self.shape = canvas.create_oval((WIDTH-self.size)/2, (HEIGHT-self.size)/2, (WIDTH+self.size)/2, (HEIGHT+self.size)/2, fill="black")
    def update(self):
        pass


class menu:
    def __init__(self):
        global gravConstant, blackHoleMass, dT, playbackRate
        self.button = Button(tk, text="Spawn New", command=self.createNewBall, state="normal")
        self.button.place(x=70, y=10)
        self.label = Label(tk, text = "x-coordinate:")
        self.label.place(x=10, y=40)
        self.label = Label(tk, text = "y-coordinate:")
        self.label.place(x=10, y=65)
        self.label = Label(tk, text = "x-velocity:")
        self.label.place(x=10, y=90)
        self.label = Label(tk, text = "y-velocity:")
        self.label.place(x=10, y=115)
        self.label = Label(tk, text = "grav. constant:")
        self.label.place(x=10, y=170)
        self.label = Label(tk, text = "black hole mass:")
        self.label.place(x=10, y=195)
        self.label = Label(tk, text = "delta-time:")
        self.label.place(x=10, y=220)
        self.label = Label(tk, text = "playback rate:")
        self.label.place(x=10, y=395)
        self.label2 = Label(tk, text = str(playbackRate)+"x")
        self.label2.place(x=110, y=395)
        self.entry = Entry(tk)
        self.entry.insert(0, "0")
        self.entry.place(x=110, y=40)
        self.entry2 = Entry(tk)
        self.entry2.insert(0, "0")
        self.entry2.place(x=110, y=65)
        self.entry3 = Entry(tk)
        self.entry3.insert(0, "0")
        self.entry3.place(x=110, y=90)
        self.entry4 = Entry(tk)
        self.entry4.insert(0, "0")
        self.entry4.place(x=110, y=115)
        self.button2 = Button(tk, text="Update:", command=self.updateVals, state="disabled")
        self.button2.place(x=80, y=140)
        self.entry5 = Entry(tk)
        self.entry5.insert(0, gravConstant)
        self.entry5.place(x=110, y=170)
        self.entry6 = Entry(tk)
        self.entry6.insert(0, blackHoleMass)
        self.entry6.place(x=110, y=195)
        self.entry7 = Entry(tk)
        self.entry7.insert(0, dT)
        self.entry7.place(x=110, y=220)
        self.button3 = Button(tk, text="Show/Hide Grid", command=self.toggleGrid)
        self.button3.place(x=60, y=245)
        self.button4 = Button(tk, text="Clear Planets and Allow Spawning", command=self.planetDestroy)
        self.button4.place(x=5, y=275)
        self.button5 = Button(tk, text="Freeze Time", command=self.freezeTime, state="normal")
        self.button5.place(x=65, y=305)
        self.button6 = Button(tk, text="Increase Playback Speed", command=self.increasep, state="normal")
        self.button6.place(x=35, y=335)
        self.button7 = Button(tk, text="Decrease Playback Speed", command=self.decreasep, state="normal")
        self.button7.place(x=35, y=365)

    def increasep(self):
        global playbackRate, unrenderedSpheres
        self.button.config(state="disabled")
        self.button5.config(state="disabled")
        playbackRate += 1
        self.label2.config(text = str(playbackRate)+"x")

    def decreasep(self):
        global playbackRate
        self.button.config(state="disabled")
        self.button5.config(state="disabled")
        playbackRate += -1          
        self.label2.config(text = str(playbackRate)+"x")
    
    def freezeTime(self):
        global timeToggle, frozen, planets
        if timeToggle == 0:
            frozen = planets
            planets = []
            self.button.config(state="disabled")
            self.button5.config(text="Unfreeze Time")
            timeToggle = 1
        else:
            planets = frozen
            frozen = []
            self.button.config(state="normal")
            self.button5.config(text="Freeze Time")
            timeToggle = 0

    def planetDestroy(self):
        global planets, frozen, timeToggle, unrenderedSpheres
        if timeToggle == 0:
            for planet in planets:
                canvas.delete(planet.shape)
                planets = []
        else:
            for planet in frozen:
                canvas.delete(planet.shape)
                frozen = []
        unrenderedSpheres = 0
        self.button.config(state="normal")
        self.button5.config(state="normal")
        
        
    
    def createNewBall(self):
        global ox, oy, spawnSpeedX, spawnSpeedY
        ox = float(self.entry.get())*50
        oy = float(self.entry2.get())*50
        spawnSpeedX = float(self.entry3.get())*50
        spawnSpeedY = float(self.entry4.get())*50
        planets.append(Ball())

    def updateVals(self):
        pass

    def toggleGrid(self):
        global lines, toggle
        if toggle == 0:
            numRows = int(round(HEIGHT/50))
            numColumns = int(round(WIDTH/50))
            for x in range(1, numColumns):
                vertLine = canvas.create_line(50*x, 0, 50*x, HEIGHT)
                lines.append(vertLine)
            for y in range(1, numRows):
                horiLine = canvas.create_line(0, 50*y, WIDTH, 50*y)
                lines.append(horiLine)
            toggle = 1
        else:
            for line in lines:
                canvas.delete(line)
            toggle = 0
    
    def update(self):
        global playbackRate, unrenderedSpheres
        if unrenderedSpheres != 0:
            self.button6.config(state="disabled")
            self.button7.config(state="disabled")
        else:
            self.button6.config(state="normal")
            self.button7.config(state="normal")
            self.button.config(state="normal")

def update(objecT):
    objecT.update()

if __name__ == "__main__":
    
    tk = Tk()
    back = Canvas(tk, width=WIDTH+255, height=HEIGHT+20)
    back.pack()
    simFrame = Frame(tk)
    canvas = Canvas(simFrame, width=WIDTH, height=HEIGHT, bg="grey")
    tk.title("orbital motion")
    simFrame.place(x=245, y=10)
    canvas.pack()
    planets = []
    others = []
    others.append(blackHole())
    others.append(menu())
    blackHole().update()

    if enableMultiprocessing == 0:
        while True:
            for objecT in planets:
                objecT.update()
            tk.update()
            if unrenderedSpheres == 0:
                time.sleep(dT)

    elif enableMultiprocessing == 1:
        while True:
            n = len(planets)
            if n == 1 or unrenderedSpheres == 0:
                for objecT in planets:
                    objecT.update()
                tk.update()
                if unrenderedSpheres == 0:
                    time.sleep(dT)
            elif n < multiprocessing.cpu_count():
                q = multiprocessing.Pool(processes = len(planets))
                async_result = q.map_async(update, planets)
                q.close()
                q.join()
                tk.update()
                print("done")
    else:
        print("ERROR: check mp setting.")
