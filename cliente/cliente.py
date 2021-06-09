from tkinter import *
import relojes
import socket
import struct

class GUI():
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

    def reinicio(self):
        grupoMulticast = '224.0.0.1'
        puertos = [15000, 15001]
        
        for puerto in puertos:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                ttl = struct.pack('b', 1)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
                sock.sendto(str('Reiniciar').encode('utf-8'), (grupoMulticast, puerto))
                self.btnReiniciar.pack_forget()
                self.frame.update()
                sock.close()
            except socket.timeout:
                print('No hubo respuesta')

    def conectar(self, direcciones):
        conectado = True
        
        while conectado:
            for direccion in direcciones:
                try:
                    self.sock.sendto('iniciar conexion'.encode('utf-8'), direccion)
                    print('Peticion enviada a ', direccion)
                    mensaje, servidor = self.sock.recvfrom(255)
                    if servidor == direccion:
                        datos = mensaje.decode('utf-8')
                        if datos.lower() == 'aceptado':
                            conectado = False
                            print('Peticion aceptada por ', direccion)
                            return servidor
                except:
                    conectado = False
                    print('No se pudo establecer conexion con ', direccion)
    
    def realizarPeticion(self):        
        direcciones = (('192.168.100.57', 15000), ('192.168.100.57', 15001))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)
        ttl = struct.pack('b', 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        direccion = self.conectar(direcciones)
        
        if direccion == None:
            print('Conexion no establecida, intente de nuevo')
        else:
            try:
                self.sock.sendto(self.hora.getTiempo().encode('utf-8'), direccion)
                while True:
                    try:
                        datos, servidor = self.sock.recvfrom(255)
                        print('Peticion aceptada por ', servidor)
                        print('-----------------------------------------')
                    except socket.timeout:
                        break
                    else:
                        datosLibros = datos.decode('utf-8')
                        l = datosLibros.split('[')
                        l1 = l[1].split(']')
                        l2 = l1[0].split(',')
                        
                        if l2[0] == '0':
                            l3 = l2[1].split('(')
                            l4 = l2[5].split(')')

                            self.lblISBN.config(text='ISBN: ' + l3[1])
                            self.lblNombre.config(text='Nombre: ' + l2[2])
                            self.lblAutor.config(text='Autor:' + l2[3])
                            self.lblEditorial.config(text='Editorial: ' + l2[4])
                            self.lblPrecio.config(text='Precio: $' + l4[0])
                            self.frame.update()
                            
                        else:
                            self.lblISBN.config(text='')
                            self.lblNombre.config(text='El servidor dice: ')
                            self.lblAutor.config(text=l2[1])
                            self.lblEditorial.config(text='')
                            self.lblPrecio.config(text='')
                            self.btnReiniciar = Button(self.frame, text='Pedir Reinicio de Sesion', command=self.reinicio)
                            self.btnReiniciar.pack()
                            self.frame.update()
            except socket.timeout:
                print('No hubo respuesta')
                
        self.sock.close()
    
    def __init__(self):
        self.root = Tk()
        self.root.title('Practica 4 - Cliente')
        self.root.geometry('400x300')
        self.root.resizable(0,0)
        self.frame = Frame()
        self.frame.pack()
        self.frame.config(bd='10')
        self.hora = relojes.reloj()
        self.lblReloj = Label(self.frame, text='00:00:00', font=('Open Sans', 20))
        self.iniciarReloj()
        self.lblReloj.pack()
        self.lblISBN = Label(self.frame, text='')
        self.lblISBN.pack()
        self.lblNombre = Label(self.frame, text='')
        self.lblNombre.pack()
        self.lblAutor = Label(self.frame, text='')
        self.lblAutor.pack()
        self.lblEditorial = Label(self.frame, text='')
        self.lblEditorial.pack()
        self.lblPrecio = Label(self.frame, text='')
        self.lblPrecio.pack()
        self.btnPedir = Button(self.frame, text='Pedir', command = self.realizarPeticion)
        self.btnPedir.pack()
        self.root.mainloop()

gui = GUI()