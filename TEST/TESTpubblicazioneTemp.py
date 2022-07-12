from commons.MyMQTT import *
import json
import time
# import socket
# import struct
# import fcntl

class sensor_publisher:
    def __init__(self, broker, port):
        self.clientMQTT=MyMQTT("sensor_publisher",broker,port,None)

    def start (self):
        self.clientMQTT.start()

    def stop (self):
        self.clientMQTT.stop()

    def publish(self,topic,message):
        self.clientMQTT.myPublish(topic,message)
	
	
# def getHwAddr(ifname):
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
#     return ':'.join('%02x' % b for b in info[18:24])	


if __name__ == "__main__":
  
    #macaddress = getHwAddr('eth0')
    conf_fn = 'CatalogueAndSettings\\settings.json'
    conf=json.load(open(conf_fn))
    brokerIpAdress = conf["brokerIpAddress"]
    brokerPort = conf["brokerPort"]
    mqttTopic = conf["mqttTopic"]
    baseTopic = conf["baseTopic"]
    ClientID = 2

    myPublisher = sensor_publisher(brokerIpAdress,brokerPort)
    myPublisher.start()

    done=False

    N=0
    while not done:
        N=N+1
        time.sleep(5)
        time_stamp = str(time.ctime(time.time())) #fornisce orario e data con il giusto formato       

        temperature = 20
        #humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)
        
        message = { "bn": "http://example.org/sensor1/", 
                    "e": [
                        { "n": "temperature", "u": "Cel", "t": time_stamp, "v":temperature  }
                        ]
                }
        
        topic = f"{mqtt_base_topic}/{ClientID}/temp_raspberry"
        topic = f"{mqtt_base_topic}/2/temp_raspberry"
        myPublisher.publish(topic,message)
        
        print(N)

    myPublisher.stop()   


