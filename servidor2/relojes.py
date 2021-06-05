import random, time

class reloj:
    __segs = random.randint(0, 59)
    __mins = random.randint(0, 59)
    __hrs = random.randint(0, 23)
    __format = '%H:%M:%S'

    def __init__(self):
        self.__segs = random.randint(0, 59)
        self.mins = random.randint(0, 59)
        self.hrs = random.randint(0, 23)
    
    def getHoras(self):
        return self.__hrs
    
    def getMinutos(self):
        return self.__mins
    
    def getSegundos(self):
        return self.__segs

    def getTiempo(self):
        horaStr = f'{self.__hrs}:{self.__mins}:{self.__segs}'
        hora = time.strptime(horaStr, self.__format)
        return time.strftime(self.__format, hora)
    
    def setTiempo(self, hrs, mins, segs):
        self.__hrs = hrs
        self.__mins = mins
        self.__segs = segs
    
    def iniciarReloj(self):
        contador = 0
        segs = self.__segs
        mins = self.__mins
        hrs = self.__hrs
        
        while True:
            time.sleep(1)

            if segs == 59 and segs >= 0:
                if mins == 59 and mins >= 0:
                    if hrs == 23 and hrs >= 0:
                        self.setTiempo(0,0,0)
                        segs = 0
                        mins = 0
                        hrs = 0
                    else:
                        hrs += 1
                        self.setTiempo(hrs, 0, 0)
                        segs = 0
                        mins = 0
                else:
                    mins += 1
                    self.setTiempo(hrs, mins, 0)
                    segs = 0
            else:
                segs += 1
                self.setTiempo(hrs, mins, segs)        
            
            return self.getTiempo()
