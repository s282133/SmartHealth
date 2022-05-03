from MyMQTT import *
import time
import json
import string
from heartrateSensor import heartrateSensorClass
from pressureSensor import pressureSensorClass

# periodo in minuti
PERIODO_HR = 5
PERIODO_PRESSURE = 15

# DA FARE: mettere funzioni publisher MQTT ma non so se vanno mantenute quelle subscriber

class rpi():

    # MQTT FUNCTIONS

    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    
    def stop(self):
        self.client.stop()
    
    def notify(self, topic, msg):   
        d = json.loads(msg)
        bn = d["bn"]
        sensorName = bn.split("/")[3]           # "bn": "http://example.org/sensor1/"  -> "sensor1"
        e = d["e"]
        measureType = e[0]["n"]
        unit = e[0]["u"]
        timestamp = e[0]["t"]
        value = e[0]["v"]
        print(f"{sensorName} measured a {measureType} of {value} {unit} at time {timestamp}.\n")


    def initSensors(self):
        self.heartrateSensor = heartrateSensorClass()
        self.pressureSensor = pressureSensorClass()

    # HEARTRATE

    def getHRmeasure(self, counter):
        newMeasureHR = self.heartrateSensor.getHR(counter)
        return newMeasureHR

    def publishHR(self):
        pass

    # PRESSURE

    def getPressuremeasure(self, counter):
        newMeasurePressure = self.pressureSensor.getPressure(counter)
        return newMeasurePressure

    def publishPressure(self):
        pass

    # altri sensori possono essere aggiunti qua



if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    MQTTpubsub = rpi("rpi", "P4IoT/SmartHealth/#", broker, port)
    MQTTpubsub.start()    

    MQTTpubsub.initSensors()

    counter = 0
    while True:
        if counter % PERIODO_HR == 0:
            newMeasureHR = int(MQTTpubsub.getHRmeasure(counter))
            print(f"HEARTRATE measure: {newMeasureHR}, counter: {counter}")
        if counter % PERIODO_PRESSURE == 0:
            newPressuremeasure = int(MQTTpubsub.getPressuremeasure(counter))
            print(f"PRESSURE measure: {newPressuremeasure}, counter: {counter}")
        counter = counter + 1       # % MCD tutti i periodi
        time.sleep(1)
    
    MQTTsubscriber.stop()

