# Il pubblicatore di temperature pubblica sul topic /temp_raspberry 
# delle temperature casuali fornite da un generatore 

from commons.MyMQTT import *
import json
import time
import socket
import struct
import requests
from DeviceConnectorAndSensors.temperatureSensor import temperatureSensorClass

class sensor_publisher:
    def __init__(self, broker, port):
        self.clientMQTT=MyMQTT("sensor_publisher",broker,port,None)

    def start (self):
        self.clientMQTT.start()

    def stop (self):
        self.clientMQTT.stop()

    def publish(self,topic,message):
        self.clientMQTT.myPublish(topic,message)
	

if __name__ == "__main__":
  
    r = requests.get(f'http://192.168.1.125:8080/lista_pazienti')    
    lista_pazienti = r.json()

    conf_fn = 'CatalogueAndSettings\\settings.json'
    conf=json.load(open(conf_fn))
    brokerIpAdress = conf["brokerIpAddress"]
    brokerPort = conf["brokerPort"]
    mqttTopic = conf["mqttTopic"]
    baseTopic = conf["baseTopic"]

    myPublisher = sensor_publisher(brokerIpAdress,brokerPort)
    myPublisher.start()

    done=False

    tempSensor = []
    for patient in lista_pazienti:
        tempSensor.append( temperatureSensorClass() )


    N=0
    Ciclo=0
    while not done:

        k = N % len(lista_pazienti)
        if k == 0:
            Ciclo+=1

        time.sleep(3)
        time_stamp = str(time.ctime(time.time()))        

        # deve venire fuori da un generatore di temperature
        temperature = tempSensor[k].getTemperature(Ciclo)
        
        message = { "bn": "http://example.org/sensor1/", 
                    "e": [
                        { "n": "temperature", "u": "Cel", "t": time_stamp, "v":temperature  }
                        ]
                }
        
        patientID = lista_pazienti[k]
        
        topic = f"{mqttTopic}/{patientID}/temp_raspberry"
        myPublisher.publish(topic,message)
        #print(f"{patientID} published {temperature} with topic: {mqttTopic}/{patientID}/temp_raspberry")

        N=N+1
        #print(N)

    myPublisher.stop()   

