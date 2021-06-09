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
        
    def iniciarConexion(self):
        grupoMulticast = '224.0.0.1'
        ip = '192.168.100.57'
        puerto = 15002

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        grupo = socket.inet_aton(grupoMulticast) + socket.inet_aton(ip)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, grupo)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(self.reinicio)
        self.sock.bind((ip, puerto))
        print('Conexion iniciada')
        
    def terminarConexion(self):
        self.sesion = False
        self.conexion.join()
        self.root.destroy()
    
    def berkeley(self, mensaje, servidor):
        try: 
            self.sock.sendto(mensaje.encode('utf-8'), servidor)
            print('Mensaje de actualizacion de hora enviado a ', servidor)
        except:
            print('Mensaje de actualizacion de hora no enviado')
    
    def sincronizar(self):
        dif1 = None
        dif2 = None
        hora_prev = self.hora.getTiempo()
        
        while self.sesion:
            servidores = (('192.168.100.57', 15000), ('192.168.100.57', 15001))
            
            for servidor in servidores:
                try:
                    hora_inicio = self.hora.getTiempo()
                    mensaje_enviado = 'Sincronizar, ' + hora_inicio
                    self.sock.sendto(mensaje_enviado.encode('utf-8'), servidor)
                    mensaje, direccion = self.sock.recvfrom(255)
                    
                    if servidor == ('192.168.100.57', 15000):
                        hora_servidor1 = mensaje.decode('utf-8')
                        recepcion_servidor = self.hora.getTiempo()
                        
                        ip_puerto = direccion[0] + ':' + str(direccion[1])
                        
                        print(ip_puerto)
                        print(hora_servidor1)
                        
                        total_seg_serv1 = self.getTiempoTotal(hora_servidor1)
                        print('total segundos serv1 ', total_seg_serv1)
                        total_seg_inicio = self.getTiempoTotal(hora_inicio)
                        print('total segundos inicio 1', total_seg_inicio)
                        total_seg_recepcion = self.getTiempoTotal(recepcion_servidor)
                        print('total segundos fin 1', total_seg_recepcion)
                        
                        dif1 = total_seg_serv1 - (total_seg_recepcion - total_seg_inicio)/2
                        print('dif1 ', dif1)
                        
                        datos_server = (hora_prev, hora_inicio)
                        self.cursor.execute("INSERT INTO horacentral VALUES (null, %s, %s)", datos_server)
                        database.commit()
                        print('Tabla horacentral actualizada  con servidor 1')
                        
                        # desface = self.getDesface(hora_inicio, hora_servidor1)
                        # datos_servidor1 = (ip_puerto, 'Servidor 1', desface)
                        
                        # self.cursor.execute("INSERT INTO equipos VALUES (null, %s, %s, %s)", datos_servidor1)
                        # database.commit()
                        # print('Tabla equipos actualizada con servidor 1')
                        
                        # consulta_id_equipo = (ip_puerto, str(desface))
                        # self.cursor.execute("SELECT id FROM equipos WHERE ip = %s AND latencia = %s", consulta_id_equipo)
                        # id_equipo = self.cursor.fetchone()
                        # print('id equipo: ', id_equipo[0])
                        
                        # self.cursor.execute("SELECT id FROM horacentral WHERE hprev = %s AND href = %s", datos_server)
                        # id_servidor = self.cursor.fetchone()
                        # print('id servidor: ', id_servidor[0])
                        
                        # tiempos_servidor1 = (id_servidor[0], id_equipo[0], hora_servidor1, hora_inicio)
                        
                        # self.cursor.execute("INSERT INTO horaequipos VALUES (null, %s, %s, %s, %s)", tiempos_servidor1)
                        # database.commit()
                        # print('Tabla horaequipos actualizada con servidor 1')
                        
                    else:
                        hora_servidor2 = mensaje.decode('utf-8')
                        recepcion_servidor = self.hora.getTiempo()
                        
                        ip_puerto = direccion[0] + ':' + str(direccion[1])
                        
                        print(ip_puerto)
                        print(hora_servidor2)

                        total_seg_serv2 = self.getTiempoTotal(hora_servidor2)
                        print('total segundos serv2 ', total_seg_serv2)
                        total_seg_inicio = self.getTiempoTotal(hora_inicio)
                        print('total segundos inicio 2', total_seg_inicio)
                        total_seg_recepcion = self.getTiempoTotal(recepcion_servidor)
                        print('total segundos fin 2', total_seg_recepcion)
                        
                        dif2 = total_seg_serv2 - (total_seg_recepcion - total_seg_inicio)/2
                        print('dif2 ', dif2)

                        datos_server = (hora_prev, hora_inicio)
                        self.cursor.execute("INSERT INTO horacentral VALUES (null, %s, %s)", datos_server)
                        database.commit()
                        print('Tabla horacentral actualizada  con servidor 2')  

                        # desface = self.getDesface(hora_inicio, hora_servidor2)
                        # datos_servidor1 = (ip_puerto, 'Servidor 2', desface)
                        
                        # self.cursor.execute("INSERT INTO equipos VALUES (null, %s, %s, %s)", datos_servidor1)
                        # database.commit()
                        # print('Tabla equipos actualizada con servidor 2')
                        
                        # consulta_id_equipo = (ip_puerto, str(desface))
                        # self.cursor.execute("SELECT id FROM equipos WHERE ip = %s AND latencia = %s", consulta_id_equipo)
                        # id_equipo = self.cursor.fetchone()
                        # print('id equipo: ', id_equipo[0])
                        
                        # self.cursor.execute("SELECT id FROM horacentral WHERE hprev = %s AND href = %s", datos_server)
                        # id_servidor = self.cursor.fetchone()
                        # print('id servidor: ', id_servidor[0])
                        
                        # tiempos_servidor2 = (id_servidor[0], id_equipo[0], hora_servidor2, hora_inicio)
                        # print(tiempos_servidor2)
                        
                        # self.cursor.execute("INSERT INTO horaequipos VALUES (null, %s, %s, %s, %s)", tiempos_servidor2)
                        # database.commit()
                        # print('Tabla horaequipos actualizada con servidor 2')
                        
                except:
                    print('No se pudo establecer conexion con ', servidor)
            
            if dif1 == None and dif2 == None:
                total_equipos = 1
            elif dif1 == None or dif2 == None: 
                total_equipos = 2
                
                if dif1 == None:
                    dif_prom = dif2/total_equipos
                    print('tiempo promedio ', dif_prom)
                    
                    hora_actual = self.getTiempoTotal(self.hora.getTiempo())
                    nueva_hora = hora_actual + dif_prom
                    
                    nueva_hora_str = self.segsHora(nueva_hora)
                    nueva_hora_l = nueva_hora_str.split('.')
                    nueva_hora_l1 = nueva_hora_l[0].split(':')
                    self.hora.setTiempo(int(nueva_hora_l1[0]), int(nueva_hora_l1[1]), int(nueva_hora_l1[2]))
                    print('hora para actualizar', nueva_hora_str)
                    
                    updt_dif = dif_prom - dif2
                    print('tiempo de actualizacion', updt_dif)
                    
                    mensaje_enviado = 'Sincronizar 2, ' + str(updt_dif)
                    
                    try: 
                        self.sock.sendto(mensaje_enviado.encode('utf-8'), servidores[1])
                        print('Mensaje de actualizacion de hora enviado')
                    except:
                        print('Mensaje de actualizacion de hora no enviado')
                else:
                    dif_prom = dif1/total_equipos
                    print('tiempo promedio ', dif_prom)
                    
                    hora_actual = self.getTiempoTotal(self.hora.getTiempo())
                    nueva_hora = hora_actual + dif_prom
                    
                    nueva_hora_str = self.segsHora(nueva_hora)
                    nueva_hora_l = nueva_hora_str.split('.')
                    nueva_hora_l1 = nueva_hora_l[0].split(':')
                    self.hora.setTiempo(int(nueva_hora_l1[0]), int(nueva_hora_l1[1]), int(nueva_hora_l1[2]))
                    print('hora para actualizar', nueva_hora_str)
                    
                    updt_dif = dif_prom - dif1
                    print('tiempo de actualizacion', updt_dif)
                    
                    mensaje_enviado = 'Sincronizar 2, ' + str(updt_dif)
                    
                    try: 
                        self.sock.sendto(mensaje_enviado.encode('utf-8'), servidores[1])
                        print('Mensaje de actualizacion de hora enviado')
                    except:
                        print('Mensaje de actualizacion de hora no enviado')
            else:
                total_equipos = 3
                dif_prom = (dif1+dif2)/total_equipos
                print('tiempo promedio ', dif_prom)
                
                hora_actual = self.getTiempoTotal(self.hora.getTiempo())
                nueva_hora = hora_actual + dif_prom
                
                nueva_hora_str = self.segsHora(nueva_hora)
                nueva_hora_l = nueva_hora_str.split('.')
                nueva_hora_l1 = nueva_hora_l[0].split(':')
                self.hora.setTiempo(int(nueva_hora_l1[0]), int(nueva_hora_l1[1]), int(nueva_hora_l1[2]))
                print('hora para actualizar', nueva_hora_str)
                
                updt_dif1 = dif_prom - dif1
                print('tiempo de actualizacion 1', updt_dif1)
                mensaje_enviado1 = 'Sincronizar 2, ' + str(updt_dif1)
                
                updt_dif2 = dif_prom - dif2
                print('tiempo de actualizacion 2', updt_dif2)
                mensaje_enviado2 = 'Sincronizar 2, ' + str(updt_dif2)
                
                sincro1 = threading.Thread(target=self.berkeley, args=(mensaje_enviado1, servidores[0]))
                sincro2 = threading.Thread(target=self.berkeley, args=(mensaje_enviado2, servidores[1]))
                sincro1.start()
                sincro2.start()
            
            print('Total de equipos ', total_equipos)

            print('---------------------------------------------------------')
            
            print('velocidad de sincronización = ', self.reinicio)
            
            if self.velocidad.get() != '':
                self.reinicio = int(self.velocidad.get())
                # print(self.reinicio)
            
            time.sleep(self.reinicio)

    def __init__(self):
        self.sesion = True
        self.reinicio = 5
        self.cursor = database.cursor(buffered=True)
        self.root = Tk()
        self.root.title('Servidor de Tiempo')
        self.root.geometry('200x150')
        self.root.resizable(0,0)
        self.frame = Frame()
        self.frame.pack()
        self.frame.config(bd='10')
        self.hora = relojes.reloj()
        self.lblReloj = Label(self.frame, text='00:00:00', font=('Open Sans', 20))
        self.lblInfo = Label(self.frame, text='Cambiar velocidad \nde sincronizacion', font=('Open Sans', 10)) 
        self.velocidad = Entry(self.frame)
        self.iniciarReloj()
        self.lblReloj.pack()
        self.lblInfo.pack()
        self.velocidad.pack()
        self.conexion = threading.Thread(target=self.iniciarConexion)
        self.conexion.start()
        self.sincronizar_servidores = threading.Thread(target=self.sincronizar)
        self.sincronizar_servidores.start()
        self.root.protocol('WM_DELETE_WINDOW', self.terminarConexion)
        self.root.mainloop()
        
servidor = Server()