import random

# ANCORA DA FARE

# this class represents a simulated pressure sensor

class pressureSensorClass():

    # non so quale siano i range normali di pressione

    # calcolo pressione massima tramite FSM e sottraggo una quantità tipo rand(-35,-45) dalla max
    # max nominale 120
    # non deve superare 140
    # dalla 21a settimana è pericolosa anche bassa

    simulatedMeasures = [20 for i in range(1000)]

    def getPressure(self, counter):
        return (self.simulatedMeasures[counter] % len(self.simulatedMeasures)) + random.randint(-3, 3)