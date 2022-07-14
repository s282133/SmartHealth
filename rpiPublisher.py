### Description: This script runs on the Raspberry Pi and publishes the data collected from the sensors to the MQTT broker
###              You can regulate the polling period by changing the PERIODO_HR and PERIODO_PRESSURE variables
###              You can add more sensors easily, check the code below
###              It's also a subscriber cause recives data from "monitoring" command       

import time
import json
from threading import Thread
from datetime import datetime

from CatalogueAndSettings import *
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

from DeviceConnectorAndSensors.heartrateSensor import heartrateSensorClass
from DeviceConnectorAndSensors.pressureSensor import pressureSensorClass
from DeviceConnectorAndSensors.glycemiaSensor import glycemiaSensorClass

TOPIC_TEMP_RASPBERRY = "temp_raspberry"

# periodo di polling in minuti
POLLING_PERIOD_HR       = 20         # chiedo una misurazione ogni 5 minuti
POLLING_PERIOD_PRESSURE = 22         # chiedo una misurazione ogni 10 minuti
POLLING_PERIOD_GLYCEMIA = 24         # chiedo una misurazione ogni 20 minuti

POLLING_MONITORING_HR       = 10         # chiedo una misurazione ogni 5 minuti
POLLING_MONITORING_PRESSURE = 12         # chiedo una misurazione ogni 10 minuti
POLLING_MONITORING_GLYCEMIA = 14         # chiedo una misurazione ogni 20 minuti

SECONDI_SCADENZA_MONITORING = 30       

ONE_MINUTE_IN_SEC = 0                # per motivi di debug a volte lo metto ad 1 ma deve essere 60
                                     # ai fini della dimostrazione potrebbe essere troppo alto e potremmo decidere di abbassarlo
SEC_WAIT_NO_MONITORING = 1
SEC_WAIT_MONITORING = SEC_WAIT_NO_MONITORING / 3

