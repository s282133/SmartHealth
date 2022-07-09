### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds
#se dovesse servire: self.telegramID=491287865 #telegramID Laura

#ulteriore commento
from gettext import Catalog
# from MyMQTT import *
import time
import socket
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from unicodedata import name
from telepot.loop import MessageLoop
import sys, os
from pprint import pprint
from TelegramBot import SwitchBot

sys.path.insert(0, os.path.abspath('..'))

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

class dataAnalysisClass():

    # MQTT FUNCTIONS

    def __init__(self, clientID, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        timeshift_fn = 'PostProcessing\\timeshift.json'
        self.thresholdsFile = json.load(open(timeshift_fn,'r'))

    def start(self):
        self.client.start()
        self.client.mySubscribe("P4IoT/SmartHealth/+/heartrate")
        self.client.mySubscribe("P4IoT/SmartHealth/+/pressure")
        self.client.mySubscribe("P4IoT/SmartHealth/+/glycemia")
        self.client.mySubscribe("P4IoT/SmartHealth/+/temperature")
    
    def stop(self):
        self.client.stop()
        
    def myPublish(self, topic, message):
        self.client.myPublish(topic, message) 
        print(f"Published on {topic}")
    
    def notify(self, topic, msg):

        print(f"Il topic è: {topic}")
        d = json.loads(msg)
        self.bn = d["bn"]
        self.clientID = int(self.bn.split("/")[3])  
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

        # #print(f"DataAnalysisBlock: clientID : {self.clientID}")
        # dayOne = retrievePregnancyDayOne(int(self.clientID))            
        # #print(f"DataAnalysisBlock: dayOne : {dayOne}")
        # dayoneY = dayOne.split("-")[0]
        # dayoneM = dayOne.split("-")[1]
        # dayoneD = dayOne.split("-")[2]
        # #print(f"dayoneY: {dayoneY}, dayoneM: {dayoneM}, dayoneD: {dayoneD}")
        # dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
        # #print(f"dayoneDays of {self.clientID} is {dayoneDays}")

        # elapsedDays = currDays - dayoneDays
        # week = int(elapsedDays / 7)
        # if(week == 0): 
        #     week = 1

        dayOne = retrievePregnancyDayOne(self.clientID)

        week = getWeek(dayOne)

        #print(f"TEST: week of pregnancy of patient {self.clientID} is {week}, from {dayOne} to {currY}-{currM}-{currD}, {elapsedDays} elapsed days")

        #print(f"DataAnalysisBlock: patient dayOne is {dayOne}")
        #print(f"DataAnalysisBlock: timestamp is {self.timestamp}")
        #print(f"week of pregnancy of patient {self.clientID} is {week}")
    

        if (self.measureType == "heartrate"):
            print(f"DataAnalysisBlock received HEARTRATE measure of: {self.value} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.manageHeartRate(week)
        elif (self.measureType == "pressureHigh"):
            self.sensed_pressureHigh=self.e[0]["v"]
            self.sensed_pressureLow=self.e[1]["v"]
            print(f"DataAnalysisBlock received PRESSURE measure of: {self.sensed_pressureHigh}, {self.sensed_pressureLow} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.managePressure(week)            
        elif (self.measureType == "glycemia"):
            print(f"DataAnalysisBlock received GLYCEMIA measure of: {self.value} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.manageGlycemia(week)
        elif (self.measureType == "temperature"):
            print(f"DataAnalysisBlock received TEMPERATURE measure of: {self.value} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.manageTemperature(week)
        else:
            print("Measure type not recognized")

    def manageHeartRate(self, week):
        thresholdsHR = self.thresholdsFile["heartrate"]
        for rangeHR in thresholdsHR:
            weekmin = rangeHR["weekrange"].split("-")[0]
            weekmax = rangeHR["weekrange"].split("-")[1]   
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeHR["min"]) and int(self.value) <= int(rangeHR["max"])):
                    print(f"DataAnalysisBlock: heart rate is in range")
                else:
                    print(f"DataAnalysisBlock: heart rate is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID, messaggio, "heartrate on", "heartrate off")
                    else:
                        print("Doctor not found for this patient")

    def managePressure(self, week):
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
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, "pression on", "pression off")
                    else:
                        print("Doctor not found for this patient")

    def manageGlycemia(self, week):
        thresholdsGL = self.thresholdsFile["glycemia"]
        for rangeGL in thresholdsGL:
            weekmin = rangeGL["weekrange"].split("-")[0]
            weekmax = rangeGL["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeGL["min"]) and int(self.value) <= int(rangeGL["max"])):
                    print(f"DataAnalysisBlock: glycemia is in range")
                else:
                    print(f"DataAnalysisBlock: glycemia is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, "glycemia on", "glycemia off")
                    else:
                        print("Doctor not found for this patient")

    def manageTemperature(self, week):
        thresholdsTE = self.thresholdsFile["temperature"]
        for rangeTE in thresholdsTE:
            weekmin = rangeTE["weekrange"].split("-")[0]
            weekmax = rangeTE["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeTE["min"]) and int(self.value) <= int(rangeTE["max"])):
                    print(f"DataAnalysisBlock: temperature is in range")
                else:
                    print(f"DataAnalysisBlock: temperature is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID >= 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, "temperature on", "temperature off")
                    else:
                        print("Doctor not found for this patient")

                              

if __name__ == "__main__":
    
    # Settings
    conf_fn = 'CatalogueAndSettings\\settings.json'
    conf=json.load(open(conf_fn))
    brokerIpAddress = conf["brokerIpAddress"]
    brokerPort = conf["brokerPort"]
    mqttTopic = conf["mqttTopic"]
    baseTopic = conf["baseTopic"]
    ipAddressServerRegistrazione = conf["ipAddressServerRegistrazione"]

    if ipAddressServerRegistrazione == "":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipAddressServerRegistrazione = s.getsockname()[0]
        s.close()  


    MQTTpubsub = dataAnalysisClass("rpiSub", brokerIpAddress, brokerPort)
    MQTTpubsub.start()    

    # SwitchBot per connettersi al Bot telegram del dottore e del paziente
    doctortelegramToken = conf["doctortelegramToken"]
    mybot_dr=SwitchBot(doctortelegramToken,
                       brokerIpAddress,
                       brokerPort,
                       mqttTopic,
                       baseTopic,
                       ipAddressServerRegistrazione,
                       MQTTpubsub)
    patientTelegramToken = conf["patientTelegramToken"]
    mybot_pz=SwitchBot(patientTelegramToken,
                       brokerIpAddress,
                       brokerPort,
                       mqttTopic,
                       baseTopic,
                       ipAddressServerRegistrazione,
                       MQTTpubsub)


    while True:
        time.sleep(10)


