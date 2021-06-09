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
    
    def setHoras(self, n):
        self.__hrs = n
    
    def getMinutos(self):
        return self.__mins

    def setMinutos(self, n):
        self.__mins = n

    def getSegundos(self):
        return self.__segs

    def setSegundos(self, n):
        self.__segs = n

    def getTiempo(self):
        horaStr = f'{self.__hrs}:{self.__mins}:{self.__segs}'
        hora = time.strptime(horaStr, self.__format)
        return time.strftime(self.__format, hora)
    
    def setTiempo(self, hrs, mins, segs):
        self.__hrs = hrs
        self.__mins = mins
        self.__segs = segs

