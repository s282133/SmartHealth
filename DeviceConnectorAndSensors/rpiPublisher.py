### Description: This script runs on the Raspberry Pi and publishes the data collected from the sensors to the MQTT broker
###              You can regulate the polling period by changing the PERIODO_HR and PERIODO_PRESSURE variables
###              You can add more sensors easily, check the code below
###              It's also a subscriber cause recives data from "monitoring" command       

# from MyMQTT import *
import time
import json
import paho.mqtt.client as PahoMQTT
import time
from threading import Thread
from datetime import datetime
import sys

from heartrateSensor import heartrateSensorClass
from pressureSensor import pressureSensorClass
from glycemiaSensor import glycemiaSensorClass

import sys, os
sys.path.insert(0, os.path.abspath('..'))
from CatalogueAndSettings import *
from commons.MyMQTT import *

# periodo di polling in minuti
POLLING_PERIOD_HR = 2               # chiedo una misurazione ogni 5 minuti
POLLING_PERIOD_PRESSURE = 3         # chiedo una misurazione ogni 10 minuti
POLLING_PERIOD_GLYCEMIA = 4         # chiedo una misurazione ogni 20 minuti

ONE_MINUTE_IN_SEC = 0              # per motivi di debug a volte lo metto ad 1 ma deve essere 60
                                    # ai fini della dimostrazione potrebbe essere troppo alto e potremmo decidere di abbassarlo
SEC_WAIT_NO_MONITORING = 12
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
        self.subTopic = f"P4IoT/SmartHealth/{self.client}/monitoring"      #da generalizzare
        self.client.mySubscribe(self.subTopic)

    def stop (self):
        self.client.stop()

    def myPublish(self, topic, message):
        print(f"{self.clientID} publishing {message} to topic: {topic}")
        self.client.myPublish(topic, message)

    def notify(self, topic, message):
        msg = json.loads(message)
        print(f"{self.clientID} received {msg} from topic: {topic}")
        if topic != f"P4IoT/SmartHealth/{self.client}/monitoring":           #da generalizzare
            pass
        else:
            status = msg["status"]
            if status == "ON":
                    self.monitoring = True
            elif status=="OFF":
                    self.monitoring = False
        

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
            print("Monitoraggio OFF")
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
            print("Monitoraggio ON")
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


def getWeek(dayOne):
    currTime = time.strftime("%Y-%m-%d")
    currY = currTime.split("-")[0]
    currM = currTime.split("-")[1]
    currD = currTime.split("-")[2]
    #print(f"currY: {currY}, currM: {currM}, currD: {currD}")
    currDays = int(currY)*365 + int(currM)*30 + int(currD)
    #print(f"DataAnalysisBlock: current day is {currDays}")

    #print(f"DataAnalysisBlock: clientID : {self.clientID}" )      
    #print(f"DataAnalysisBlock: dayOne : {dayOne}")
    dayoneY = dayOne.split("-")[0]
    dayoneM = dayOne.split("-")[1]
    dayoneD = dayOne.split("-")[2]
    #print(f"dayoneY: {dayoneY}, dayoneM: {dayoneM}, dayoneD: {dayoneD}")
    dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
    #print(f"dayoneDays of {self.clientID} is {dayoneDays}")

    elapsedDays = currDays - dayoneDays
    week = int(elapsedDays / 7)
    return week


if __name__ == "__main__":

#aggiungere un while

    #f = open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json')   
    while True:

        filename = sys.path[0] + '\\CatalogueAndSettings\\catalog.json'
        f = open(filename)
        catalog = json.load(f)

        doctorList = catalog["doctorList"]
        if len(doctorList) > 0:

            for doctorObject in doctorList:
                patientList = doctorObject["patientList"]
                if len(patientList) > 0:

                    for userObject in patientList:
                        connectedDevice = userObject["connectedDevice"]

                        if connectedDevice["onlineSince"] == -1:
                            connectedDevice["onlineSince"] = time.strftime("%Y-%m-%d") 
                            #f.close

                            with open(sys.path[0] + '\\CatalogueAndSettings\\catalog.json', "w") as f:
                                json.dump(catalog, f, indent=2)

                            patientID = userObject["patientID"] 
                            thread = Thread(target=rpiPub, args=(str(patientID),))
                            thread.start()

                            print(f"{patientID} is online")

                        # remove entry in catalogue if pregnancy week is greater than 36 (i.e., 9 months)
                        dayOne = userObject["personalData"]["pregnancyDayOne"] 
                        week = getWeek(dayOne)
                        print(f'Patient {userObject["patientID"]} is in week {week}')
                        if int(week) >= 36:
                            patientList.remove(userObject)
                            with open(sys.path[0] + '\\CatalogueAndSettings\\catalog.json', "w") as f:
                                json.dump(catalog, f, indent=2)

        time.sleep(60)
