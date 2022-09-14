import json
import time
from datetime import datetime
import sys,os
from MyMQTT import *
from functionsOnCatalogue import *
from customExceptions import *
DOWNLOAD_TIME = 30

sys.path.insert(0, os.path.abspath('..'))

COUNTER_RESOLUTION = 1
SAMPLING_RESOLUTION = 5

class statistics():

    def __init__(self, clientID, mqtt_broker, mqtt_port, mqtt_topic):
        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = clientID
        self.pub_topic = str(mqtt_topic).replace("+", clientID)
        self.start()        # MQTT functions start
        self.subscribe()
        self.events = []
        self.parameters_list = []
        self.current_event_parameters = []
        self.patient_dayOne = http_retrievePregnancyDayOne(self.clientID)
        print(f"self.patient_dayOne {self.patient_dayOne}")
        self.patient_name = http_getNameFromClientID(self.clientID)
        print(f"self.patient_name {self.patient_name}")
        self.patient_state = http_getMonitoringStateFromClientID(self.clientID)
        print(f"self.patient_state {self.patient_state}")


# PROVA PER INVIO DATI PERSONALI a nodered

    def get_personal_parameters(self, patientID):
        #ricerca dati dal patient ID
        patientNumber = str(patientID).strip("channel")
        full_name = http_getNameFromClientID(patientNumber)
        state = http_getMonitoringStateFromClientID(patientNumber)
        pregnancy_day_one = http_retrievePregnancyDayOne(patientNumber)
        personal_parameters_json = {
            "patientID": patientID,
            "full_name": full_name,
            "day_one": pregnancy_day_one,
            "state": state
        }
        return personal_parameters_json

#FINE PROVA INVIO DATI PERSONALI

    def create_event(self, parameter_name, parameter_unit, min, avg, max):
        event = self.event_structure.copy()         # senza copy non funziona, bah
        event["n"] = parameter_name
        event["t"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event["u"] = parameter_unit
        event["v"] = [min, avg, max]
        return event


    def create_message(self, events):
        message = self.message_structure.copy()
        message["bn"] =str(message["bn"]).replace("{{clientID}}", self.clientID)
        # prima c'era patientID, non so perché
        message["e"] = events
        return message


    def notify(self,topic, payload): 
            measure_type = str(str(topic).split("/")[3])
            # print(f"measure type : {measure_type}")
            content = (payload.decode("utf-8")) 
            # print(f"{measure_type} : \n\n{content}")
            with open(f"stat_weekly_{measure_type}.json", 'w') as wp:
                wp.write(content)
            wp.close()
            with open(f"stat_weekly_{measure_type}.json","r") as f:
                sum = 0
                min = 999
                max = 0
                avg = 0
                invalid = 0
                dict = json.load(f)
                patientID = dict["channel"]["name"]
                #print(f"{self.clientID} patientID: {self.patientID}")
                feeds = dict["feeds"]
                for feed in feeds:
                    [field, unit] = self.retrieve_field_and_unit(measure_type)
                    measure = feed[field]
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
                    avg = float("{0:.2f}".format(avg))
                else:
                    min = None
                    avg = None
                    max = None 
            event = self.create_event(measure_type, unit, min, avg, max)
            self.events.append(event)   
            # for event in self.events:
            #     print(f"{event}\n\n")
            at_least_one_not_present = 0
            self.current_event_parameters.append( event["n"] )
            for parameter_name in self.parameters_list:
                if parameter_name not in self.current_event_parameters:
                    at_least_one_not_present = 1
            # qui ci sono tutti!
            if at_least_one_not_present == 0:
                print("publish!")
                message = self.create_message(self.events)
                print(message)
                # qua pubblica anche dati personali
                self.myPublish(self.pub_topic, message)
                self.publishPatientInfo()
                self.current_event_parameters = []
                self.events = []

    def retrieve_field_and_unit(self, measure_type):
        with open("settings_weeklyStats.json", 'r') as sf:
            dict = json.load(sf)
            parameters = dict["parameters"]
            self.parameters_list = []
            for parameter in parameters:
                self.parameters_list.append(parameter["name"])
            self.message_structure = dict["message_structure"]
            self.event_structure = dict["event_structure"]
            try:
                for parameter in parameters:
                    if(parameter["name"] == measure_type):
                        return [parameter["ts_field"],parameter["unit"]]
                raise genericException
            except:
                print("Field not found.")
                sys.exit(-5)

    def start (self):
        self.client_MQTT.start()


    def stop (self):
        self.client_MQTT.stop()


    def myPublish(self, topic, message):
        print(f"{self.clientID} publishing {message} to topic: {topic}\n\n\n")
        self.client_MQTT.myPublish(topic, message)
    

    def subscribe(self): 
        self.client_MQTT.mySubscribe("P4IoT/statistics_file/#")

    def publishPatientInfo(self):
        patientInfo = {
                "full_name": self.patient_name,
                "patientID": self.clientID,
                "day_one": self.patient_dayOne,
                "state": self.patient_state
        }
        info_pub_topic = self.pub_topic.replace("statistic", "info")
        self.myPublish(info_pub_topic, patientInfo)

if __name__ == "__main__" :

    mqtt_service = http_getServiceByName("Weekly_Statistics")
    try:
        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        mqtt_base_topic = mqtt_service["base_topic"]
        mqtt_api = get_api_from_service_and_name(mqtt_service,"send_statistics") 
        mqtt_topic = mqtt_api["topic_statistic"]
        pub_mqtt_topic = str(mqtt_topic).replace("{{base_topic}}", mqtt_base_topic)
        Statistics=statistics("20", mqtt_broker=mqtt_broker, mqtt_port=mqtt_port, mqtt_topic= pub_mqtt_topic)
        print(f"topic pub hehe: {pub_mqtt_topic}")
        while True:
            time.sleep(1)

    except TypeError:
        print("Weekly_Statistics could not be initialized.")