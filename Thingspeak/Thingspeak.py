from MyMQTT import *
import json
import time
import requests

class Thingspeak():
    def __init__(self,broker,port):
        self.mqttClient=MyMQTT("thingspeak",broker,port,self) 
        self.cont=0
        

    def notify(self,topic,payload): 
        message = json.loads(payload) #trasformiamo in json
        if topic=="P4IoT/SmartHealth/peso":
            peso=message["status"]
            r2 = requests.get(f'https://api.thingspeak.com/update?api_key=FRN2A7XGJHIUSN24&field5={peso}')    
        elif topic!="P4IoT/SmartHealth/clientID/monitoring": #da cambiare    
            print(f"Topic is (else){topic}")
            self.measureType = message['e'][0]['n']
            if self.measureType=="heartrate":
                heart_rate=int(message['e'][0]['v'])
                r1 = requests.get(f'https://api.thingspeak.com/update?api_key=FRN2A7XGJHIUSN24&field1={heart_rate}')
                print(f"Field1: {heart_rate}")
            elif message['e'][0]['n']=="glycemia":
                glycemia=int(message['e'][0]['v'])
                r2=requests.get(f'https://api.thingspeak.com/update?api_key=FRN2A7XGJHIUSN24&field3={glycemia}')
                print(f"Field3: {glycemia}")
            elif message['e'][0]['n']=="pressureHigh":
                self.sensed_pressureHigh=message['e'][0]['v']
                self.sensed_pressureLow=message['e'][1]['v']
                r2 = requests.get(f'https://api.thingspeak.com/update?api_key=FRN2A7XGJHIUSN24&field2={self.sensed_pressureHigh}')
                r3 = requests.get(f'https://api.thingspeak.com/update?api_key=FRN2A7XGJHIUSN24&field4={self.sensed_pressureLow}')     
                print(f"Field2: {self.sensed_pressureHigh}")
                print(f"Field4: {self.sensed_pressureLow}")
                
           
            
                
            
    def start(self): 
        self.mqttClient.start() #mi connetto con mosquitto

    def subscribe(self): 
        self.mqttClient.mySubscribe("P4IoT/SmartHealth/#")


if __name__=="__main__":
    mySubscriber=Thingspeak('test.mosquitto.org',1883) #anche questo andrebbe letto dal catalog
    mySubscriber.start()
    mySubscriber.subscribe()


    while True: #per rimanere connesso in attesa delle notifiche 
        time.sleep(1)