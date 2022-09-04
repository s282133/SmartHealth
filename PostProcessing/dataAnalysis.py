# MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds
# telegramID Laura = 491287865
# telegramID Giulia = 786029508
# telegramID Antuan = 298694124

import time
import json

from MyMQTT import *
from functionsOnCatalogue import *

from gettext import Catalog
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class dataAnalysisClass():

    def __init__(self):

        # Gestione servizi MQTT
        try:
            mqtt_service = http_getServiceByName("MQTT_analysis")
            mqtt_broker = mqtt_service["broker"]
            mqtt_port = mqtt_service["port"]
            self.mqtt_base_topic = mqtt_service["base_topic"]
            mqtt_api = get_api_from_service_and_name( mqtt_service, "send_measure" )

            mqtt_topic_temperature  = mqtt_api["topic_temperature"]
            mqtt_topic_heartrate    = mqtt_api["topic_heartrate"]
            mqtt_topic_pressure     = mqtt_api["topic_pressure"]
            mqtt_topic_glycemia     = mqtt_api["topic_glycemia"]
        except:
            print("dataAnalysis - error [ERR 1]")
            exit(1)

        try:
            self.local_topic_temperature = getTopicByParameters(mqtt_topic_temperature, self.mqtt_base_topic, "+")
            self.local_topic_heartrate   = getTopicByParameters(mqtt_topic_heartrate, self.mqtt_base_topic, "+")
            self.local_topic_pressure    = getTopicByParameters(mqtt_topic_pressure, self.mqtt_base_topic, "+")
            self.local_topic_glycemia    = getTopicByParameters(mqtt_topic_glycemia, self.mqtt_base_topic, "+")
        except:
            print("dataAnalysis - error [ERR 2]")
            exit(2)

        try:
            mqtt_topic_send_alert = get_api_from_service_and_name(mqtt_service,"send_alert") 

            self.topic_send_alert  = mqtt_topic_send_alert["topic"]

            self.mqtt_client = MyMQTT(None, mqtt_broker, mqtt_port, self)
            timeshift_fn = 'timeshift.json'
        except:
            print("dataAnalysis - error [ERR 3]")
            exit(3)
        
        try:
            self.thresholdsFile = json.load(open(timeshift_fn,'r'))
        except:
            print("dataAnalysis - error [ERR 4]")
            exit(4)


    def start(self):

        try:
            self.mqtt_client.start()
        except:
            print("dataAnalysis - error [ERR 5]")
            exit(5)
        
        try:
            self.mqtt_client.mySubscribe(self.local_topic_temperature)
            self.mqtt_client.mySubscribe(self.local_topic_heartrate)
            self.mqtt_client.mySubscribe(self.local_topic_pressure)
            self.mqtt_client.mySubscribe(self.local_topic_glycemia)
        except:
            print("dataAnalysis - error [ERR 6]")
            exit(6)

    def stop(self):
        self.mqtt_client.stop()
        

    def myPublish(self, topic, message):
        self.mqtt_client.myPublish(topic, message) 
        print(f"Published on {topic}")


    def notify(self, topic, msg):

        print(f"Il topic è: {topic}")
        d = json.loads(msg)
        self.bn = d["bn"]
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
        # dayOne = http_retrievePregnancyDayOne(int(local_clientID))            
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

        try:
            monitoringState = http_getMonitoringStateFromClientID(local_clientID)
            if monitoringState == "on":
                return
        except:
            print("DataAnalysisBlock - error [ERR 7]")
            exit(7)

        try:
            dayOne = http_retrievePregnancyDayOne(local_clientID)
        except:
            print("DataAnalysisBlock - error [ERR 8]")
            exit(8)
        
        try:
            patientName = http_getNameFromClientID(local_clientID)
        except:
            print("DataAnalysisBlock - error [ERR 9]")
            exit(9)
        
        try:
            week = getWeek(dayOne)
        except:
            print("DataAnalysisBlock - error [ERR 10]")
            exit(10)

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
        try:
            thresholdsHR = self.thresholdsFile["heartrate"]
        except:
            print("DataAnalysisBlock - error [ERR 11]")
            exit(11)

        for rangeHR in thresholdsHR:
            try:
                weekmin = rangeHR["weekrange"].split("-")[0]
                weekmax = rangeHR["weekrange"].split("-")[1]   
            except:
                print("DataAnalysisBlock - error [ERR 12]")
                exit(12)
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeHR["min"]) and int(self.value) <= int(rangeHR["max"])):
                    print(f"DataAnalysisBlock: heart rate is in range")
                else:
                    print(f"DataAnalysisBlock: heart rate is NOT in range") 
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"heartrate on {parClientID}", f"heartrate off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 13]")
                        exit(13)


    def managePressure(self, week, parClientID, parPatientName):
        try:
            thresholdsPR = self.thresholdsFile["pressure"]
        except:
            print("DataAnalysisBlock - error [ERR 14]")
            exit(14)
        
        for rangePR in thresholdsPR:
            try:
                weekmin = rangePR["weekrange"].split("-")[0]
                weekmax = rangePR["weekrange"].split("-")[1]
            except:
                print("DataAnalysisBlock - error [ERR 15]")
                exit(15)

            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                try:
                    highmax=rangePR["high"]["max"]
                    highmin=rangePR["high"]["min"]
                    lowmax=rangePR["low"]["max"]
                    lowmin=rangePR["low"]["min"]
                except:
                    print("DataAnalysisBlock - error [ERR 16]")
                    exit(16)

                if (int(self.sensed_pressureHigh) >= int(highmax) and int(self.sensed_pressureHigh) <= int(highmin)) and  \
                    (int(self.sensed_pressureLow) >= int(lowmax) and int(self.sensed_pressureLow) <= int(lowmin)) :
                    print(f"DataAnalysisBlock: pressure is in range")
                else:
                    print(f"DataAnalysisBlock: pressure is NOT in range") 
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"pression on {parClientID}", f"pression off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 17]")
                        exit(17)


    def manageGlycemia(self, week, parClientID, parPatientName):
        try:
            thresholdsGL = self.thresholdsFile["glycemia"]
        except:
            print("DataAnalysisBlock - error [ERR 18]")
            exit(18)

        for rangeGL in thresholdsGL:
            try:
                weekmin = rangeGL["weekrange"].split("-")[0]
                weekmax = rangeGL["weekrange"].split("-")[1]
            except:
                print("DataAnalysisBlock - error [ERR 19]")
                exit(19)

            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeGL["min"]) and int(self.value) <= int(rangeGL["max"])):
                    print(f"DataAnalysisBlock: glycemia is in range")
                else:
                    print(f"DataAnalysisBlock: glycemia is NOT in range") 
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"glycemia on {parClientID}", f"glycemia off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 20]")
                        exit(20)


    def manageTemperature(self, week, parClientID, parPatientName):
        try:
            thresholdsTE = self.thresholdsFile["temperature"]
        except:
            print("DataAnalysisBlock - error [ERR 21]")
            exit(21)

        for rangeTE in thresholdsTE:
            try:
                weekmin = rangeTE["weekrange"].split("-")[0]
                weekmax = rangeTE["weekrange"].split("-")[1]
            except:
                print("DataAnalysisBlock - error [ERR 22]")
                exit(22)
            
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (float(self.value) >= float(rangeTE["min"]) and float(self.value) <= float(rangeTE["max"])):
                    print(f"DataAnalysisBlock: temperature is in range")
                else:
                    print(f"DataAnalysisBlock: temperature is NOT in range") 
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"temperature on {parClientID}", f"temperature off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 23]")
                        exit(23)

                              
    def send_alert(self, parClientID, parTelegramID, parMessagio, parCmdOn, parCmdOff):
        messaggio = {
            "telegramID": parTelegramID,
            "Messaggio": parMessagio,
            "CmdOn": parCmdOn,
            "CmdOff": parCmdOff
        }
        try:
            local_topic_send_alert = getTopicByParameters(self.topic_send_alert, self.mqtt_base_topic, str(parClientID))
            self.mqtt_client.myPublish(local_topic_send_alert, messaggio) 
        except:
            print("DataAnalysisBlock - error [ERR 24]")
            exit(24)


if __name__ == "__main__":
    
    MQTTpubsub = dataAnalysisClass()
    MQTTpubsub.start()   

    while True:
        time.sleep(10)


