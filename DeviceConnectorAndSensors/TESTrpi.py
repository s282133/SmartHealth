import sys,os
sys.path.insert(0, os.path.abspath('..'))

from DeviceConnectorAndSensors.rpiPublisher import *
from DeviceConnectorAndSensors.heartrateSensor import *
from DeviceConnectorAndSensors.pressureSensor import *
from DeviceConnectorAndSensors.glycemiaSensor import *
from DeviceConnectorAndSensors.MyMQTT import *

rpi= rpiPub("hardcoded")