import random

class temperatureSensorClass():

    def __init__(self):
        self.temperature = 36.5

    def getTemperature(self,ciclo):

        self.temperature = self.temperature + random.randint(-1, 1)/10

        if self.temperature < 36:
            self.temperature = 36

        if self.temperature > 39:
            self.temperature = 39
            
        self.temperature = float("{0:.2f}".format(self.temperature))

        return self.temperature

    