import random

# ANCORA DA FARE

# this class represents a simulated pressure sensor

class pressureSensorClass():

    simulatedMeasures = [20 for i in range(1000)]

    def getPressure(self, counter):
        return self.simulatedMeasures[counter] + random.randint(-3, 3)