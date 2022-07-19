# from MyMQTT import *
import json
import time
import requests
# import sys
import re
import sys, os
sys.path.insert(0, os.path.abspath('..'))
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *


class Thingspeak():
    def __init__(self,broker,port):
        self.mqttClient=MyMQTT("thingspeak",broker,port,self) 
        self.cont=0
        self.patternWeight = re.compile(r'P4IoT/SmartHealth/.+/peso')
        self.patternMonitoring = re.compile(r'P4IoT/SmartHealth/.+/monitoring')
        self.lastHeartrate=0
        self.lastGlycemia=0
        self.lastPressureLow=0
        self.lastPressureHigh=0
        self.lastPeso=0
        

    def notify(self,topic,payload): 
        message = json.loads(payload) #trasformiamo in json 
        if bool(self.patternWeight.match(str(topic))): 
            self.clientID = int(str(topic).split("/")[2]) 
            api_key = retrieveTSWriteAPIfromClientID(self.clientID) 
            peso=message["status"] 
            print(f"topic del peso: {topic}") 
            #self.lastPeso = peso 
            rp = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.lastHeartrate}&field2={self.lastPressureHigh}&field3={self.lastGlycemia}&field4={self.lastPressureLow}&field5={peso}') 
                

        elif not bool(self.patternMonitoring.match(str(topic))): 
            print(f"topic non del peso: {topic}")
            self.clientID = int(str(topic).split("/")[2])
            api_key = retrieveTSWriteAPIfromClientID(self.clientID) 
            self.newMeasureType = message['e'][0]['n'] 
            
            if(self.newMeasureType == "heartrate"): 
                self.sensed_heartrate = message['e'][0]['v']
                #self.lastHeartrate = self.sensed_heartrate 
                r = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.sensed_heartrate}&field2={self.lastPressureHigh}&field3={self.lastGlycemia}&field4={self.lastPressureLow}&field5={self.lastPeso}') 

            elif(self.newMeasureType == "glycemia"): 
                self.sensed_glycemia = message['e'][0]['v']
                api_key = retrieveTSWriteAPIfromClientID(self.clientID)
                #self.lastGlycemia = self.sensed_glycemia 
                r = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.lastHeartrate}&field2={self.lastPressureHigh}&field3={self.sensed_glycemia}&field4={self.lastPressureLow}&field5={self.lastPeso}') 
                    
            elif(self.newMeasureType == "pressureHigh"):
                api_key = retrieveTSWriteAPIfromClientID(self.clientID)
                self.sensed_pressureHigh= message['e'][0]['v'] 
                self.sensed_pressureLow= message['e'][1]['v'] 
                #self.lastPressureHigh = self.sensed_pressureHigh 
                #self.lastPressureLow = self.sensed_pressureLow 
                r = requests.get(f'http://api.thingspeak.com/update?api_key={api_key}&field1={self.lastHeartrate}&field2={self.sensed_pressureHigh}&field3={self.lastGlycemia}&field4={self.sensed_pressureLow}&field5={self.lastPeso}')
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # message = json.loads(payload) #trasformiamo in json
        # if bool(self.patternWeight.match(str(topic))):
        #     self.clientID = int(str(topic).split("/")[2])
        #     api_key = retrieveTSWriteAPIfromClientID(self.clientID)
        #     peso=message["status"]
        #     print(f"topic del peso: {topic}")
        #     r2 = requests.get(f'https://api.thingspeak.com/update?api_key={api_key}&field5={peso}') 


        # elif not bool(self.patternMonitoring.match(str(topic))): #da cambiare
        #     print(f"topic non del peso: {topic}")
        #     # self.bn=message['bn'] 
        #     # self.clientID = int(str(self.bn).split("/")[3])
        #     self.clientID = int(str(topic).split("/")[2])
        #     api_key = retrieveTSWriteAPIfromClientID(self.clientID)     
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
        self.mqttClient.start() #mi connetto con mosquitto


    def subscribe(self): 
        self.mqttClient.mySubscribe("P4IoT/SmartHealth/+/peso")
        self.mqttClient.mySubscribe("P4IoT/SmartHealth/+/temperature")
        self.mqttClient.mySubscribe("P4IoT/SmartHealth/+/glycemia")
        self.mqttClient.mySubscribe("P4IoT/SmartHealth/+/pressure")
        self.mqttClient.mySubscribe("P4IoT/SmartHealth/+/heartrate")


if __name__=="__main__":
    #mySubscriber=Thingspeak('test.mosquitto.org',1883) #anche questo andrebbe letto dal catalog
    mySubscriber=Thingspeak("broker.hivemq.com",1883) #anche questo andrebbe letto dal catalog
   
    mySubscriber.start()
    mySubscriber.subscribe()


    while True: #per rimanere connesso in attesa delle notifiche 
        time.sleep(1)