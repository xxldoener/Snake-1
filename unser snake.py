from random import *
from tkinter import *
import tkinter as tk
import socket as so

# Allgemeine Spiel Infos
WELT_GRÖSSE = 500
ZELLEN = 8
SNAKETEMPO = 200
VERBINDEN = int(input("Mit Arduino verbinden? Ja(1) Nein(0)"))


#Wlan-Shield Verbindung
class Arduino(object):
    def __init__(self, window, host, port):

        self.window= window

        # Öffnet den Socket und verbindet mit dem Arduino
        self.socket= so.socket()
        self.socket.connect((host, port))
        self.socket.setblocking(False)

        self.rd_buff= bytes()

    def send_command(self, command):
        'Send a message to the Arduino'

        self.socket.send(command.encode('utf-8') + b'\n')

    def close(self):
        'Cleanly close the connection'

        self.socket.close()
#Ende der Wlan-Shield Verbindung

# Kreieren der Welt
class Welt:
    height = 20
    width = 20
    apfelposition = (1,1)

    def __init__(self, snake):

        self.setup_window()
        
#Abfragen des Hostnamen und des Ports, falls man mit Arduino verbinden will.
        if VERBINDEN == 1:
            host= input('Hostname: ')
            port= input('Port: ')
            self.arduino= Arduino(
                self.window,
                host, int(port)
            )
        self.setup_content(snake)

#Setup für die Wlan-Verbindung
    def setup_window(self):
        self.window= tk.Tk()
        self.window.title('Snake')
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

#Schließen der Wlan-Verbindung
    def on_close(self):
        if VERBINDEN == 1: 
            self.arduino.close()
        self.window.destroy()

#Setup für das Spiel
    def setup_content(self, snake):
        self.snake = snake
        self.width = ZELLEN
        self.height = ZELLEN
        self.neueApfelposition()    
  
#Zufällige Position des Apfels auf dem Spielfeld

    def neueApfelposition(self):
        self.apfelposition = (randint(1, self.width - 1), randint(1, self.height - 1))

        x = self.apfelposition[0]
        y = self.apfelposition[1]

        for part in self.snake.körper:
            if(x == part.x and y == part.y):
                self.neueApfelposition()
    

class SnakeKörperStück:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
# Zusammensezen der Schlange und festlegen des Startpunktes
class Snake:

    def __init__(self):
        startpunkt = (ZELLEN/2, ZELLEN/2)

        part1 = SnakeKörperStück(startpunkt[0], startpunkt[1])
        part2 = SnakeKörperStück(startpunkt[0], startpunkt[1]+1)

        self.körper = [part1,part2]

        self.richtung = "up"
        self.letzte_richtung = "up"

