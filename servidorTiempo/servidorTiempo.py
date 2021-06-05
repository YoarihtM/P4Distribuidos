import mysql.connector
from tkinter import *
from PIL import Image
import relojes
import os
import random
import socket
import threading
import datetime
import time

class Server():
    def iniciarReloj(self):
        segs = self.hora.getSegundos()
        mins = self.hora.getMinutos()
        hrs = self.hora.getHoras()
        
        if segs == 59 and segs >= 0:
            if mins == 59 and mins >= 0:
                if hrs == 23 and hrs >= 0:
                    self.hora.setTiempo(0,0,0)
                    segs = 0
                    mins = 0
                    hrs = 0
                else:
                    hrs += 1
                    self.hora.setTiempo(hrs, 0, 0)
                    segs = 0
                    mins = 0
            else:
                mins += 1
                self.hora.setTiempo(hrs, mins, 0)
                segs = 0
        else:
            segs += 1
            self.hora.setTiempo(hrs, mins, segs)
        
        self.lblReloj.config(text=self.hora.getTiempo())
        self.lblReloj.after(1000, self.iniciarReloj)

    def __init__(self):
        self.root = Tk()
        self.root.title('Practica 3 - Servidor')
        self.root.geometry('200x100')
        self.root.resizable(0,0)
        self.frame = Frame()
        self.frame.pack()
        self.frame.config(bd='10')
        self.hora = relojes.reloj()
        self.lblReloj = Label(self.frame, text='00:00:00', font=('Open Sans', 20))
        self.iniciarReloj()
        self.lblReloj.pack()
        self.root.mainloop()
        
servidor = Server()