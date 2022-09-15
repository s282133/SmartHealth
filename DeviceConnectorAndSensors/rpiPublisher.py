### Description: This script runs on the Raspberry Pi and publishes the data collected from the sensors to the MQTT broker
###              You can regulate the polling period by changing the PERIODO_HR and PERIODO_PRESSURE variables
###              You can add more sensors easily, check the code below
###              It's also a subscriber cause recives data from "monitoring" command       

import time
import json
from threading import Thread
from datetime import datetime


from MyMQTT import *
from functionsOnCatalogue import *

from heartrateSensor import heartrateSensorClass
from pressureSensor import pressureSensorClass
from glycemiaSensor import glycemiaSensorClass

TOPIC_TEMP_RASPBERRY = "temp_raspberry"
TOPIC_TEMP_SIMULATE = "temp_simulate"

# periodo di polling in minuti
POLLING_PERIOD_HR       = 60    
POLLING_PERIOD_PRESSURE = 85        
POLLING_PERIOD_GLYCEMIA = 115       

POLLING_MONITORING_HR       = 25        
POLLING_MONITORING_PRESSURE = 48      
POLLING_MONITORING_GLYCEMIA = 115     

SECONDI_SCADENZA_MONITORING = 300      
SECONDI_CONTROLLO_NUOVI_PAZIENTI = 30
SECONDI_CONTROLLO_SETIMANE_GRAVIDANZA = 3600*24

ONE_MINUTE_IN_SEC = 0                
                                   
SEC_WAIT_NO_MONITORING = 1
SEC_WAIT_MONITORING = SEC_WAIT_NO_MONITORING / 3

