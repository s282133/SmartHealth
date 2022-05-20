### Description: This script runs on the Raspberry Pi and publishes the data collected from the sensors to the MQTT broker
###              You can regulate the polling period by changing the PERIODO_HR and PERIODO_PRESSURE variables
###              You can add more sensors easily, check the code below

# ORA E' ANCHE UN SUBSCRIBER !

from MyMQTT import *
import time
import json
import paho.mqtt.client as PahoMQTT
import time
from datetime import datetime
import sys

from heartrateSensor import heartrateSensorClass
from pressureSensor import pressureSensorClass
from glycemiaSensor import glycemiaSensorClass

# periodo di polling in minuti
POLLING_PERIOD_HR = 1               # chiedo una misurazione ogni 5 minuti
POLLING_PERIOD_PRESSURE = 2         # chiedo una misurazione ogni 10 minuti
POLLING_PERIOD_GLYCEMIA = 3        # chiedo una misurazione ogni 20 minuti

ONE_MINUTE_IN_SEC = 1               # per motivi di debug a volte lo metto ad 1 ma deve essere 60
                                    # ai fini della dimostrazione potrebbe essere troppo alto e potremmo decidere di abbassarlo
SEC_WAIT_NO_MONITORING = 3
SEC_WAIT_MONITORING = SEC_WAIT_NO_MONITORING / 3;

