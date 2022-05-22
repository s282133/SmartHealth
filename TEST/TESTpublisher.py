# per vedere se il rpi dopo aver ricevuto "monitoring ON" manda dati piu velocemente
from time import sleep
from MyMQTT import MyMQTT

class TESTpub():
    
    # MQTT FUNCTIONS
    def __init__(self, clientID):
        self.client = MyMQTT(clientID, "test.mosquitto.org", 1883, self)
        self.clientID = clientID
        self.messageBroker = "test.mosquitto.org"
        self.monitoring = False
        self.counter = 0
        print(f"{self.clientID} created")
        self.start()
    def start (self):
        self.client.start()

    def stop (self):
        self.client.stop()

    def myPublish(self, topic, message):
        print(f"{self.clientID} publishing {message} to topic: {topic}")
        self.client.myPublish(topic, message)


if __name__ == '__main__':
    
    TEST = TESTpub("TEST")

    topic = "P4IoT/SmartHealth/hardcoded/monitoring"

    measureToBeMonitored = "heartrate"

    monitoring = "OFF"

    while True:
        monitoring = "OFF"
        message = {"measureType": measureToBeMonitored, "status": monitoring}
        TEST.myPublish(topic, message)
        sleep(30)
        monitoring = "ON"
        message = {"measureType": measureToBeMonitored, "status": monitoring}
        TEST.myPublish(topic, message)
        sleep(30)

