# MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds

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

            mqtt_topic_sub_generic = mqtt_api["topic_sub_generic"]
            self.mqtt_topic_sub_generic = mqtt_topic_sub_generic.replace("{{base_topic}}", self.mqtt_base_topic)
        except:
            print("dataAnalysis - error [ERR 1]")
            exit(1)

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
            self.mqtt_client.mySubscribe(self.mqtt_topic_sub_generic)
        except:
            print("dataAnalysis - error [ERR 6]")
            exit(6)

    def stop(self):
        self.mqtt_client.stop()
        

    def myPublish(self, topic, message):
        self.mqtt_client.myPublish(topic, message) 

    def notify(self, topic, msg):
        d = json.loads(msg)
        self.bn = d["bn"]
        local_clientID = int(self.bn.split("/")[3])  
        self.e = d["e"]
        self.measureType = self.e[0]["n"]
        self.unit = self.e[0]["u"]
        self.timestamp = self.e[0]["t"]
        self.value = self.e[0]["v"]
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
            
        # ricezione misure
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

    # controllo soglia heartrate
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
                    pass
                else:
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"heartrate on {parClientID}", f"heartrate off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 13]")
                        exit(13)

    # controllo soglia pressione
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
                    pass
                else:
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"pression on {parClientID}", f"pression off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 17]")
                        exit(17)

    # controllo soglia glicemia
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
                    pass
                else:
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"glycemia on {parClientID}", f"glycemia off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 20]")
                        exit(20)

    # controllo soglia temperatura
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
                    pass
                else:
                    messaggio = f"Attention, patient {parPatientName} (ID: {parClientID}) {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    try:
                        self.telegramID = http_findDoctorTelegramIdFromPatientId(parClientID)
                        self.send_alert(parClientID, self.telegramID, messaggio, f"temperature on {parClientID}", f"temperature off {parClientID}")
                    except:
                        print("Doctor not found for this patient")
                        print("DataAnalysisBlock - error [ERR 23]")
                        exit(23)

    # pubblica il messaggio di allarme al medico                         
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