class rpiPub():

    # MQTT FUNCTIONS
    def __init__(self, clientID):
        self.client = MyMQTT(clientID, "test.mosquitto.org", 1883, self)
        self.clientID = clientID
        self.messageBroker = "test.mosquitto.org"
        self.monitoring = False
        self.counter = 0
        print(f"{self.clientID} created")
        self.start()
        self.initSensors()
        while True:
            self.routineFunction() 

    def start (self):
        self.client.start()
        self.subTopic = f"P4IoT/SmartHealth/{self.clientID}/+/monitoring"
        self.client.mySubscribe(self.subTopic)

    def stop (self):
        self.client.stop()

    def myPublish(self, topic, message):
        print(f"{self.clientID} publishing {message} to topic: {topic}")
        self.client.myPublish(topic, message)

    def notify(self, topic, message):
        if message == "ON":
            self.monitoring = True
            print(f"{self.clientID} monitoring is ON")
        elif message == "OFF":
            self.monitoring = False
            print(f"{self.clientID} monitoring is OFF")
        else:
            print(f"{self.clientID} received unknown message: {message}")

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
        topicHR = f"P4IoT/SmartHealth/{self.clientID}/heartrate"
        messageHR = {"bn": f"http://SmartHealth.org/{self.clientID}/heartrateSensor/", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}
        self.myPublish(topicHR, messageHR)
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
        messagePR = {"bn": f"http://SmartHealth.org/{self.clientID}/pressureSensor/", "e": [{"n": "pressureHigh", "u": "mmHg", "t": timeOfMessage, "v": pressureHigh}, {"n": "pressureLow", "u": "mmHg", "t": timeOfMessage, "v": pressureLow}]}
        self.myPublish(f"P4IoT/SmartHealth/{self.clientID}/pressure", messagePR)
        print(f"{self.clientID} published {pressureHigh},{pressureLow} with topic: P4IoT/SmartHealth/{self.clientID}/pressure")

    # GLYCEMIA

    def getGlycemia(self, counter):
        newMeasureGlycemia = self.glycemiaSensor.getGlycemia(counter)
        return newMeasureGlycemia

    def publishGlycemia(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messageGL = {"bn": f"http://SmartHealth.org/{self.clientID}/glycemiaSensor/", "e": [{"n": "glycemia", "u": "mg/dL", "t": timeOfMessage, "v": measure}]}
        self.myPublish(f"P4IoT/SmartHealth/{self.clientID}/glycemia", messageGL)
        print(f"{self.clientID} published {measure} with topic: P4IoT/SmartHealth/{self.clientID}/glycemia")

    def routineFunction(self):
        if(self.monitoring == False):
            if self.counter % POLLING_PERIOD_HR == 0:
                time.sleep(SEC_WAIT_NO_MONITORING)
                newMeasureHR = int(self.getHRmeasure(self.counter))
                self.publishHR(newMeasureHR)
            if self.counter % POLLING_PERIOD_PRESSURE == 0:
                time.sleep(SEC_WAIT_NO_MONITORING)
                newMeasurePressureDict = self.getPressuremeasure(self.counter)
                self.publishPressure(newMeasurePressureDict)
            if self.counter % POLLING_PERIOD_GLYCEMIA == 0:
                time.sleep(SEC_WAIT_NO_MONITORING)
                newMeasureGlycemia = int(self.getGlycemia(self.counter))
                self.publishGlycemia(newMeasureGlycemia)
            self.counter = self.counter + 1
            time.sleep(ONE_MINUTE_IN_SEC)
        else:
            if self.counter % POLLING_PERIOD_HR == 0:
                time.sleep(SEC_WAIT_MONITORING)
                newMeasureHR = int(self.getHRmeasure(self.counter))
                self.publishHR(newMeasureHR)
            if self.counter % POLLING_PERIOD_PRESSURE == 0:
                time.sleep(SEC_WAIT_MONITORING)
                newMeasurePressureDict = self.getPressuremeasure(self.counter)
                self.publishPressure(newMeasurePressureDict)
            if self.counter % POLLING_PERIOD_GLYCEMIA == 0:
                time.sleep(SEC_WAIT_MONITORING)
                newMeasureGlycemia = int(self.getGlycemia(self.counter))
                self.publishGlycemia(newMeasureGlycemia)
            self.counter = self.counter + 1
            time.sleep(ONE_MINUTE_IN_SEC)

    # altri sensori possono essere aggiunti qua

if __name__ == "__main__":

    rpi = rpiPub(sys.argv[1])      # qui devo definire il patientID, parla con le ragazze


    # ho spostato tutta la parte di sotto nella funzione "routineFunction"

    rpi.start()

    rpi.initSensors()

    counter = 0
    
    monitoring = False

    while True:
        if(monitoring == False):
            if counter % POLLING_PERIOD_HR == 0:
                time.sleep(SEC_WAIT_NO_MONITORING)
                newMeasureHR = int(rpi.getHRmeasure(counter))
                rpi.publishHR(newMeasureHR)
            if counter % POLLING_PERIOD_PRESSURE == 0:
                time.sleep(SEC_WAIT_NO_MONITORING)
                newMeasurePressureDict = rpi.getPressuremeasure(counter)
                rpi.publishPressure(newMeasurePressureDict)
            if counter % POLLING_PERIOD_GLYCEMIA == 0:
                time.sleep(SEC_WAIT_NO_MONITORING)
                newMeasureGlycemia = int(rpi.getGlycemia(counter))
                rpi.publishGlycemia(newMeasureGlycemia)
            counter = counter + 1
            time.sleep(ONE_MINUTE_IN_SEC)
        else:
            if counter % POLLING_PERIOD_HR == 0:
                time.sleep(SEC_WAIT_MONITORING)
                newMeasureHR = int(rpi.getHRmeasure(counter))
                rpi.publishHR(newMeasureHR)
            if counter % POLLING_PERIOD_PRESSURE == 0:
                time.sleep(SEC_WAIT_MONITORING)
                newMeasurePressureDict = rpi.getPressuremeasure(counter)
                rpi.publishPressure(newMeasurePressureDict)
            if counter % POLLING_PERIOD_GLYCEMIA == 0:
                time.sleep(SEC_WAIT_MONITORING)
                newMeasureGlycemia = int(rpi.getGlycemia(counter))
                rpi.publishGlycemia(newMeasureGlycemia)
            counter = counter + 1
            time.sleep(ONE_MINUTE_IN_SEC)