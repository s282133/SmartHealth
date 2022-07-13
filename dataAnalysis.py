### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds
# telegramID Laura = 491287865

import time
import json

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

from gettext import Catalog
from DoctorBot import DoctorBot
from PatientBot import PatientBot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class dataAnalysisClass():

    # MQTT FUNCTIONS

    def __init__(self):
        self.client = MyMQTT(None, mqtt_broker, mqtt_port, self)
        timeshift_fn = 'PostProcessing\\timeshift.json'
        self.thresholdsFile = json.load(open(timeshift_fn,'r'))

    def start(self):
        self.client.start()
        self.client.mySubscribe(local_topic_temperature)
        self.client.mySubscribe(local_topic_heartrate)
        self.client.mySubscribe(local_topic_pressure)
        self.client.mySubscribe(local_topic_glycemia)

    def stop(self):
        self.client.stop()
        

    def myPublish(self, topic, message):
        self.client.myPublish(topic, message) 
        print(f"Published on {topic}")


    def notify(self, topic, msg):

        print(f"Il topic è: {topic}")
        d = json.loads(msg)
        self.bn = d["bn"]
        #variabile locale per evitare problemi legati alla concorrenza (variabile globale richiamata da un metodo diverso)
        local_clientID = int(self.bn.split("/")[3])  
        self.e = d["e"]
        self.measureType = self.e[0]["n"]
        self.unit = self.e[0]["u"]
        self.timestamp = self.e[0]["t"]
        self.value = self.e[0]["v"]

        # currY = self.timestamp.split("-")[0]
        # currM = self.timestamp.split("-")[1]
        # currD_hms = self.timestamp.split("-")[2]
        # currD = currD_hms.split(" ")[0]
        # #print(f"currY: {currY}, currM: {currM}, currD: {currD}")
        # currDays = int(currY)*365 + int(currM)*30 + int(currD)
        # #print(f"DataAnalysisBlock: current day is {currDays}")

        # #print(f"DataAnalysisBlock: clientID : {local_clientID}")
        # dayOne = retrievePregnancyDayOne(int(local_clientID))            
        # #print(f"DataAnalysisBlock: dayOne : {dayOne}")
        # dayoneY = dayOne.split("-")[0]
        # dayoneM = dayOne.split("-")[1]
        # dayoneD = dayOne.split("-")[2]
        # #print(f"dayoneY: {dayoneY}, dayoneM: {dayoneM}, dayoneD: {dayoneD}")
        # dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
        # #print(f"dayoneDays of {local_clientID} is {dayoneDays}")

        # elapsedDays = currDays - dayoneDays
        # week = int(elapsedDays / 7)
        # if(week == 0): 
        #     week = 1

        monitoringState = getMonitoringStateFromClientID(local_clientID)
        if monitoringState == "on":
            return

        dayOne = retrievePregnancyDayOne(local_clientID)

        patientName = getNameFromClientID(local_clientID)

        week = getWeek(dayOne)

        #print(f"TEST: week of pregnancy of patient {local_clientID} is {week}, from {dayOne} to {currY}-{currM}-{currD}, {elapsedDays} elapsed days")

        #print(f"DataAnalysisBlock: patient dayOne is {dayOne}")
        #print(f"DataAnalysisBlock: timestamp is {self.timestamp}")
        #print(f"week of pregnancy of patient {local_clientID} is {week}")
    

        if (self.measureType == "heartrate"):
            print(f"DataAnalysisBlock received HEARTRATE measure of: {self.value} at time {self.timestamp}, by {local_clientID}, week of pregnancy {week}")
            self.manageHeartRate(week,local_clientID,patientName)
        elif (self.measureType == "pressureHigh"):
            self.sensed_pressureHigh=self.e[0]["v"]
            self.sensed_pressureLow=self.e[1]["v"]
            print(f"DataAnalysisBlock received PRESSURE measure of: {self.sensed_pressureHigh}, {self.sensed_pressureLow} at time {self.timestamp}, by {local_clientID}, week of pregnancy {week}")
            self.managePressure(week,local_clientID,patientName)            
        elif (self.measureType == "glycemia"):
            print(f"DataAnalysisBlock received GLYCEMIA measure of: {self.value} at time {self.timestamp}, by {local_clientID}, week of pregnancy {week}")
            self.manageGlycemia(week,local_clientID,patientName)
        elif (self.measureType == "temperature"):
            print(f"DataAnalysisBlock received TEMPERATURE measure of: {self.value} at time {self.timestamp}, by {local_clientID}, week of pregnancy {week}")
            self.manageTemperature(week,local_clientID,patientName)
        else:
            print("Measure type not recognized")


    def manageHeartRate(self, week, parClientID, parPatientName):
        thresholdsHR = self.thresholdsFile["heartrate"]
        for rangeHR in thresholdsHR:
            weekmin = rangeHR["weekrange"].split("-")[0]
            weekmax = rangeHR["weekrange"].split("-")[1]   
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeHR["min"]) and int(self.value) <= int(rangeHR["max"])):
                    print(f"DataAnalysisBlock: heart rate is in range")
                else:
                    print(f"DataAnalysisBlock: heart rate is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["resources"]
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = findDoctorTelegramIdFromPatientId(parClientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID, messaggio, f"heartrate on {parClientID}", f"heartrate off {parClientID}")
                    else:
                        print("Doctor not found for this patient")

    def managePressure(self, week, parClientID, parPatientName):
        thresholdsPR = self.thresholdsFile["pressure"]
        for rangePR in thresholdsPR:
            weekmin = rangePR["weekrange"].split("-")[0]
            weekmax = rangePR["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                highmax=rangePR["high"]["max"]
                highmin=rangePR["high"]["min"]
                lowmax=rangePR["low"]["max"]
                lowmin=rangePR["low"]["min"]
                if (int(self.sensed_pressureHigh) >= int(highmax) and int(self.sensed_pressureHigh) <= int(highmin)) and  \
                    (int(self.sensed_pressureLow) >= int(lowmax) and int(self.sensed_pressureLow) <= int(lowmin)) :
                    print(f"DataAnalysisBlock: pressure is in range")
                else:
                    print(f"DataAnalysisBlock: pressure is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["resources"]
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = findDoctorTelegramIdFromPatientId(parClientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, f"pression on {parClientID}", f"pression off {parClientID}")
                    else:
                        print("Doctor not found for this patient")

    def manageGlycemia(self, week, parClientID, parPatientName):
        thresholdsGL = self.thresholdsFile["glycemia"]
        for rangeGL in thresholdsGL:
            weekmin = rangeGL["weekrange"].split("-")[0]
            weekmax = rangeGL["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeGL["min"]) and int(self.value) <= int(rangeGL["max"])):
                    print(f"DataAnalysisBlock: glycemia is in range")
                else:
                    print(f"DataAnalysisBlock: glycemia is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["resources"]
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    self.telegramID = findDoctorTelegramIdFromPatientId(parClientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, f"glycemia on {parClientID}", f"glycemia off {parClientID}")
                    else:
                        print("Doctor not found for this patient")

    def manageTemperature(self, week, parClientID, parPatientName):
        thresholdsTE = self.thresholdsFile["temperature"]
        for rangeTE in thresholdsTE:
            weekmin = rangeTE["weekrange"].split("-")[0]
            weekmax = rangeTE["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (float(self.value) >= float(rangeTE["min"]) and float(self.value) <= float(rangeTE["max"])):
                    print(f"DataAnalysisBlock: temperature is in range")
                else:
                    print(f"DataAnalysisBlock: temperature is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["resources"]
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    self.telegramID = findDoctorTelegramIdFromPatientId(parClientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, f"temperature on {parClientID}", f"temperature off {parClientID}")
                    else:
                        print("Doctor not found for this patient")

                              

if __name__ == "__main__":
    
    # Gestione servizi MQTT
    resouce_filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    catalog = json.load(open(resouce_filename))
    services = catalog["services"]

    mqtt_service = getServiceByName(services,"MQTT_analysis")
    if mqtt_service == None:
        print("Servizio registrazione non trovato")
    mqtt_broker = mqtt_service["broker"]
    mqtt_port = mqtt_service["port"]
    mqtt_base_topic = mqtt_service["base_topic"]
    mqtt_api = getApiByName(mqtt_service["APIs"],"send_measure") 

    mqtt_topic_temperature  = mqtt_api["topic_temperature"]
    mqtt_topic_heartrate    = mqtt_api["topic_heartrate"]
    mqtt_topic_pressure     = mqtt_api["topic_pressure"]
    mqtt_topic_glycemia     = mqtt_api["topic_glycemia"]

    local_topic_temperature = getTopicByParameters(mqtt_topic_temperature, mqtt_base_topic, "+")
    local_topic_heartrate   = getTopicByParameters(mqtt_topic_heartrate, mqtt_base_topic, "+")
    local_topic_pressure    = getTopicByParameters(mqtt_topic_pressure, mqtt_base_topic, "+")
    local_topic_glycemia    = getTopicByParameters(mqtt_topic_glycemia, mqtt_base_topic, "+")

    MQTTpubsub = dataAnalysisClass()
    MQTTpubsub.start()   

    mybot_dr=DoctorBot(MQTTpubsub)
    mybot_pz=PatientBot(MQTTpubsub)

    while True:
        time.sleep(10)


