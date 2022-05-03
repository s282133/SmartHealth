import random

# ANCORA DA FARE

# this class represents a simulated pressure sensor

class glycemiaSensorClass():

    simulatedMeasures = [80 for i in range(1000)]

    def getGlycemia(self, counter):
        return self.simulatedMeasures[counter] + random.randint(-3, 3)