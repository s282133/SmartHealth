### Description: This script runs on the Raspberry Pi and publishes the data collected from the sensors to the MQTT broker
###              You can regulate the polling period by changing the PERIODO_HR and PERIODO_PRESSURE variables
###              You can add more sensors easily, check the code below

from MyMQTT import *
import time
import json
import paho.mqtt.client as PahoMQTT
import time
from datetime import datetime

from heartrateSensor import heartrateSensorClass
from pressureSensor import pressureSensorClass
from glycemiaSensor import glycemiaSensorClass

# periodo di polling in minuti
POLLING_PERIOD_HR = 1               # chiedo una misurazione ogni 5 minuti
POLLING_PERIOD_PRESSURE = 2         # chiedo una misurazione ogni 10 minuti
POLLING_PERIOD_GLYCEMIA = 3        # chiedo una misurazione ogni 20 minuti

ONE_MINUTE_IN_SEC = 60               # per motivi di debug a volte lo metto ad 1 ma deve essere 60
                                    # ai fini della dimostrazione potrebbe essere troppo alto e potremmo decidere di abbassarlo

class rpiPub():

    # MQTT FUNCTIONS
    def __init__(self, clientID):
        self.clientID = clientID
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        self._paho_mqtt.on_connect = self.myOnConnect

        self.messageBroker = 'test.mosquitto.org'

    def start (self):
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()

    def stop (self):
        self._paho_mqtt.loop_stop() 
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
        self._paho_mqtt.publish(topic, message, 2)

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.messageBroker, rc))


    ##### SENSORS FUNCTIONS #####

    def initSensors(self):
        self.heartrateSensor = heartrateSensorClass()
        self.pressureSensor = pressureSensorClass()
        self.glycemiaSensor = glycemiaSensorClass()

    # HEARTRATE

    def getHRmeasure(self, counter):
        newMeasureHR = self.heartrateSensor.getHR(counter)
        return newMeasureHR

    def publishHR(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rpi.myPublish(f"P4IoT/SmartHealth/{self.clientID}/heartrate", json.dumps({"bn": f"http://SmartHealth.org/{self.clientID}/heartrateSensor/", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}))
        print(f"{self.clientID} published {measure} with topic: P4IoT/SmartHealth/{self.clientID}/heartrate")

    # PRESSURE

    def getPressuremeasure(self, counter):
        dictPressure = self.pressureSensor.getPressure(counter)
        return dictPressure

    def publishPressure(self, measureDict):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pressureHigh = measureDict["pressureHigh"]
        pressureLow = measureDict["pressureLow"]
        # TODO : mettere 2 "e", una per min e una per max
        rpi.myPublish(f"P4IoT/SmartHealth/{self.clientID}/pressure", json.dumps({"bn": f"http://SmartHealth.org/{self.clientID}/pressureSensor/", "e": [{"n": "pressure", "u": "hPa", "t": timeOfMessage, "v": f'{pressureHigh},{pressureLow}'}]}))
        print(f"{self.clientID} published {pressureHigh},{pressureLow} with topic: P4IoT/SmartHealth/{self.clientID}/pressure")

    # GLYCEMIA

    def getGlycemia(self, counter):
        newMeasureGlycemia = self.glycemiaSensor.getGlycemia(counter)
        return newMeasureGlycemia

    def publishGlycemia(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rpi.myPublish("P4IoT/SmartHealth/{self.clientID}/glycemia", json.dumps({"bn": f"http://SmartHealth.org/{self.clientID}/glycemiaSensor/", "e": [{"n": "glycemia", "u": "mg/dL", "t": timeOfMessage, "v": measure}]}))
        print(f"{self.clientID} published {measure} with topic: P4IoT/SmartHealth/{self.clientID}/glycemia")


    # altri sensori possono essere aggiunti qua


if __name__ == "__main__":

    rpi = rpiPub("345")      # qui devo definire il clientID, parla con le ragazze

    rpi.start()

    rpi.initSensors()
    SEC_WAIT = 3
    counter = 0
    while True:
        if counter % POLLING_PERIOD_HR == 0:
            time.sleep(SEC_WAIT)
            newMeasureHR = int(rpi.getHRmeasure(counter))
            rpi.publishHR(newMeasureHR)
        if counter % POLLING_PERIOD_PRESSURE == 0:
            time.sleep(SEC_WAIT)
            newMeasurePressureDict = rpi.getPressuremeasure(counter)
            rpi.publishPressure(newMeasurePressureDict)
        if counter % POLLING_PERIOD_GLYCEMIA == 0:
            time.sleep(SEC_WAIT)
            newMeasureGlycemia = int(rpi.getGlycemia(counter))
            rpi.publishGlycemia(newMeasureGlycemia)
        counter = counter + 1
        time.sleep(ONE_MINUTE_IN_SEC)