import json
import time
import requests
# import sys
import re
import sys, os
sys.path.insert(0, os.path.abspath('..'))
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *


class statistics():

    # MQTT FUNCTIONS
    def __init__(self, clientID):
        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = clientID
        self.start()

    def start (self):
        self.client_MQTT.start()
                
    def stop (self):
        self.client_MQTT.stop()

    def myPublish(self, topic, message):
        #print(f"{self.clientID} publishing {message} to topic: {topic}")

        self.client_MQTT.myPublish(topic, message)
        
    def RoutineFunction():
        


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
    Statistics=statistics("Weekly_stat")
    mqtt_api = getApiByName(mqtt_service["APIs"],"send_qualcosa") 
    mqtt_topic = mqtt_api["topic"]
    