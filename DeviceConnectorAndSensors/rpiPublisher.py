### Description: This script runs on the Raspberry Pi and publishes the data collected from the sensors to the MQTT broker
###              You can regulate the polling period by changing the PERIODO_HR and PERIODO_PRESSURE variables
###              You can add more sensors easily, check the code below

from MyMQTT import *
import time
import json
import paho.mqtt.client as PahoMQTT
import time
from datetime import datetime

from heartrateSensor import heartrateSensorClass
from pressureSensor import pressureSensorClass
from glycemiaSensor import glycemiaSensorClass

# periodo di polling in minuti
POLLING_PERIOD_HR = 5               # chiedo una misurazione ogni 5 minuti
POLLING_PERIOD_PRESSURE = 10        # chiedo una misurazione ogni 10 minuti
POLLING_PERIOD_GLYCEMIA = 20        # chiedo una misurazione ogni 20 minuti

ONE_MINUTE_IN_SEC = 60

class rpiPub():

    # MQTT FUNCTIONS
    def __init__(self, clientID):
        self.clientID = clientID
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect

        self.messageBroker = 'test.mosquitto.org'

    def start (self):
		#manage connection to broker
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()

    def stop (self):
        self._paho_mqtt.loop_stop() 
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
		# publish a message with a certain topic
        self._paho_mqtt.publish(topic, message, 2)

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.messageBroker, rc))


    ##### SENSORS FUNCTIONS #####

    def initSensors(self):
        self.heartrateSensor = heartrateSensorClass()
        self.pressureSensor = pressureSensorClass()
        self.glycemiaSensor = glycemiaSensorClass()

    # HEARTRATE

    def getHRmeasure(self, counter):
        newMeasureHR = self.heartrateSensor.getHR(counter)
        return newMeasureHR

    def publishHR(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # cambiare topic! legarlo all'id paziente
        rpi.myPublish("P4IoT/SmartHealth/heartrate", json.dumps({"bn": "http://example.org/heartrateSensor/", "e": [{"n": "heartrate", "u": "bpm", "t": timeOfMessage, "v": measure}]}))
        print(f"Published {measure} with topic: P4IoT/SmartHealth/heartrate")

    # PRESSURE

    def getPressuremeasure(self, counter):
        newMeasurePressure = self.pressureSensor.getPressure(counter)
        return newMeasurePressure

    def publishPressure(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rpi.myPublish("P4IoT/SmartHealth/pressure", json.dumps({"bn": "http://example.org/pressureSensor/", "e": [{"n": "pressure", "u": "hPa", "t": timeOfMessage, "v": measure}]}))
        print(f"Published {measure} with topic: P4IoT/SmartHealth/pressure")

    # GLYCEMIA

    def getGlycemia(self, counter):
        newMeasureGlycemia = self.glycemiaSensor.getGlycemia(counter)
        return newMeasureGlycemia

    def publishGlycemia(self, measure):
        timeOfMessage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rpi.myPublish("P4IoT/SmartHealth/glycemia", json.dumps({"bn": "http://example.org/glycemiaSensor/", "e": [{"n": "glycemia", "u": "mg/dL", "t": timeOfMessage, "v": measure}]}))
        print(f"Published {measure} with topic: P4IoT/SmartHealth/glycemia")


    # altri sensori possono essere aggiunti qua


if __name__ == "__main__":

    rpi = rpiPub("rpiPub")

    rpi.start()

    rpi.initSensors()
 
    counter = 0
    while True:
        if counter % POLLING_PERIOD_HR == 0:
            newMeasureHR = int(rpi.getHRmeasure(counter))
            rpi.publishHR(newMeasureHR)
        if counter % POLLING_PERIOD_PRESSURE == 0:
            newMeasurePressure = int(rpi.getPressuremeasure(counter))
            rpi.publishPressure(newMeasurePressure)
        if counter % POLLING_PERIOD_GLYCEMIA == 0:
            newMeasureGlycemia = int(rpi.getGlycemia(counter))
            rpi.publishGlycemia(newMeasureGlycemia)
        counter = counter + 1
        time.sleep(ONE_MINUTE_IN_SEC)