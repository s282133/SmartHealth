from MyMQTT import *
import time
import json
import string

class rpi():

    # MQTT FUNCTIONS

    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    
    def stop(self):
        self.client.stop()
    
    def notify(self, topic, msg):   
        d = json.loads(msg)
        bn = d["bn"]
        sensorName = bn.split("/")[3] + "/" + bn.split("/")[4]           # "bn": "http://example.org/clientID/sensor1/"  -> "clientID/sensor1"
        e = d["e"]
        measureType = e[0]["n"]
        unit = e[0]["u"]
        timestamp = e[0]["t"]
        value = e[0]["v"]
        print(f"{sensorName} measured a {measureType} of {value} {unit} at time {timestamp}.\n")


if __name__ == "__main__":
    conf = json.load(open("../CatalogueAndSettings/settings.json"))
    broker = conf["broker"]
    port = conf["port"]

    # topic : P4IoT/SmartHealth/#  =>  tutti i sensori di tutti i client
    # topic : P4IoT/SmartHealth/clientID/#  =>  tutti i sensori di un client specifico
    # topic : P4IoT/SmartHealth/clientID/sensor1 =>  un sensore specifico di un client specifico
    # topic : P4IoT/SmartHealth/+/sensor1 => il sensore1 (ex: heartrate) di tutti i client
    
    # TEST 1
    MQTTpubsub = rpi("rpiSub", "P4IoT/SmartHealth/#", broker, port)
    # questo test sarebbe per piu client ma ad oggi ne abbiamo solo una istanza

    # TEST 2
    # MQTTpubsub = rpi("rpiSub", "P4IoT/SmartHealth/+/heartrate", broker, port)

    # TEST 3
    # MQTTpubsub = rpi("rpiSub", "P4IoT/SmartHealth/+/glycemia", broker, port)

    # TEST 4
    MQTTpubsub = rpi("rpiSub", "P4IoT/SmartHealth/+/pressure", broker, port)

    MQTTpubsub.start()    

    while True:
        time.sleep(1)

    MQTTsubscriber.stop()

