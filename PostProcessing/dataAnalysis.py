### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds

from MyMQTT import *
import time
import json


# TODO: extend to publisher MQTT broker

class dataAnalysisClass():

    # MQTT FUNCTIONS

    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic
        self.thresholdsFile = open("timeshift.json", "r")

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
            week = "qualcosa da 0 a 36"
            self.manageHeartRate(value, week)
        elif (measureType == "pressure"):
            print(f"DataAnalysisBlock received PRESSURE measure of: {value} at time {timestamp}")
            week = "qualcosa da 0 a 36"
            self.managePressure(value, week)            
        elif (measureType == "glycemia"):
            print(f"DataAnalysisBlock received GLYCEMIA measure of: {value} at time {timestamp}")
            week = "qualcosa da 0 a 36"
            self.manageGlycemia(value, week)
        else:
            print("Measure type not recognized")

    # per queste funzioni descritte sotto dovremmo anche farci passare la settimana di gravidanza

    def manageHeartRate(self, value, week):
        # TODO: evaluate heart rate according to thresholds due to week of pregnancy
        thresholdsHR = self.thresholdsFile["heartrate"]
        for rangeHR in thresholdsHR:
            weekmin = rangeHR["weekrange"].split("-")[0]
            weekmax = rangeHR["weekrange"].split("-")[1]
            if (week >= weekmin and week <= weekmax):
                if (value >= rangeHR["min"] and value <= rangeHR["max"]):
                    print(f"DataAnalysisBlock: heart rate is in range")
                    # TODO: send message to MQTT broker
                else:
                    print(f"DataAnalysisBlock: heart rate is NOT in range") 
                    # take further action !
                    # TODO: send message to MQTT broker OR TELEGRAM or both

    def managePressure(self, value, week):
        # TODO: evaluate pressure according to thresholds due to week of pregnancy
        thresholdsPR = self.thresholdsFile["pressure"]
        for rangePR in thresholdsPR:
            weekmin = rangePR["weekrange"].split("-")[0]
            weekmax = rangePR["weekrange"].split("-")[1]
            if (week >= weekmin and week <= weekmax):
                if (value >= rangePR["min"] and value <= rangePR["max"]):
                    print(f"DataAnalysisBlock: pressure is in range")
                    # TODO: send message to MQTT broker
                else:
                    print(f"DataAnalysisBlock: pressure is NOT in range") 
                    # take further action !
                    # TODO: send message to MQTT broker OR TELEGRAM or both

    def manageGlycemia(self, value, week):
        # TODO: evaluate glycemia according to thresholds due to week of pregnancy
        thresholdsGL = self.thresholdsFile["glycemia"]
        for rangeGL in thresholdsGL:
            weekmin = rangeGL["weekrange"].split("-")[0]
            weekmax = rangeGL["weekrange"].split("-")[1]
            if (week >= weekmin and week <= weekmax):
                if (value >= rangeGL["min"] and value <= rangeGL["max"]):
                    print(f"DataAnalysisBlock: glycemia is in range")
                    # TODO: send message to MQTT broker
                else:
                    print(f"DataAnalysisBlock: glycemia is NOT in range") 
                    # take further action !
                    # TODO: send message to MQTT broker OR TELEGRAM or both



if __name__ == "__main__":
    conf = json.load(open("../CatalogueAndSettings/settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    MQTTpubsub = dataAnalysisClass("rpiSub", "P4IoT/SmartHealth/#", broker, port)

    MQTTpubsub.start()    

    while True:
        time.sleep(1)

    MQTTsubscriber.stop()


