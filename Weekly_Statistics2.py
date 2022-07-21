import json
import time
from datetime import datetime
import sys,os
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

sys.path.insert(0, os.path.abspath('..'))


class statistics():

    def __init__(self, clientID, mqtt_broker, mqtt_port, mqtt_topic):
        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = clientID
        self.pub_topic = str(mqtt_topic).replace("+", clientID)
        self.start()        # MQTT functions start
        self.initialize()   # settings read by script
        

    def initialize(self):
        self.counter = 0
        with open("settings_weeklyStats2.json", "r") as rp:
            settings_dict = json.load(rp)
            self.message_structure = settings_dict["message_structure"]
            self.event_structure = settings_dict["event_structure"]
            self.list_parameters = settings_dict["parameters"]
            self.names = []
            self.ts_fields = []
            self.local_files = []
            self.units = []
            for parameter in self.list_parameters:
                self.names.append(parameter["name"])
                self.ts_fields.append(parameter["ts_field"])
                self.local_files.append(parameter["local_file"])
                self.units.append(parameter["unit"])

            ### DEBUG
            # print(f"names : {self.names}")
            # print(f"ts_fields : {self.ts_fields}")
            # print(f"local_files : {self.local_files}")
            # print(f"units : {self.units}")
            # print(f"message structure : {self.message_structure}")
            # print(f"event structure : {self.event_structure}")
            
            
                                                


    def start (self):
        self.client_MQTT.start()
                
    def stop (self):
        self.client_MQTT.stop()

    def myPublish(self, topic, message):
        #print(f"{self.clientID} publishing {message} to topic: {topic}")
        self.client_MQTT.myPublish(topic, message)
    



if __name__ == "__main__" :

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

    # crea funzione wrapper per sto casino