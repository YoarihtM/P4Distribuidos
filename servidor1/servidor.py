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
    database = 'libros'
)

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
    
    def sumarTiempo(self, reloj1, reloj2):
        formato = '%H:%M:%S'
        
        hora1 = datetime.datetime.strptime(reloj1, formato)
        hora2 = datetime.datetime.strptime(reloj2, formato)

        hora_sumada = hora1 + hora2
        
        hora_str = str(hora_sumada)
        l = hora_str.split(', ')
        
        if len(l) > 1:
            return l[1]
        else:
            return l[0]

    def restarTiempo(self, reloj1, reloj2):
        formato = '%H:%M:%S'
        
        hora1 = datetime.datetime.strptime(reloj1, formato)
        hora2 = datetime.datetime.strptime(reloj2, formato)

        hora_sustraida = hora1 - hora2
        
        hora_str = str(hora_sustraida)
        l = hora_str.split(', ')
        
        if len(l) > 1:
            return l[1]
        else:
            return l[0]
            
    def getDesface(self, reloj1, reloj2):
        formato = '%H:%M:%S'
        
        hora1 = datetime.datetime.strptime(reloj1, formato)
        hora2 = datetime.datetime.strptime(reloj2, formato)
        
        if hora1 > hora2:
            hora_sustraida = hora1 - hora2
        elif hora2 > hora1:
            hora_sustraida = hora2 - hora1
        
        return str(hora_sustraida)
    
    def getTiempoTotal(self, reloj):
        formato = '%H:%M:%S'
        tiempo = time.strptime(reloj, formato)
        
        return datetime.timedelta(hours=tiempo.tm_hour, minutes=tiempo.tm_min, seconds=tiempo.tm_sec).total_seconds()
    
    def segsHora(self, segundos):
        formato = '%H:%M:%S'
        hora = datetime.timedelta(seconds=segundos)
        hora_str = str(hora)
        
        # print('Conversion de segundos a hora', hora1_str)
        
        return hora_str
    
    def iniciarSesion(self):
        grupoMulticast = '224.0.0.1'
        ip = '192.168.100.57'
        puerto = 15000

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        grupo = socket.inet_aton(grupoMulticast) + socket.inet_aton(ip)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, grupo)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(5)
        sock.bind((ip, puerto))
        print('Conexion iniciada, esperando peticiones...')

        self.enviados = []
        
        while self.sesion:
            try:
                mensaje, direccion = sock.recvfrom(255)
                print('Mensaje: ' + str(mensaje.decode('utf-8')) + ' Desde:')
                print(direccion[0])
                
                datos = mensaje.decode('utf-8')
                
                l_mensaje = datos.split(', ')
                
                if len(l_mensaje) > 1:
                    if l_mensaje[0].lower() == 'sincronizar':
                        l_nueva_hora = l_mensaje[1].split(':')
                        
                        updt_hora = int(l_nueva_hora[0])
                        updt_min = int(l_nueva_hora[1]) + random.randint(1,3)
                        updt_seg = int(l_nueva_hora[2]) 
                        
                        self.hora.setTiempo(updt_hora, updt_min, updt_seg)
                        
                        diferencia_tiempo = self.restarTiempo(self.hora.getTiempo(), l_mensaje[1])
                        # print('Diferencia en tiempo ', l_mensaje[1])
                        
                        time.sleep(random.randint(2,5))
                        sock.sendto(diferencia_tiempo.encode('utf-8'), direccion)
                        print('Hora sincronizada con diferencia en tiempo enviada')
                        
                    elif l_mensaje[0].lower() == 'sincronizar 2':
                        diferencia_segundos = l_mensaje[1]
                        
                        print('segundos recibidos ', diferencia_segundos)
                        hora_actual = self.getTiempoTotal(self.hora.getTiempo())
                        updt_tiempo = hora_actual + float(diferencia_segundos)
                        updt_tiempo_str = self.segsHora(updt_tiempo)
                        
                        nueva_hora_l = updt_tiempo_str.split('.')
                        nueva_hora_l1 = nueva_hora_l[0].split(':')
                        self.hora.setTiempo(int(nueva_hora_l1[0]), int(nueva_hora_l1[1]), int(nueva_hora_l1[2]))
                        print('Tiempo sincronizado')
                else:
                    if l_mensaje[0].lower() == 'iniciar conexion':
                        print('Peticion de conexion recibida por ', direccion)
                        sock.sendto('aceptado'.encode('utf-8'), direccion)
                        print('Solicitud aceptada')
                        
                    else:
                        if len(set(self.listaISBN).intersection(self.enviados)) < 5:
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
        self.root.title('Practica 4 - Servidor 1')
        self.root.geometry('400x400')
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

        self.hora = relojes.reloj()
        self.lblReloj = Label(self.frame, text='00:00:00', font=('Open Sans', 20))
        self.iniciarReloj()
        self.lblReloj.pack()
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