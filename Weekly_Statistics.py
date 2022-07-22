import json
import time
from datetime import datetime
import sys,os
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

sys.path.insert(0, os.path.abspath('..'))

COUNTER_RESOLUTION = 1
SAMPLING_RESOLUTION = 5

class statistics():

    def __init__(self, clientID, mqtt_broker, mqtt_port, mqtt_topic):
        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = clientID
        self.pub_topic = str(mqtt_topic).replace("+", clientID)
        self.start()        # MQTT functions start
        self.initialize()   # settings read by script
        while True:
            self.counter += 1       
            if self.counter == SAMPLING_RESOLUTION:
                self.counter = 0
                self.events = []
                for parameter_index in range(len(self.list_parameters)):
                    parameter_name = self.names[parameter_index]
                    parameter_ts_field = self.ts_fields[parameter_index]
                    parameter_local_file = self.local_files[parameter_index]
                    parameter_unit = self.units[parameter_index]
                    [min, avg, max] = self.compute_statistics(parameter_ts_field, parameter_local_file)
                    event = self.create_event(parameter_name, parameter_unit, min, avg, max)
                    self.events.append(event)
                message = self.create_message(self.events)
                self.myPublish(self.pub_topic, message)
            time.sleep(COUNTER_RESOLUTION)

    def create_event(self, parameter_name, parameter_unit, min, avg, max):
        event = self.event_structure.copy()         # senza copy non funziona, bah
        event["n"] = parameter_name
        event["t"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event["u"] = parameter_unit
        event["v"] = [min, avg, max]
        return event



    def create_message(self, events):
        message = self.message_structure.copy()
        message["bn"].replace("{{clientID}}", self.clientID)
        message["e"] = events
        return message


    def compute_statistics(self, parameter_ts_field, parameter_local_file):
        try:
            with open(parameter_local_file,"r") as f:
                sum = 0
                min = 999
                max = 0
                avg = 0
                invalid = 0
                dict = json.load(f)
                feeds = dict["feeds"]
                for feed in feeds:
                    measure = feed[parameter_ts_field]
                    try:
                        measure = float(measure)
                        sum += measure
                        if measure < min:
                            min = measure
                        if measure > max:
                            max = measure
                    except:
                        invalid += 1
                if(len(feeds) > 0 and len(feeds) > invalid):
                    avg = sum / (len(feeds) - invalid)
                else:
                    min = None
                    avg = None
                    max = None
                return [min, avg, max]
        except:
            print("Error reading local file of weekly measures.")
            return [None, None, None]

    def initialize(self):
        self.counter = 0
        try:
            with open("settings_weeklyStats.json", "r") as rp:
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
        except:
            print("Error reading settings file.")
            sys.exit(1)

    def start (self):
        self.client_MQTT.start()
                
    def stop (self):
        self.client_MQTT.stop()

    def myPublish(self, topic, message):
        print(f"{self.clientID} publishing {message} to topic: {topic}\n\n\n")
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
    pub_mqtt_topic = str(mqtt_topic).replace("{{base_topic}}", mqtt_base_topic)
    Statistics=statistics("WeeklyStat", mqtt_broker=mqtt_broker, mqtt_port=mqtt_port, mqtt_topic= pub_mqtt_topic)

    # crea funzione wrapper per sto casino