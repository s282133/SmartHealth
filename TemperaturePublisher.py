# Il pubblicatore di temperature pubblica sul topic /temp_raspberry 
# delle temperature casuali fornite da un generatore 

import json
import time

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

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

    # Lista pazienti con raspberry simulati per l'invio delle temperature
    resouce_filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    catalog = json.load(open(resouce_filename))
    lista_pazienti_simulati = []
    lista = catalog["resources"]
    for doctorObject in lista:
        patientList = doctorObject["patientList"]
        for patientObject in patientList:
            patientID = patientObject["patientID"]
            idRegistratoSuRaspberry = patientObject["idRegistratoSuRaspberry"]
            if idRegistratoSuRaspberry == "no":
                lista_pazienti_simulati.append(patientID)

    # Gestione servizi MQTT
    services = catalog["services"]
    mqtt_service = getServiceByName(services,"MQTT_analysis")
    if mqtt_service == None:
        print("Servizio registrazione non trovato")
    mqtt_broker = mqtt_service["broker"]
    mqtt_port = mqtt_service["port"]
    mqtt_base_topic = mqtt_service["base_topic"]
    mqtt_api = getApiByName(mqtt_service["APIs"],"send_temperature") 
    mqtt_topic = mqtt_api["topic"]

    myPublisher = sensor_publisher(mqtt_broker,mqtt_port)
    myPublisher.start()

    done=False

    tempSensor = []
    for patient in lista_pazienti_simulati:
        tempSensor.append( temperatureSensorClass() )

    N=0
    Ciclo=0
    while not done:

        k = N % len(lista_pazienti_simulati)
        if k == 0:
            Ciclo+=1

        time.sleep(3)
        time_stamp = str(time.ctime(time.time()))        

        temperature = tempSensor[k].getTemperature(Ciclo)
        
        message = { "bn": "http://example.org/sensor1/", 
                    "e": [
                        { "n": "temperature", "u": "Cel", "t": time_stamp, "v":temperature  }
                        ]
                }
        
        patientID = lista_pazienti_simulati[k]
        
        local_topic = getTopicByParameters(mqtt_topic, mqtt_base_topic, str(patientID))

        myPublisher.publish(local_topic,message)
        print(f"{patientID} published {temperature} with topic: {local_topic}")

        N=N+1

    myPublisher.stop()   