class rpiPub():

    # MQTT FUNCTIONS
    def __init__(self, clientID):
        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = int(clientID)

        self.monitoring_status = getMonitoringStateFromClientID(self.clientID)
        if self.monitoring_status == "on":
            self.monitoring = True
        else:
            self.monitoring = False

        self.counter = 0
        self.monitoring_counter = 0

        print(f"{self.clientID} created")
        self.start()
        self.initSensors()
        while True:
            self.routineFunction() 

    def start (self):
        self.client_MQTT.start()
        self.subTopic = f"{mqtt_base_topic}/{self.clientID}/monitoring"    
        self.client_MQTT.mySubscribe(self.subTopic)

        #da sostituire con jinja
        self.TopicTempRaspberry = getTopicByParameters(mqtt_topic, mqtt_base_topic, str(self.clientID))
        
        self.client_MQTT.mySubscribe(self.TopicTempRaspberry)

    def stop (self):
        self.client_MQTT.stop()

    def myPublish(self, topic, message):
        #print(f"{self.clientID} publishing {message} to topic: {topic}")
        self.client_MQTT.myPublish(topic, message)

    def notify(self, topic, message):
        msg = json.loads(message)
        subtopic = topic.split("/")[3]
        if subtopic == "monitoring":           
            print(f"{self.clientID} received {msg} from topic: {topic}")
            self.monitoring_status = msg["status"]
            if self.monitoring_status == "on":
                self.monitoring_counter = 0
                self.monitoring = True
            elif self.monitoring_status=="off":
                self.monitoring = False

            setMonitorinStatefromClientID(self.monitoring_status, self.clientID)

        elif subtopic == TOPIC_TEMP_RASPBERRY:      
            newMeasureTempRaspberry = msg["e"][0]["v"]
            #print(f"{self.clientID} received {newMeasureTempRaspberry} from topic: {topic}")
            self.publishTemperature(newMeasureTempRaspberry)
        else: 
            pass

        
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
        topicHR = f"{mqtt_base_topic}/{self.clientID}/heartrate"
        messageHR = {"bn": f"http://SmartHealth.org/{self.clientID}/heartrateSensor/", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}
        self.myPublish(topicHR, messageHR)
        print(f"{self.clientID} published {measure} with topic: {mqtt_base_topic}/{self.clientID}/heartrate ({self.monitoring_status})")

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
        self.myPublish(f"{mqtt_base_topic}/{self.clientID}/pressure", messagePR)
        print(f"{self.clientID} published {pressureHigh},{pressureLow} with topic: {mqtt_base_topic}/{self.clientID}/pressure ({self.monitoring_status})")

    # GLYCEMIA

    def getGlycemia(self, counter):
        newMeasureGlycemia = self.glycemiaSensor.getGlycemia(counter)
        return newMeasureGlycemia

    def publishGlycemia(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messageGL = {"bn": f"http://SmartHealth.org/{self.clientID}/glycemiaSensor/", "e": [{"n": "glycemia", "u": "mg/dL", "t": timeOfMessage, "v": measure}]}
        self.myPublish(f"{mqtt_base_topic}/{self.clientID}/glycemia", messageGL)
        print(f"{self.clientID} published {measure} with topic: {mqtt_base_topic}/{self.clientID}/glycemia ({self.monitoring_status})")


    # TEMPERATURE

    def publishTemperature(self, measureTemp):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messageTE = {"bn": f"http://SmartHealth.org/{self.clientID}/temperatureSensor/", "e": [{"n": "temperature", "u": "C", "t": timeOfMessage, "v": measureTemp}]}
        self.myPublish(f"{mqtt_base_topic}/{self.clientID}/temperature", messageTE)
        print(f"{self.clientID} published {measureTemp} with topic: {mqtt_base_topic}/{self.clientID}/temperature")


    # Lettura e pubblicazione dati 

    def routineFunction(self):
        time.sleep(1)
        if(self.monitoring == False):
            #print("Monitoraggio OFF")
            #time.sleep(SEC_WAIT_NO_MONITORING)
            if self.counter % POLLING_PERIOD_HR == 0:
                newMeasureHR = int(self.getHRmeasure(self.counter))
                self.publishHR(newMeasureHR)
            if self.counter % POLLING_PERIOD_PRESSURE == 0:
                newMeasurePressureDict = self.getPressuremeasure(self.counter)
                self.publishPressure(newMeasurePressureDict)
            if self.counter % POLLING_PERIOD_GLYCEMIA == 0:
                newMeasureGlycemia = int(self.getGlycemia(self.counter))
                self.publishGlycemia(newMeasureGlycemia)
            self.counter = self.counter + 1
            #time.sleep(ONE_MINUTE_IN_SEC)
        else:
            #print("Monitoraggio ON")
            #time.sleep(SEC_WAIT_MONITORING)
            if self.counter % POLLING_MONITORING_HR == 0:
                newMeasureHR = int(self.getHRmeasure(self.counter))
                self.publishHR(newMeasureHR)
            if self.counter % POLLING_MONITORING_PRESSURE == 0:
                newMeasurePressureDict = self.getPressuremeasure(self.counter)
                self.publishPressure(newMeasurePressureDict)
            if self.counter % POLLING_MONITORING_GLYCEMIA == 0:
                newMeasureGlycemia = int(self.getGlycemia(self.counter))
                self.publishGlycemia(newMeasureGlycemia)
            self.counter = self.counter + 1

            self.monitoring_counter = self.monitoring_counter + 1
            if self.monitoring_counter == SECONDI_SCADENZA_MONITORING:
                self.monitoring_counter = 0
                self.monitoring_status ="off"
                self.monitoring = False
                setMonitorinStatefromClientID(self.monitoring_status, self.clientID)


# def getWeek(dayOne):
#     currTime = time.strftime("%Y-%m-%d")
#     currY = currTime.split("-")[0]
#     currM = currTime.split("-")[1]
#     currD = currTime.split("-")[2]
#     #print(f"currY: {currY}, currM: {currM}, currD: {currD}")
#     currDays = int(currY)*365 + int(currM)*30 + int(currD)
#     #print(f"DataAnalysisBlock: current day is {currDays}")

#     #print(f"DataAnalysisBlock: clientID : {self.clientID}" )      
#     #print(f"DataAnalysisBlock: dayOne : {dayOne}")
#     dayoneY = dayOne.split("-")[0]
#     dayoneM = dayOne.split("-")[1]
#     dayoneD = dayOne.split("-")[2]
#     #print(f"dayoneY: {dayoneY}, dayoneM: {dayoneM}, dayoneD: {dayoneD}")
#     dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
#     #print(f"dayoneDays of {self.clientID} is {dayoneDays}")

#     elapsedDays = currDays - dayoneDays
#     week = int(elapsedDays / 7)
#     return week


if __name__ == "__main__":

    #setOnlineSinceFromClientID(1)
    #setOnlineSinceFromClientID(2)
    #setOnlineSinceFromClientID(3)
    setOnlineSinceFromClientID(6)

    # Gestione servizi MQTT
    resouce_filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    catalog = json.load(open(resouce_filename))
    services = catalog["services"]
    mqtt_service = getServiceByName(services,"MQTT_rilevazione_valori")
    if mqtt_service == None:
        print("Servizio registrazione non trovato")
    mqtt_broker = mqtt_service["broker"]
    mqtt_port = mqtt_service["port"]
    mqtt_base_topic = mqtt_service["base_topic"]
    mqtt_api = getApiByName(mqtt_service["APIs"],"send_temperature") 
    mqtt_topic = mqtt_api["topic"]

    cicli=0
    while True:
        if cicli % 200 == 0:

            filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
            f = open(filename)
            catalog = json.load(f)

            doctorList = catalog["resources"]
            if len(doctorList) > 0:

                for doctorObject in doctorList:
                    patientList = doctorObject["patientList"]
                    if len(patientList) > 0:

                        for userObject in patientList:
                            connectedDevice = userObject["connectedDevice"]

                            if connectedDevice["onlineSince"] == -1:
                                
                                connectedDevice["onlineSince"] = time.strftime("%Y-%m-%d") 
                                with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
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
                                with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
                                    json.dump(catalog, f, indent=2)
        cicli+=1
        time.sleep(0.1)
        #time.sleep(60)
