### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds

from MyMQTT import *
import time
import json

class dataAnalysisClass():

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

        # la gestione del peso e del questionario non è inclusa !

        d = json.loads(msg)
        bn = d["bn"]
        sensorName = bn.split("/")[3]           # "bn": "http://example.org/sensor1/"  -> "sensor1"
        e = d["e"]
        measureType = e[0]["n"]
        unit = e[0]["u"]
        timestamp = e[0]["t"]
        value = e[0]["v"]
        #print(f"{sensorName} measured a {measureType} of {value} {unit} at time {timestamp}.\n")
        if (measureType == "heartrate"):
            print(f"DataAnalysisBlock received HEARTRATE measure of: {value} at time {timestamp}")
            self.manageHeartRate(value)
        elif (measureType == "pressure"):
            print(f"DataAnalysisBlock received PRESSURE measure of: {value} at time {timestamp}")
            self.managePressure(value)            
        elif (measureType == "glycemia"):
            print(f"DataAnalysisBlock received GLYCEMIA measure of: {value} at time {timestamp}")
            self.manageGlycemia(value)
        else:
            print("Measure type not recognized")


    def manageHeartRate(self, value):
        # TODO: evaluate heart rate according to thresholds and month of pregnancy
        pass

    def managePressure(self, value):
        # TODO: evaluate pressure according to thresholds and month of pregnancy
        pass

    def manageGlycemia(self, value):
        # TODO: evaluate glycemia according to thresholds and month of pregnancy
        pass



if __name__ == "__main__":
    conf = json.load(open("../CatalogueAndSettings/settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    MQTTpubsub = dataAnalysisClass("rpiSub", "P4IoT/SmartHealth/#", broker, port)

    MQTTpubsub.start()    

    while True:
        time.sleep(1)

    MQTTsubscriber.stop()


