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
    database = 'libros_copia'
)

class GUI():
    def iniciarSesion(self):
        grupoMulticast = '224.0.0.1'
        ip = '192.168.100.57'
        puerto = 15001

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        grupo = socket.inet_aton(grupoMulticast) + socket.inet_aton(ip)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, grupo)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        sock.bind((ip, puerto))
        print('Conexion iniciada, esperando peticiones...')

        self.enviados = []
        
        while self.sesion:
            try:
                if len(set(self.listaISBN).intersection(self.enviados)) < 5:
                    mensaje, direccion = sock.recvfrom(255)
                    print('Hora: ' + str(mensaje.decode('utf-8')) + ' Desde:')
                    print(direccion[0])
                    self.eleccion = random.choice(self.listaISBN)
                    print(self.eleccion)

                    dato_usuario = (direccion[0], 'Usuario:'+direccion[0])
                    self.cursor.execute("INSERT INTO usuario VALUES(null, %s, %s)", dato_usuario)
                    database.commit()

                    while self.eleccion in self.enviados:
                        self.eleccion = random.choice(self.listaISBN)
                    
                    self.enviados.append(self.eleccion)

                    dato_pedido = (str(datetime.date.today()), str(mensaje.decode('utf-8')), str(mensaje.decode('utf-8')))

                    self.cursor.execute("INSERT INTO pedido VALUES(null, %s, %s, %s)", dato_pedido)
                    database.commit()

                    self.cursor.execute("SELECT id FROM pedido WHERE fecha = %s AND hora_inicio = %s AND hora_fin = %s", dato_pedido)
                    idPedido = self.cursor.fetchone()
                    
                    dato_sesion = (idPedido[0], self.eleccion[0])
                    print(dato_sesion)
                    self.cursor.execute("INSERT INTO sesion VALUES(null, %s, %s)", dato_sesion)
                    database.commit()

                    self.cursor.execute("SELECT id FROM usuario WHERE ip = %s AND nombre = %s", dato_usuario)
                    idUsuarioSesion = self.cursor.fetchall()
                    #print(idUsuarioSesion[len(idUsuarioSesion)-1][0])

                    dato_usuario_sesion = (idUsuarioSesion[len(idUsuarioSesion)-1][0], idPedido[0], str(mensaje.decode('utf-8')))
                    self.cursor.execute("INSERT INTO usuario_sesion VALUES (null, %s, %s, %s)", dato_usuario_sesion)
                    database.commit()

                    self.cursor.execute("""
                    SELECT * FROM libro WHERE ISBN=
                    """ + self.eleccion[0])

                    self.resultado = self.cursor.fetchall()
                    self.img = PhotoImage(file = self.rutaImg + '/img/' + self.resultado[0][5])
                    self.imgRed = self.img.subsample(10,10)
                    self.lblImg.config(image=self.imgRed)
                    self.lblImg.pack()
                    self.lblNombreLibro.config(text=self.resultado[0][1])
                    self.lblNombreLibro.pack(fill=BOTH)
                    self.frame.update()
                    sock.sendto(str([0, self.resultado[0][:5]]).encode('utf-8'), direccion)
                else:
                    mensaje, direccion = sock.recvfrom(255)
                    self.lblImg.pack_forget()
                    self.lblNombreLibro.config(text=direccion[0] + ' dice ' + str(mensaje.decode('utf-8')))
                    self.frame.update()
                    sock.sendto(str([1, 'Todos los libros han sido repartidos ¿desea reiniciar la sesion?']).encode('utf-8'), direccion)
            except:
                continue
        
    def reiniciar(self):
        self.enviados = []
    
    def terminar(self):
        self.sesion = False
        self.conexion.join()
        self.root.destroy()

    def __init__(self):
        self.sesion = True
        self.cursor = database.cursor()
        self.root = Tk()
        self.root.title('Practica 3 - Servidor')
        self.root.geometry('400x350')
        self.root.resizable(0,0)
        self.frame = Frame()
        self.frame.pack()
        self.frame.config(bd='10')
        self.rutaImg = os.path.join(os.path.dirname(__file__))

        self.cursor.execute("""
        SELECT ISBN FROM libro;
        """)
        self.listaISBN = self.cursor.fetchall()
        print(self.listaISBN)

        self.btnReiniciar = Button(self.frame, text='Reiniciar', command=self.reiniciar)
        self.btnReiniciar.pack()
        self.lblImg = Label(self.frame, text='')
        self.lblImg.pack()
        self.lblNombreLibro = Label(self.frame)
        self.conexion = threading.Thread(target=self.iniciarSesion)
        self.conexion.start()
        self.root.protocol('WM_DELETE_WINDOW', self.terminar)
        self.root.mainloop()

gui = GUI()