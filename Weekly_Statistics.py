import json
import time
import requests
import decimal
# import sys
import re
import sys, os
sys.path.insert(0, os.path.abspath('..'))
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

ONE_WEEK_IN_SECONDS = 604800

class statistics():

    # MQTT FUNCTIONS
    def __init__(self, clientID, mqtt_broker, mqtt_port):
        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = clientID
        self.start()
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
        while True:
            self.counter += 1
            #if self.counter == ONE_WEEK_IN_SECONDS:
            print(f"counter : {self.counter}")
            if self.counter == 5:
                statsHR = self.computeStatsHR()
                # self.myPublish("sometopicHR", "somemessagewithstatsHR")
                statsGL = self.computeStatsGL()
                # self.myPublish("sometopicGL", "somemessagewithstatsGL")                
                statsPRH = self.computeStatsPRH()
                # self.myPublish("sometopicPRH", "somemessagewithstatsPRH")                
                statsPRL = self.computeStatsPRL()
                # self.myPublish("sometopicPRL", "somemessagewithstatsPRL")                
                statsTE = self.computeStatsTE()
                # self.myPublish("sometopicTE", "somemessagewithstatsTE") 
                statsWE = self.computeStatsWE()
                # self.myPublish("sometopicWE", "somemessagewithstatsWE")
                print(f"statsHR : {statsHR}")
                print(f"statsPRH : {statsPRH}")
                print(f"statsPRL : {statsPRL}")
                self.counter = 0
            time.sleep(1)

    def start (self):
        self.client_MQTT.start()
                
    def stop (self):
        self.client_MQTT.stop()

    def myPublish(self, topic, message):
        #print(f"{self.clientID} publishing {message} to topic: {topic}")
        self.client_MQTT.myPublish(topic, message)
    
    def computeStatsHR(self):
        avg = 0
        max = 0
        min = 200
        sum = 0
        num_measures = 0
        allstats = []
        field = f"{self.hr_field}"
        file = f"{self.hr_file}"
        fp = open(file, "r")      
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        if(len(list(allmeasures)) > 0):
            for entry in allmeasures:
                measure = int(entry[field])
                num_measures += 1
                sum += measure
                if(measure < min):
                    min = measure
                if(measure > max):
                    max = measure
            avg = sum / num_measures 
            avg = float('%.3f' % round(avg,2))
            allstats = [min,avg,max]
            return allstats
        return None

    def computeStatsPRH(self):
        avg = 0
        max = 0
        min = 200
        sum = 0
        num_measures = 0
        allstats = []
        field = f"{self.prH_field}"
        file = f"{self.prH_file}"
        fp = open(file, "r")  
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        if(len(list(allmeasures)) > 0):
            for entry in allmeasures:
                measure = int(entry[field])
                num_measures += 1
                sum += measure
                if(measure < min):
                    min = measure
                if(measure > max):
                    max = measure
            avg = sum / num_measures 
            avg = float('%.3f' % round(avg,2))
            allstats = [min,avg,max]
            return allstats
        return None

    def computeStatsPRL(self):
        avg = 0
        max = 0
        min = 200
        sum = 0
        num_measures = 0
        allstats = []
        field = f"{self.prL_field}"
        file = f"{self.prL_file}"
        fp = open(file, "r")     
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        if(len(list(allmeasures)) > 0):
            for entry in allmeasures:
                measure = int(entry[field])
                num_measures += 1
                sum += measure
                if(measure < min):
                    min = measure
                if(measure > max):
                    max = measure
            avg = sum / num_measures 
            avg = float('%.3f' % round(avg,2))
            allstats = [min,avg,max]
            return allstats
        return None

    def computeStatsGL(self):
        avg = 0
        max = 0
        min = 200
        sum = 0
        num_measures = 0
        allstats = []
        field = f"{self.gl_field}"
        file = f"{self.gl_file}"
        fp = open(file, "r")       
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        if(len(list(allmeasures)) > 0):
            for entry in allmeasures:
                measure = int(entry[field])
                num_measures += 1
                sum += measure
                if(measure < min):
                    min = measure
                if(measure > max):
                    max = measure
            avg = sum / num_measures 
            avg = float('%.3f' % round(avg,2))
            allstats = [min,avg,max]
            return allstats
        return None

    def computeStatsTE(self):
        avg = 0
        max = 0
        min = 200
        sum = 0
        num_measures = 0
        allstats = []
        field = f"{self.te_field}"
        file = f"{self.te_file}"
        fp = open(file, "r")            
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        if(len(list(allmeasures)) > 0):
            for entry in allmeasures:
                measure = int(entry[field])
                num_measures += 1
                sum += measure
                if(measure < min):
                    min = measure
                if(measure > max):
                    max = measure
            avg = sum / num_measures 
            avg = float('%.3f' % round(avg,2))
            allstats = [min,avg,max]
            return allstats
        return None          

    def computeStatsWE(self):
        avg = 0
        max = 0
        min = 200
        sum = 0
        num_measures = 0
        allstats = []
        field = f"{self.we_field}"
        file = f"{self.we_file}"
        fp = open(file, "r")            
        dict = json.load(fp)
        allmeasures = dict["feeds"]
        if(len(list(allmeasures)) > 0):
            for entry in allmeasures:
                measure = int(entry[field])
                num_measures += 1
                sum += measure
                if(measure < min):
                    min = measure
                if(measure > max):
                    max = measure
            avg = sum / num_measures 
            avg = float('%.3f' % round(avg,2))
            allstats = [min,avg,max]
            return allstats
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
    Statistics=statistics("WeeklyStat", mqtt_broker=mqtt_broker, mqtt_port=mqtt_port)