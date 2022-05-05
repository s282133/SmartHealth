import random

# ANCORA DA FARE

# this class represents a simulated pressure sensor

class pressureSensorClass():

    # non so quale siano i range normali di pressione

    simulatedMeasures = [20 for i in range(1000)]

    def getPressure(self, counter):
        return (self.simulatedMeasures[counter] % len(self.simulatedMeasures)) + random.randint(-3, 3)