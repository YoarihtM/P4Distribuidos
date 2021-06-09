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

database = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'tiempo'
)

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
        
    def restarTiempo(self, reloj1, reloj2):
        formato = '%H:%M:%S'
        
        hora1 = datetime.datetime.strptime(reloj1, formato)
        hora2 = datetime.datetime.strptime(reloj2, formato)
        
        print('hora 1: ', hora1)
        print('hora 2: ', hora2)
        hora_sustraida = hora1 - hora2
        
        hora_str = str(hora_sustraida)
        l = hora_str.split(', ')
        
        print(l)
        
        if len(l) > 1:
            print('hora sustraida', l[1])
            return l[1]
        else:
            print('hora sustraida', l[0])
            return l[0]
            
    def getDesface(self, reloj1, reloj2):
        formato = '%H:%M:%S'
        
        hora1 = datetime.datetime.strptime(reloj1, formato)
        hora2 = datetime.datetime.strptime(reloj2, formato)
        
        print('hora 1: ', hora1)
        print('hora 2: ', hora2)
        
        if hora1 > hora2:
            hora_sustraida = hora1 - hora2
        elif hora2 > hora1:
            hora_sustraida = hora2 - hora1
        
        return str(hora_sustraida)
        
        
    def iniciarConexion(self):
        grupoMulticast = '224.0.0.1'
        ip = '192.168.100.57'
        puerto = 15002

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        grupo = socket.inet_aton(grupoMulticast) + socket.inet_aton(ip)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, grupo)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(2)
        self.sock.bind((ip, puerto))
        print('Conexion iniciada')
        
    def terminarConexion(self):
        self.sesion = False
        self.conexion.join()
        self.root.destroy()
        
    def sincronizar(self):
        datos_server = (self.hora.getTiempo(), self.hora.getTiempo())
        self.cursor.execute("INSERT INTO horacentral VALUES (null, %s, %s)", datos_server)
        database.commit()
        print('Tiempo local registrado!')
        servidores = (('192.168.100.57', 15000), ('192.168.100.57', 15001))
        
        for servidor in servidores:
            try:
                hora_inicio = self.hora.getTiempo()
                self.sock.sendto('Sincronizar'.encode('utf-8'), servidor)
                mensaje, direccion = self.sock.recvfrom(255)
                
                if servidor == ('192.168.100.57', 15000):
                    hora_servidor1 = mensaje.decode('utf-8')
                    desface = self.getDesface(hora_inicio, hora_servidor1)
                    datos_servidor1 = (direccion[0], 'Servidor 1', desface)
                    self.cursor.execute("INSERT INTO equipos VALUES (null, %s, %s, %s)", datos_servidor1)
                    database.commit()
                else:
                    hora_servidor2 = mensaje.decode('utf-8')
            except:
                print('No se pudo establecer conexion con ', servidor)
        
        try:
            print('Hora de inicio ', hora_inicio)
            print('Hora s1: ', hora_servidor1)
            print('Hora s2: ', hora_servidor2)
        except:
            print('Tiempo no recibido por falta de conexion con algun servidor')
            
        print('---------------------------------------------------------')

    def __init__(self):
        self.cursor = database.cursor()
        self.root = Tk()
        self.root.title('Servidor de Tiempo')
        self.root.geometry('200x100')
        self.root.resizable(0,0)
        self.frame = Frame()
        self.frame.pack()
        self.frame.config(bd='10')
        self.hora = relojes.reloj()
        self.lblReloj = Label(self.frame, text='00:00:00', font=('Open Sans', 20))
        self.btnSincronizar = Button(self.frame, text='Sincronizar', command=self.sincronizar)
        self.iniciarReloj()
        self.lblReloj.pack()
        self.btnSincronizar.pack()
        self.conexion = threading.Thread(target=self.iniciarConexion)
        self.conexion.start()
        self.root.protocol('WM_DELETE_WINDOW', self.terminarConexion)
        self.root.mainloop()
        
servidor = Server()