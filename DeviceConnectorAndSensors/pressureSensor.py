import random

# ANCORA DA FARE

# this class represents a simulated pressure sensor

class pressureSensorClass():

    simulatedMeasures = [1,2,3,4,5,6,7,8,9,10]

    def getPressure(self, counter):
        return random.randint(0, 100)