class rpiPub():

    def __init__(self, clientID):

        # Gestione servizi MQTT
        try:
            mqtt_service = http_getServiceByName("MQTT_analysis")
            mqtt_broker = mqtt_service["broker"]
            mqtt_port = mqtt_service["port"]
            self.mqtt_base_topic = mqtt_service["base_topic"]
        except:
            print("RPI Publisher - error [ERR 1]")
            exit()

        try:
            #topic sub
            mqtt_api = get_api_from_service_and_name(mqtt_service,"temp_raspberry") 
            self.mqtt_topic_temp_raspberry = mqtt_api["topic"]

            mqtt_api_monitoring = get_api_from_service_and_name(mqtt_service,"monitoring_on") 
            self.mqtt_topic_monitoring_on  = mqtt_api_monitoring["topic"]
            
            mqtt_api_temp_simulate = get_api_from_service_and_name(mqtt_service,"temp_simulate") 
            self.mqtt_topic_temp_simulate  = mqtt_api_temp_simulate["topic"]
            ##
            
            mqtt_api_heartrate = get_api_from_service_and_name(mqtt_service,"heartrate") 
            self.mqtt_topic_heartrate  = mqtt_api_heartrate["topic"]
            mqtt_api_pressure = get_api_from_service_and_name(mqtt_service,"pressure") 
            self.mqtt_topic_pressure  = mqtt_api_pressure["topic"]
            mqtt_api_glycemia = get_api_from_service_and_name(mqtt_service,"glycemia") 
            self.mqtt_topic_glycemia  = mqtt_api_glycemia["topic"]
            mqtt_api_temperature = get_api_from_service_and_name(mqtt_service,"temperature") 
            self.mqtt_topic_temperature  = mqtt_api_temperature["topic"]
        except:
            print("RPI Publisher - error [ERR 2]")
            exit()

        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = int(clientID)

        try:
            self.monitoring_status = http_getMonitoringStateFromClientID(self.clientID)
            if self.monitoring_status == "on":
                self.monitoring = True
            else:
                self.monitoring = False
        except:
            self.monitoring = False
            self.monitoring_status = "off"
            print("RPI Publisher - error [ERR 3]")
            exit()

        self.counter = 0
        self.monitoring_counter = 0

        print(f"{self.clientID} created")
        self.start()
        self.initSensors()
        while True:
            self.routineFunction() 


    def start (self):
        self.client_MQTT.start()

        try:
            TopicTempRaspberry = getTopicByParameters(self.mqtt_topic_temp_raspberry, self.mqtt_base_topic, self.clientID)
            self.client_MQTT.mySubscribe(TopicTempRaspberry)

            #{{base_topic}}/{{patientID}}/monitoring
            topic_monitoring = getTopicByParameters(self.mqtt_topic_monitoring_on, self.mqtt_base_topic, self.clientID)
            self.client_MQTT.mySubscribe(topic_monitoring)
            
            #{{base_topic}}/{{patientID}}/temp_simulate
            topic_temp_simulate = getTopicByParameters(self.mqtt_topic_temp_simulate, self.mqtt_base_topic, self.clientID)
            self.client_MQTT.mySubscribe(topic_temp_simulate)
        except:
            print("RPI Publisher - error [ERR 4]")
            exit()


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

            try:
                http_setMonitorinStatefromClientID(self.clientID, self.monitoring_status)
            except:
                print("RPI Publisher - error [ERR 5]")
                exit()

        elif subtopic == TOPIC_TEMP_RASPBERRY:      
            newMeasureTempRaspberry = msg["e"][0]["v"]
            #print(f"{self.clientID} received {newMeasureTempRaspberry} from topic: {topic}")
            self.publishTemperature(newMeasureTempRaspberry)
            
        elif subtopic == TOPIC_TEMP_SIMULATE:      
            newMeasureTempSimulate = msg["e"][0]["v"]
            #print(f"{self.clientID} received {newMeasureTempRaspberry} from topic: {topic}")
            self.publishTemperature(newMeasureTempSimulate)
            
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

        try:
            topicHR = getTopicByParameters(self.mqtt_topic_heartrate, self.mqtt_base_topic, self.clientID)
        except:
            print("RPI Publisher - error [ERR 6]")
            exit()
        #topicHR = f"{self.mqtt_base_topic}/{self.clientID}/heartrate"

        # Perchè le misure non sono nel vettore "e"? Per quale motivo è conveniente?
        # Perchè non abbiamo specificayo mai il sensore ma solo il raspberry? E' sufficiente?
        try:
            ResourceService = http_getServiceByName("ResourceService")
            bn = get_api_from_service_and_name(ResourceService,"gestione_bn") 
            basic_uri = bn["basic_uri"]
            heartrateSensor = bn["heartrate_sensor"]

            messageHR = {"bn": f"{basic_uri}/{self.clientID}/{heartrateSensor}/", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}

            #bn non nel settings
            #messageHR = {"bn": f"http://SmartHealth.org/{self.clientID}/heartrateSensor/", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}
            
            #Alternativa al bn che inizi per //http
            #messageHR = {"bn": f"{self.clientID}", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}
            self.myPublish(topicHR, messageHR)
            print(f"{self.clientID} published {measure} with topic: {topicHR} ({self.monitoring_status})")
        except:
            print("RPI Publisher - error [ERR 7]")
            exit()

    # PRESSURE

    def getPressuremeasure(self, counter):
        dictPressure = self.pressureSensor.getPressure(counter)
        return dictPressure

    def publishPressure(self, measureDict):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pressureHigh = measureDict["pressureHigh"]
        pressureLow = measureDict["pressureLow"]

        try:
            topicPR= getTopicByParameters(self.mqtt_topic_pressure, self.mqtt_base_topic, self.clientID)
            #f"{self.mqtt_base_topic}/{self.clientID}/pressure"
        except:
            print("RPI Publisher - error [ERR 8]")
            exit()
        
        try:
            ResourceService = http_getServiceByName("ResourceService")
            bn = get_api_from_service_and_name(ResourceService,"gestione_bn") 
            basic_uri = bn["basic_uri"]
            pressureSensor = bn["pressure_sensor"]
            messagePR = {"bn": f"{basic_uri}/{self.clientID}/{pressureSensor}/", "e": [{"n": "pressureHigh", "u": "mmHg", "t": timeOfMessage, "v": pressureHigh}, {"n": "pressureLow", "u": "mmHg", "t": timeOfMessage, "v": pressureLow}]}

            #messagePR = {"bn": f"http://SmartHealth.org/{self.clientID}/pressureSensor/", "e": [{"n": "pressureHigh", "u": "mmHg", "t": timeOfMessage, "v": pressureHigh}, {"n": "pressureLow", "u": "mmHg", "t": timeOfMessage, "v": pressureLow}]}
            self.myPublish(topicPR, messagePR)
            print(f"{self.clientID} published {pressureHigh},{pressureLow} with topic: {topicPR} ({self.monitoring_status})")
        except:
            print("RPI Publisher - error [ERR 9]")
            exit()

    # GLYCEMIA

    def getGlycemia(self, counter):
        newMeasureGlycemia = self.glycemiaSensor.getGlycemia(counter)
        return newMeasureGlycemia

    def publishGlycemia(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            topicGL= getTopicByParameters(self.mqtt_topic_glycemia, self.mqtt_base_topic, self.clientID)
        except:
            print("RPI Publisher - error [ERR 10]")
            exit()
        
        try:
            ResourceService = http_getServiceByName("ResourceService")
            bn = get_api_from_service_and_name(ResourceService,"gestione_bn") 
            basic_uri = bn["basic_uri"]
            glycemiaSensor = bn["glycemia_sensor"]
            messageGL = {"bn": f"{basic_uri}/{self.clientID}/{glycemiaSensor}/", "e": [{"n": "glycemia", "u": "mg/dL", "t": timeOfMessage, "v": measure}]}

            #messageGL = {"bn": f"http://SmartHealth.org/{self.clientID}/glycemiaSensor/", "e": [{"n": "glycemia", "u": "mg/dL", "t": timeOfMessage, "v": measure}]}
            self.myPublish(topicGL, messageGL)
            print(f"{self.clientID} published {measure} with topic: {topicGL} ({self.monitoring_status})")
        except:
            print("RPI Publisher - error [ERR 11]")
            exit()

    # TEMPERATURE

    def publishTemperature(self, measureTemp):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            topicTE = getTopicByParameters(self.mqtt_topic_temperature, self.mqtt_base_topic, self.clientID)
        except:
            print("RPI Publisher - error [ERR 12]")
            exit()
        
        try:
            ResourceService = http_getServiceByName("ResourceService")
            bn = get_api_from_service_and_name(ResourceService,"gestione_bn") 
            basic_uri = bn["basic_uri"]
            temperatureSensor = bn["temperature_sensor"]

            messageTE = {"bn": f"{basic_uri}/{self.clientID}/{temperatureSensor}/", "e": [{"n": "temperature", "u": "C", "t": timeOfMessage, "v": measureTemp}]}
            self.myPublish(topicTE, messageTE)
            print(f"{self.clientID} published {measureTemp} with topic: {topicTE} ({self.monitoring_status})")
        except:
            print("RPI Publisher - error [ERR 13]")
            exit()

    # Lettura e pubblicazione dati 

    def routineFunction(self):
        time.sleep(1)
        if(self.monitoring == False):

            if self.counter % POLLING_PERIOD_HR == 0:
                try:
                    newMeasureHR = int(self.getHRmeasure(self.counter))
                    self.publishHR(newMeasureHR)
                except:
                    print("RPI Publisher - error [ERR 14]")
                    exit()
            if self.counter % POLLING_PERIOD_PRESSURE == 0:
                try:
                    newMeasurePressureDict = self.getPressuremeasure(self.counter)
                    self.publishPressure(newMeasurePressureDict)
                except:
                    print("RPI Publisher - error [ERR 15]")
                    exit()
            if self.counter % POLLING_PERIOD_GLYCEMIA == 0:
                try:
                    newMeasureGlycemia = int(self.getGlycemia(self.counter))
                    self.publishGlycemia(newMeasureGlycemia)
                except:
                    print("RPI Publisher - error [ERR 16]")
                    exit()
            self.counter = self.counter + 1
        else:
            if self.counter % POLLING_MONITORING_HR == 0:
                try:
                    newMeasureHR = int(self.getHRmeasure(self.counter))
                    self.publishHR(newMeasureHR)
                except:
                    print("RPI Publisher - error [ERR 17]")
                    exit()
            if self.counter % POLLING_MONITORING_PRESSURE == 0:
                try:
                    newMeasurePressureDict = self.getPressuremeasure(self.counter)
                    self.publishPressure(newMeasurePressureDict)
                except:
                    print("RPI Publisher - error [ERR 18]")
                    exit()
            if self.counter % POLLING_MONITORING_GLYCEMIA == 0:
                try:
                    newMeasureGlycemia = int(self.getGlycemia(self.counter))
                    self.publishGlycemia(newMeasureGlycemia)
                except:
                    print("RPI Publisher - error [ERR 19]")
                    exit()
            self.counter = self.counter + 1

            self.monitoring_counter = self.monitoring_counter + 1
            if self.monitoring_counter == SECONDI_SCADENZA_MONITORING:
                self.monitoring_counter = 0
                self.monitoring_status ="off"
                self.monitoring = False
                http_setMonitorinStatefromClientID(self.clientID, self.monitoring_status)



if __name__ == "__main__":

    # DEBUG: da eliminare alla fine: imposta in automatico il -1 sul paziente 9 per far pubblicare su di lui
    # setOnlineSinceFromClientID(10)
    # setOnlineSinceFromClientID(1)


    cicli=0
    while True:

        # Eseguito ogni 30 secondi
        if cicli % SECONDI_CONTROLLO_NUOVI_PAZIENTI == 0:

            try:
                # print("primo try")
                json_lista = http_get_lista_pazienti_da_monitorare()
                # print(f"{json_lista}")
                lista_pazienti_da_monitorare = json_lista["lista_pazienti_da_monitorare"]
                # print(f"{lista_pazienti_da_monitorare}")
              
            except:
                print("RPI Publisher - error [ERR 20]")
                exit()

            for patientID in lista_pazienti_da_monitorare:
                # print("sono entrato nel for")
                try:
                    http_set_patient_in_monitoring(patientID)  
                    # print("secondo try")
                    thread = Thread(target=rpiPub, args=(str(patientID),))
                    thread.start()
                    # print(f"{patientID} is online")
                except:
                    print("RPI Publisher - error [ERR 21]")
                    exit()

        # Eseguito all'avvio e ogni 24 ore
        if cicli % SECONDI_CONTROLLO_SETIMANE_GRAVIDANZA == 0:
            try:
                http_contolla_scadenza_week()
            except:
                print("RPI Publisher - error [ERR 22]")
                exit()
                
        cicli+=1
        time.sleep(1)