#Aufbau des GUI
class Snake_spiel(Frame):

    def __init__(self, welt, snake, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.welt = welt
        self.snake = snake

    def myLoop(self):
        if VERBINDEN == 0:
            self.zeichneWelt()
        self.Spiellogik()
        self.after(SNAKETEMPO, self.myLoop)
        
    def setCanvas(self, canvas):
        self.canv = canvas  

    def zeichneWelt(self):
        self.canv.delete("all")

        #Gitter zeichnen
        zellen_grösse = WELT_GRÖSSE / self.welt.width
        for x in range(self.welt.width):
            for y in range(self.welt.height):
                self.canv.create_rectangle(x * zellen_grösse, y * zellen_grösse, x * zellen_grösse + zellen_grösse,
                                           y * zellen_grösse + zellen_grösse)

        #Essen zeichen
        self.canv.create_oval(welt.apfelposition[0] * zellen_grösse + 3, welt.apfelposition[1] * zellen_grösse + 3,
                              welt.apfelposition[0] * zellen_grösse + zellen_grösse - 3,
                              welt.apfelposition[1] * zellen_grösse + zellen_grösse - 3, fill="darkred")

        #Schlange zeichnen
        for part in self.snake.körper:
            self.canv.create_rectangle(part.x * zellen_grösse, part.y * zellen_grösse, part.x * zellen_grösse + zellen_grösse,
                                       part.y * zellen_grösse + zellen_grösse, fill="green")

#Ablauf wenn eine Steuerungstaste bedient wird   
    def Spiellogik(self):
        if(self.snake.richtung == "up"):
            self.snake.letzte_richtung = "up"
            newPart = SnakeKörperStück(self.snake.körper[0].x, self.snake.körper[0].y - 1)
            self.snake.körper.insert(0, newPart)
        elif (self.snake.richtung == "down"):
            self.snake.letzte_richtung = "down"
            newPart = SnakeKörperStück(self.snake.körper[0].x, self.snake.körper[0].y + 1)
            self.snake.körper.insert(0, newPart)    
        elif (self.snake.richtung == "left"):
            self.snake.letzte_richtung = "left"
            newPart = SnakeKörperStück(self.snake.körper[0].x - 1, self.snake.körper[0].y)
            self.snake.körper.insert(0, newPart)
        elif (self.snake.richtung == "right"):
            self.snake.letzte_richtung = "right"
            newPart = SnakeKörperStück(self.snake.körper[0].x + 1, self.snake.körper[0].y)
            self.snake.körper.insert(0, newPart)



        xKopf = self.snake.körper[0].x
        yKopf = self.snake.körper[0].y

        xApfel = self.welt.apfelposition[0]
        yApfel = self.welt.apfelposition[1]
        
#Wenn der Kopf der Schlange den Apfel berührt, kommt ein neuer Apfel
        if(xKopf == xApfel and yKopf == yApfel):
            self.welt.neueApfelposition()
        else:
            self.snake.körper.pop()    

#Wenn der Kopf der Schlange die Spielfeldbegrenzung erreicht, startet das Spiel neu
        if(xKopf >= welt.width or xKopf < 0 or yKopf >= welt.height or yKopf < 0):
            self.snake = Snake()
            

        körperIter = iter(self.snake.körper)
        next(körperIter)
        for part in körperIter:
            if(xKopf == part.x and yKopf == part.y):
                self.snake = Snake()
                
# Zuweisung der Steuerung und senden an Arduino, falls gewünscht
    def hochTaste(self, event):
        if(self.snake.letzte_richtung != "down"):
            self.snake.richtung = "up"
            if VERBINDEN == 1:
                welt.arduino.send_command("up")
    def runterTaste(self, event):
        if(self.snake.letzte_richtung != "up"):
            self.snake.richtung = "down"
            if VERBINDEN == 1:
                welt.arduino.send_command("down")
    def rechtsTaste(self, event):
        if(self.snake.letzte_richtung != "left"):
            self.snake.richtung = "right"
            if VERBINDEN == 1:
                welt.arduino.send_command("right")
    def linksTaste(self, event):
        if(self.snake.letzte_richtung != "right"):
            self.snake.richtung = "left"
            if VERBINDEN == 1:
                welt.arduino.send_command("left")

        

            
snake = Snake()
welt = Welt(snake)

spiel = Snake_spiel(welt, snake)
spiel.master.title("Snake-Projekt")
spiel.master.minsize(WELT_GRÖSSE,WELT_GRÖSSE)
spiel.master.maxsize(WELT_GRÖSSE,WELT_GRÖSSE)

spiel.master.bind("<Down>", spiel.runterTaste)
spiel.master.bind("<Up>", spiel.hochTaste)
spiel.master.bind("<Left>", spiel.linksTaste)
spiel.master.bind("<Right>", spiel.rechtsTaste)

canv = Canvas(spiel.master, width=WELT_GRÖSSE, height=WELT_GRÖSSE)
canv.pack()

#Ablauf
spiel.setCanvas(canv)
spiel.zeichneWelt()
spiel.myLoop()
spiel.mainloop()
