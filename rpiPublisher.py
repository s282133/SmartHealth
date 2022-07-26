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
POLLING_PERIOD_HR       = 60     
POLLING_PERIOD_PRESSURE = 85        
POLLING_PERIOD_GLYCEMIA = 115       

POLLING_MONITORING_HR       = 25        
POLLING_MONITORING_PRESSURE = 48      
POLLING_MONITORING_GLYCEMIA = 71       

SECONDI_SCADENZA_MONITORING = 300      

ONE_MINUTE_IN_SEC = 0                
                                   
SEC_WAIT_NO_MONITORING = 1
SEC_WAIT_MONITORING = SEC_WAIT_NO_MONITORING / 3

class rpiPub():

    def __init__(self, clientID):

        # Gestione servizi MQTT
        mqtt_service = http_getServiceByName("MQTT_analysis")

        if mqtt_service == None:
            print("Servizio registrazione non trovato")
            exit()

        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        self.mqtt_base_topic = mqtt_service["base_topic"]
        mqtt_api = http_getApiByName("MQTT_analysis","send_temperature") 
        self.mqtt_topic = mqtt_api["topic"]

        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = int(clientID)

        self.monitoring_status = http_getMonitoringStateFromClientID(self.clientID)
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
        self.subTopic = f"{self.mqtt_base_topic}/{self.clientID}/monitoring"    
        self.client_MQTT.mySubscribe(self.subTopic)
        #da sostituire con jinja?
        self.TopicTempRaspberry = getTopicByParameters(self.mqtt_topic, self.mqtt_base_topic, str(self.clientID))
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
            http_setMonitorinStatefromClientID(self.clientID, self.monitoring_status)
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
        topicHR = f"{self.mqtt_base_topic}/{self.clientID}/heartrate"
        messageHR = {"bn": f"http://SmartHealth.org/{self.clientID}/heartrateSensor/", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}
        self.myPublish(topicHR, messageHR)
        print(f"{self.clientID} published {measure} with topic: {self.mqtt_base_topic}/{self.clientID}/heartrate ({self.monitoring_status})")


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
        self.myPublish(f"{self.mqtt_base_topic}/{self.clientID}/pressure", messagePR)
        print(f"{self.clientID} published {pressureHigh},{pressureLow} with topic: {self.mqtt_base_topic}/{self.clientID}/pressure ({self.monitoring_status})")


    # GLYCEMIA

    def getGlycemia(self, counter):
        newMeasureGlycemia = self.glycemiaSensor.getGlycemia(counter)
        return newMeasureGlycemia

    def publishGlycemia(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messageGL = {"bn": f"http://SmartHealth.org/{self.clientID}/glycemiaSensor/", "e": [{"n": "glycemia", "u": "mg/dL", "t": timeOfMessage, "v": measure}]}
        self.myPublish(f"{self.mqtt_base_topic}/{self.clientID}/glycemia", messageGL)
        print(f"{self.clientID} published {measure} with topic: {self.mqtt_base_topic}/{self.clientID}/glycemia ({self.monitoring_status})")


    # TEMPERATURE

    def publishTemperature(self, measureTemp):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messageTE = {"bn": f"http://SmartHealth.org/{self.clientID}/temperatureSensor/", "e": [{"n": "temperature", "u": "C", "t": timeOfMessage, "v": measureTemp}]}
        self.myPublish(f"{self.mqtt_base_topic}/{self.clientID}/temperature", messageTE)
        print(f"{self.clientID} published {measureTemp} with topic: {self.mqtt_base_topic}/{self.clientID}/temperature")


    # Lettura e pubblicazione dati 

    def routineFunction(self):
        time.sleep(1)
        if(self.monitoring == False):

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
        else:
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
                http_setMonitorinStatefromClientID(self.clientID, self.monitoring_status)


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

    # da eliminare alla fine: imposta in automatico il -1 sul paziente 1 per far pubblicare su di lui
    setOnlineSinceFromClientID(1)

    # da decidere dove metterla?
    http_contolla_scadenza_week()

    cicli=0
    while True:
        if cicli % 200 == 0:

            json_lista = http_get_lista_pazienti_da_monitorare()
            lista_pazienti_da_monitorare = json_lista["lista_pazienti_da_monitorare"]
            
            for patientID in lista_pazienti_da_monitorare:

                http_set_patient_in_monitoring(patientID)  

                thread = Thread(target=rpiPub, args=(str(patientID),))
                thread.start()
                print(f"{patientID} is online")

        cicli+=1
        time.sleep(0.1)