import json
import time
from pandas import notnull
import requests
import decimal
# import sys
import re
import sys, os
from jinja2 import Template
sys.path.insert(0, os.path.abspath('..'))
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

ONE_WEEK_IN_SECONDS = 604800

class statistics():

    # MQTT FUNCTIONS
    def __init__(self, clientID, mqtt_broker, mqtt_port, mqtt_topic):

        ###########################################################
        #
        # TOPIC:
        #   {{base_topic}}/+/statistics
        #   
        # MESSAGE FORMAT:
        # {
        #    "parameter" : "heartrate",
        #    "statistics" : 
        #    {
        #        "min" : "...",
        #        "avg" : "...",
        #        "max" : "..."
        #    }   
        # }
        #
        ###########################################################

        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = clientID
        self.pub_topic = str(mqtt_topic).replace("+", clientID)
        self.start()
        self.initialize()
        while True:
            self.counter += 1
            #if self.counter == ONE_WEEK_IN_SECONDS:           
            if self.counter == 10:       # DA METTERE A 'ONE_WEEK_IN_SECONDS'
                statsHR = self.computeStatsHR()
                message = self.messageCreation("heartrate", statsHR)
                # print(f"{message}")
                self.myPublish(self.pub_topic, message)                
                statsGL = self.computeStatsGL()
                message = self.messageCreation("glycemia", statsGL)            
                # print(f"{message}")    
                self.myPublish(self.pub_topic, message)                               
                statsPRH = self.computeStatsPRH()
                message = self.messageCreation("pressure_high", statsPRH)                
                # print(f"{message}")   
                self.myPublish(self.pub_topic, message)                                         
                statsPRL = self.computeStatsPRL()
                message = self.messageCreation("pressure_low", statsPRL)
                # print(f"{message}")            
                self.myPublish(self.pub_topic, message)                                      
                statsTE = self.computeStatsTE()
                message = self.messageCreation("temperature", statsTE)
                # print(f"{message}")     
                self.myPublish(self.pub_topic, message)                              
                statsWE = self.computeStatsWE()
                message = self.messageCreation("weight", statsWE)
                # print(f"{message}")        
                self.myPublish(self.pub_topic, message)                           
                self.counter = 0
            time.sleep(1)

    def initialize(self):
        self.counter = 0
        with open("settings_weeklyStats.json", "r") as rp:
            settings_dict = json.load(rp)
            allfields = settings_dict["fields"]
            allfiles = settings_dict["files"]
            self.hr_field = allfields["heartrate"]
            self.prH_field = allfields["pressureHigh"]
            self.gl_field = allfields["glycemia"]
            self.prL_field = allfields["pressureLow"]
            self.we_field = allfields["weight"]
            self.te_field = allfields["temperature"]
            self.hr_file = allfiles["heartrate"]
            self.prH_file = allfiles["pressureHigh"]
            self.gl_file = allfiles["glycemia"]
            self.prL_file = allfiles["pressureLow"]
            self.we_file = allfiles["weight"]
            self.te_file = allfiles["temperature"]
            self.message_structure = settings_dict["message_structure"]

    def messageCreation(self, parameter, stats):
        message = self.message_structure
        message["parameter"] = parameter
        try:
            message["statistics"]["min"] = list(stats)[0]
        except:
            message["statistics"]["min"] = "none"
        try:
            message["statistics"]["avg"] = list(stats)[1]
        except:
            message["statistics"]["avg"] = "none"
        try:
            message["statistics"]["max"] = list(stats)[2]
        except:
            message["statistics"]["max"] = "none"   
        return message         

    def start (self):
        self.client_MQTT.start()
                
    def stop (self):
        self.client_MQTT.stop()

    def myPublish(self, topic, message):
        print(f"{self.clientID} publishing {message} to topic: {topic}")
        self.client_MQTT.myPublish(topic, message)
    
    def computeStatsHR(self):
        field = f"{self.hr_field}"
        file = f"{self.hr_file}"
        fp = open(file, "r")      
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        parameter = "HEARTRATE"
        return self.iterateOverList(allmeasures, field, parameter)

    def computeStatsPRH(self):
        field = f"{self.prH_field}"
        file = f"{self.prH_file}"
        fp = open(file, "r")  
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        parameter = "PRESSURE_HIGH"
        return self.iterateOverList(allmeasures, field, parameter)

    def computeStatsPRL(self):
        field = f"{self.prL_field}"
        file = f"{self.prL_file}"
        fp = open(file, "r")     
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        parameter = "PRESSURE_LOW"
        return self.iterateOverList(allmeasures, field, parameter)

    def computeStatsGL(self):
        field = f"{self.gl_field}"
        file = f"{self.gl_file}"
        fp = open(file, "r")       
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        parameter = "GLYCEMIA"
        return self.iterateOverList(allmeasures, field, parameter)

    def computeStatsTE(self):
        field = f"{self.te_field}"
        file = f"{self.te_file}"
        fp = open(file, "r")            
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        parameter = "TEMPERATURE"
        return self.iterateOverList(allmeasures, field, parameter)

    def computeStatsWE(self):
        field = f"{self.we_field}"
        file = f"{self.we_file}"
        fp = open(file, "r")            
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        parameter = "WEIGHT"
        return self.iterateOverList(allmeasures, field, parameter)

    def iterateOverList(self, allmeasures, field, parameter):
        avg = 0
        max = 0
        min = 999
        sum = 0
        num_measures = 0
        index = 0
        allstats = []
        discardedElementIndexes = []
        if(len(list(allmeasures)) > 0):
            for entry in allmeasures:
                measure = entry[field]
                try:
                    measure = int(measure)
                    num_measures += 1
                    sum += measure
                    if(measure < min):
                        min = measure
                    if(measure > max):
                        max = measure                
                except:
                    discardedElementIndexes.append(index)
                index += 1
            if(len(discardedElementIndexes) > 0):
                print(f"[{parameter}] Invalid element(s) got discarded at the following position(s) in the JSON file:\n{discardedElementIndexes}")
            if(num_measures > 0):
                avg = sum / num_measures 
                avg = float('%.3f' % round(avg,2))
                allstats = [min,avg,max]
                return allstats   
            else:
                return None         



if __name__ == "__main__":

    resouce_filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    catalog = json.load(open(resouce_filename))
    services = catalog["services"]
    mqtt_service = getServiceByName(services,"Weekly_statistics")
    if mqtt_service == None:
        print("Servizio registrazione non trovato")
    mqtt_broker = mqtt_service["broker"]
    mqtt_port = mqtt_service["port"]
    mqtt_base_topic = mqtt_service["base_topic"]
    mqtt_api = getApiByName(mqtt_service["APIs"],"send_statistics") 
    mqtt_topic = mqtt_api["topic_statistic"]
    #print(f"TOPIC prima: {mqtt_topic}")
    pub_mqtt_topic = str(mqtt_topic).replace("{{base_topic}}", mqtt_base_topic)
    #print(f"TOPIC dopo: {pub_mqtt_topic}")
    Statistics=statistics("WeeklyStat", mqtt_broker=mqtt_broker, mqtt_port=mqtt_port, mqtt_topic= pub_mqtt_topic)