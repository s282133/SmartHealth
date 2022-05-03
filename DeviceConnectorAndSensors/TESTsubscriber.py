from MyMQTT import *
import time
import json
import string

# periodo in minuti
PERIODO_HR = 5
PERIODO_PRESSURE = 15

# DA FARE: mettere funzioni publisher MQTT ma non so se vanno mantenute quelle subscriber

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
        sensorName = bn.split("/")[3]           # "bn": "http://example.org/sensor1/"  -> "sensor1"
        e = d["e"]
        measureType = e[0]["n"]
        unit = e[0]["u"]
        timestamp = e[0]["t"]
        value = e[0]["v"]
        print(f"{sensorName} measured a {measureType} of {value} {unit} at time {timestamp}.\n")


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    MQTTpubsub = rpi("rpiSub", "P4IoT/SmartHealth/#", broker, port)
    
    MQTTpubsub.start()    

    while True:
        time.sleep(1)

    MQTTsubscriber.stop()

