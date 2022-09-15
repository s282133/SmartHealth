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

    def __init__(self, clientID, mqtt_broker, mqtt_port, mqtt_base_topic, mqtt_topic_sub, mqtt_topic_pub_info, mqtt_topic_pub_stats):
        self.client_MQTT = MyMQTT(clientID, mqtt_broker, mqtt_port, self)
        self.clientID = clientID

        self.base_topic = mqtt_base_topic
        self.mqtt_topic_sub = mqtt_topic_sub
        self.mqtt_topic_pub_info = mqtt_topic_pub_info
        self.mqtt_topic_pub_stats = mqtt_topic_pub_stats

        self.start()        # MQTT functions start
        self.subscribe()
        self.events = []
        self.parameters_list = []
        self.current_event_parameters = []
        # self.patient_dayOne = http_retrievePregnancyDayOne(self.clientID)
        # print(f"self.patient_dayOne {self.patient_dayOne}")
        # self.patient_name = http_getNameFromClientID(self.clientID)
        # print(f"self.patient_name {self.patient_name}")
        # self.patient_state = http_getMonitoringStateFromClientID(self.clientID)
        # print(f"self.patient_state {self.patient_state}")


# PROVA PER INVIO DATI PERSONALI a nodered

    def get_personal_parameters(self, patientID):
        #ricerca dati dal patient ID
        full_name = http_getNameFromClientID(patientID)
        state = http_getMonitoringStateFromClientID(patientID)
        pregnancy_day_one = http_retrievePregnancyDayOne(patientID)
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


    def create_message(self, events, patientID):
        message = self.message_structure.copy()
        message["bn"] =str(message["bn"]).replace("{{clientID}}", patientID)
        message["e"] = events
        return message


    def notify(self,topic, payload): 
            measure_type = str(str(topic).split("/")[4])
            [field, unit] = self.retrieve_field_and_unit(measure_type)
            patientID = str(str(topic).split("/")[3])
            # print(f"measure type : {measure_type}")
            content = (payload.decode("utf-8")) 
            # print(f"{patientID} 's {measure_type} : \n\n{content}")
            with open(f"{patientID}_stat_weekly_{measure_type}.json", 'w') as wp:
                wp.write(content)
            wp.close()
            with open(f"{patientID}_stat_weekly_{measure_type}.json","r") as f:
                sum = 0
                min = 999
                max = 0
                avg = 0
                invalid = 0
                dict = json.load(f)
                self.patientID = dict["channel"]["name"]
                #print(f"{self.clientID} patientID: {self.patientID}")
                feeds = dict["feeds"]
                if len(feeds) > 0:
                    for feed in feeds:
                        [field, unit] = self.retrieve_field_and_unit(measure_type)
                        # print(f"unit : {unit}, measure_type {measure_type}, patient {patientID}")
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
                    # print("non ancora")
            # qui ci sono tutti!
            if at_least_one_not_present == 0:
                message = self.create_message(self.events, self.patientID)
                # print(message)
                # qua pubblica anche dati personali
                pub_topic_stats1 = str(self.mqtt_topic_pub_stats).replace("{{base_topic}}", self.base_topic)
                pub_topic_stats2 = str(pub_topic_stats1).replace("{{patientID}}", self.patientID)
                pub_topic_stats3 = str(pub_topic_stats2).strip("/{{{{measure}}}}")
           
                full_name = http_getNameFromClientID(patientID)
                state = http_getMonitoringStateFromClientID(patientID)
                pregnancy_day_one = http_retrievePregnancyDayOne(patientID) # 4          

                self.myPublish(pub_topic_stats3, message)
                self.publishPatientInfo(param_patientID=patientID, param_dayOne= pregnancy_day_one, param_patientName= full_name, param_state= state)
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
        sub_topic1 = str(self.mqtt_topic_sub).replace("{{base_topic}}", self.base_topic)
        sub_topic2 = str(sub_topic1).replace("{{patientID}}", "#")
        sub_topic = str(sub_topic2).strip("/{{measure}}")
        self.client_MQTT.mySubscribe(sub_topic)

    def publishPatientInfo(self, param_patientID, param_patientName, param_dayOne, param_state):
        # {{base_topic}}/info/{{patientID}}/{{measure}}
        patientInfo = {
                "full_name": param_patientName,
                "patientID": param_patientID,
                "day_one": param_dayOne,
                "state": param_state
        }

        info_pub_topic1 = str(self.mqtt_topic_pub_info).replace("{{base_topic}}", self.base_topic)
        info_pub_topic2 = str(info_pub_topic1).replace("{{patientID}}/{{measure}}", param_patientID)

        self.myPublish(info_pub_topic2, patientInfo)

if __name__ == "__main__" :

    mqtt_service = http_getServiceByName("MQTT_analysis")
    try:
        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        mqtt_base_topic = mqtt_service["base_topic"]
        
        mqtt_api_sub = get_api_from_service_and_name(mqtt_service,"weeklystats_sub") 
        mqtt_topic_sub = mqtt_api_sub["topic"]

        mqtt_api_pub_info = get_api_from_service_and_name(mqtt_service, "weeklystats_pub_info" )
        mqtt_topic_pub_info = mqtt_api_pub_info["topic"]
        
        mqtt_api_pub_stats = get_api_from_service_and_name(mqtt_service, "weeklystats_pub_stats" )
        mqtt_topic_pub_stats = mqtt_api_pub_stats["topic"]

        Statistics=statistics("WeeklyStatistics", mqtt_broker=mqtt_broker, mqtt_port=mqtt_port, 
        mqtt_base_topic=mqtt_base_topic, mqtt_topic_sub=mqtt_topic_sub, 
        mqtt_topic_pub_info = mqtt_topic_pub_info, mqtt_topic_pub_stats=mqtt_topic_pub_stats)

        while True:
            time.sleep(1)

    except TypeError:
        print("Weekly_Statistics could not be initialized.")