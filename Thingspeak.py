import json
import time
import requests
import re
import sys, os

from commons.customExceptions import ServiceUnavailableException
sys.path.insert(0, os.path.abspath('..'))
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

DOWNLOAD_TIME = 30

class Thingspeak():

    def __init__(self,broker,port):

        mqtt_service = http_getServiceByName("Thingspeak")
        if mqtt_service == None:
            print("Servizio registrazione non trovato")
        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        self.mqtt_base_topic = mqtt_service["base_topic"]
        mqtt_api = get_api_from_service_and_name(mqtt_service,"send_data_to_thingspeak") 

        mqtt_topic_temperature  = mqtt_api["topic_temperature"]
        mqtt_topic_heartrate    = mqtt_api["topic_heartrate"]
        mqtt_topic_pressure     = mqtt_api["topic_pressure"]
        mqtt_topic_glycemia     = mqtt_api["topic_glycemia"]
        mqtt_topic_peso         = mqtt_api["topic_peso"]
        mqtt_topic_monitoring   = mqtt_api["topic_monitoring"]

        self.local_topic_temperature = getTopicByParameters(mqtt_topic_temperature, self.mqtt_base_topic, "+")
        self.local_topic_heartrate   = getTopicByParameters(mqtt_topic_heartrate, self.mqtt_base_topic, "+")
        self.local_topic_pressure    = getTopicByParameters(mqtt_topic_pressure, self.mqtt_base_topic, "+")
        self.local_topic_glycemia    = getTopicByParameters(mqtt_topic_glycemia, self.mqtt_base_topic, "+")
        self.local_topic_peso        = getTopicByParameters(mqtt_topic_peso, self.mqtt_base_topic, "+")
        self.local_topic_monitoring  = getTopicByParameters(mqtt_topic_monitoring, self.mqtt_base_topic, "+")
        
        self.mqttClient=MyMQTT(None, mqtt_broker, mqtt_port, self) 
        self.cont=0
        self.patternWeight = re.compile(r'P4IoT/SmartHealth/.+/peso')
        self.patternMonitoring = re.compile(r'P4IoT/SmartHealth/.+/monitoring')
        self.initializeSlim()
        while True:
            if self.counter == DOWNLOAD_TIME:
                self.counter = 0
                self.downloadData()
            self.counter += 1
            time.sleep(1)
		

    def initializeSlim(self):
        self.start()
        self.subscribe()
        self.counter = 0
        self.lastHeartrate=0
        self.lastGlycemia=0
        self.lastPressureLow=0
        self.lastPressureHigh=0
        self.lastPeso=0
        try:
            with open("settings_weeklyStats.json", "r") as rp:
                settings_dict = json.load(rp)
                self.list_parameters = settings_dict["parameters"]
                self.ts_fields = []
                self.local_files = []                
                for parameter in self.list_parameters:
                    self.ts_fields.append(parameter["ts_field"])
                    self.local_files.append(parameter["local_file"])
        except:
            sys.exit("Errore nella lettura del file settings_weeklyStats.json")


    def downloadData(self):
        for i in range(len(self.list_parameters)):
            field = self.ts_fields[i]
            fieldnumber = int(str(field).strip("field"))
            #print("Downloading data from field " + fieldnumber)
            #downloaded_catalogue = requests.get(f'https://api.thingspeak.com/channels/1721151/fields/{fieldnumber}.json?days=1&min=1')
            downloaded_catalogue = requests.get(f'https://api.thingspeak.com/channels/1721151/fields/{fieldnumber}.json?results=8000&min=1')
            if downloaded_catalogue.status_code == 200:
                with open(self.local_files[i], "w") as wp:
                    json.dump(downloaded_catalogue.json(), wp, indent=4)
            else:
                print("Error. Status code: " + str(downloaded_catalogue.status_code))
                sys.exit()


    def notify(self,topic,payload): 
        message = json.loads(payload) 
        if bool(self.patternWeight.match(str(topic))): 
            self.clientID = int(str(topic).split("/")[2]) 
            api_key = http_retrieveTSWriteAPIfromClientID(self.clientID) 
            peso=message["status"] 
            print(f"topic del peso: {topic}") 
            self.lastPeso = peso 
            rp = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.lastHeartrate}&field2={self.lastPressureHigh}&field3={self.lastGlycemia}&field4={self.lastPressureLow}&field5={peso}') 
                
        elif not bool(self.patternMonitoring.match(str(topic))): 
            print(f"topic non del peso: {topic}")
            self.clientID = int(str(topic).split("/")[2])
            api_key = http_retrieveTSWriteAPIfromClientID(self.clientID) 
            self.newMeasureType = message['e'][0]['n'] 
            
            if(self.newMeasureType == "heartrate"): 
                self.sensed_heartrate = message['e'][0]['v']
                self.lastHeartrate = self.sensed_heartrate 
                r = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.sensed_heartrate}&field2={self.lastPressureHigh}&field3={self.lastGlycemia}&field4={self.lastPressureLow}&field5={self.lastPeso}') 

            elif(self.newMeasureType == "glycemia"): 
                self.sensed_glycemia = message['e'][0]['v']
                api_key = http_retrieveTSWriteAPIfromClientID(self.clientID)
                self.lastGlycemia = self.sensed_glycemia 
                r = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.lastHeartrate}&field2={self.lastPressureHigh}&field3={self.sensed_glycemia}&field4={self.lastPressureLow}&field5={self.lastPeso}') 
                    
            elif(self.newMeasureType == "pressureHigh"):
                api_key = http_retrieveTSWriteAPIfromClientID(self.clientID)
                self.sensed_pressureHigh= message['e'][0]['v'] 
                self.sensed_pressureLow= message['e'][1]['v'] 
                self.lastPressureHigh = self.sensed_pressureHigh 
                self.lastPressureLow = self.sensed_pressureLow 
                r = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.lastHeartrate}&field2={self.sensed_pressureHigh}&field3={self.lastGlycemia}&field4={self.sensed_pressureLow}&field5={self.lastPeso}')
                
        
        # message = json.loads(payload) #trasformiamo in json
        # if bool(self.patternWeight.match(str(topic))):
        #     self.clientID = int(str(topic).split("/")[2])
        #     api_key = http_retrieveTSWriteAPIfromClientID(self.clientID)
        #     peso=message["status"]
        #     print(f"topic del peso: {topic}")
        #     r2 = requests.get(f'https://api.thingspeak.com/update?api_key={api_key}&field5={peso}') 


        # elif not bool(self.patternMonitoring.match(str(topic))): #da cambiare
        #     print(f"topic non del peso: {topic}")
        #     # self.bn=message['bn'] 
        #     # self.clientID = int(str(self.bn).split("/")[3])
        #     self.clientID = int(str(topic).split("/")[2])
        #     api_key = http_retrieveTSWriteAPIfromClientID(self.clientID)     
        #     print(f"Topic is (else){topic}")
        #     self.measureType = message['e'][0]['n']

        #     if self.measureType=="heartrate":
        #         heart_rate=int(message['e'][0]['v'])
        #         r1 = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={heart_rate}')
        #         print(f"Field1: {heart_rate}")

        #     elif message['e'][0]['n']=="glycemia":
        #         glycemia=int(message['e'][0]['v'])
        #         r2=requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field3={glycemia}')
        #         print(f"Field3: {glycemia}")

        #     elif message['e'][0]['n']=="pressureHigh":
        #     #elif message['e'][0]['n']=="pressure": #se lo facciamo usl topic
        #         self.sensed_pressureHigh=message['e'][0]['v']
        #         self.sensed_pressureLow=message['e'][1]['v']
        #         r3 = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field2={self.sensed_pressureHigh}&field4={self.sensed_pressureLow}')
        #         #r4 = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field4={self.sensed_pressureLow}')
        #         #r3 = requests.get(f'https://api.thingspeak.com/update?api_key={api_key}')     
        #         print(f"Field2: {self.sensed_pressureHigh}")
        #         print(f"Field4: {self.sensed_pressureLow}")
                
                
            
    def start(self): 
        self.mqttClient.start() 


    def subscribe(self): 
        self.mqttClient.mySubscribe(self.local_topic_heartrate)
        self.mqttClient.mySubscribe(self.local_topic_temperature)
        self.mqttClient.mySubscribe(self.local_topic_pressure)
        self.mqttClient.mySubscribe(self.local_topic_glycemia)
        self.mqttClient.mySubscribe(self.local_topic_peso)


if __name__=="__main__":
    
    mqtt_service = http_getServiceByName("Thingspeak")
    try:
        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        mySubscriber=Thingspeak(mqtt_broker, mqtt_port) 
    except TypeError:
        print("Thingspeak could not be initialized.")