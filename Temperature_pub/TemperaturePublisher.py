# Il pubblicatore di temperature pubblica sul topic /temp_raspberry 
# delle temperature casuali fornite da un generatore 

import json          
import time

from MyMQTT import *
from functionsOnCatalogue import *

from temperatureSensor import temperatureSensorClass

POLLING_PERIOD_TEMPERATURE = 10

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

    try:
        json_lista = http_get_lista_pazienti_simulati()
        lista_pazienti_simulati = json_lista["lista_pazienti_simulati"]
    except:
        print("temperaturePublisher - error [ERR 1]")
        exit(1)

    # Gestione servizi MQTT
    try:
        mqtt_service = http_getServiceByName("MQTT_analysis")
    except:
        print("temperaturePublisher - error [ERR 2]")
        exit(1)
        
    try:
        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        mqtt_base_topic = mqtt_service["base_topic"]
    except TypeError:
        print("Temperature_Publisher could not be initialized [ERR 1].")
    except KeyError:
        print("Temperature_Publisher could not be initialized [ERR 2].")
    except:
        print("Temperature_Publisher could not be initialized [ERR 3].")
    try:
        mqtt_api = get_api_from_service_and_name(mqtt_service,"temp_raspberry") 
        mqtt_topic = mqtt_api["topic"]
    except TypeError:
        print("Temperature_Publisher could not be initialized [ERR 4].")
    except KeyError:
        print("Temperature_Publisher could not be initialized [ERR 5].")
    except:
        print("Temperature_Publisher could not be initialized [ERR 6].")

    myPublisher = sensor_publisher(mqtt_broker,mqtt_port)
    myPublisher.start()

    done=False

    tempSensor = []
    if len(lista_pazienti_simulati)!=0:
        for patient in lista_pazienti_simulati:
            tempSensor.append( temperatureSensorClass() )

        N=0
        Ciclo=0
        while not done:

            #prova
            #if lista_pazienti_simulati == 0:
            #    lista_pazienti_simulati = 1
                
            k = N % len(lista_pazienti_simulati)
            
            if k == 0:
                Ciclo+=1

            time.sleep(POLLING_PERIOD_TEMPERATURE)
            time_stamp = str(time.ctime(time.time()))        

            temperature = tempSensor[k].getTemperature(Ciclo)
            
            message = { "bn": "http://example.org/sensor1/", 
                        "e": [
                            { "n": "temperature", "u": "Cel", "t": time_stamp, "v":temperature  }
                            ]
                    }
            
            patientID = lista_pazienti_simulati[k]
          
            try:
                local_topic = getTopicByParameters(mqtt_topic, mqtt_base_topic, str(patientID))
                myPublisher.publish(local_topic,message)
                print(f"{patientID} published {temperature} with topic: {local_topic}")
                N=N+1
            except:
                print("temperaturePublisher - error [ERR 7]")
                exit(1)

        myPublisher.stop()   

