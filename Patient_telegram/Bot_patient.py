from collections import UserList
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
# from MyMQTT import *

import sys, os
sys.path.insert(0, os.path.abspath('..'))
from commons.MyMQTT import *

#creare classe per successivo oggetto cherrypy
class telegram_subscriber():
    def __init__(self,broker,port):
        self.mqttClient=MyMQTT("telegram",broker,port,self) 

    def notify(self,topic,payload): 
        self.messaggio = json.loads(payload)

        self.catalog = json.load(open("C:\\Users\\Giulia\\Desktop\\II ANNO\\IoT\\5\\ES_5\\es2\\catalog.json")) 
        self.lista = self.catalog["usersList"]

        for i in self.lista:
            if i["userName"] == self.messaggio["utente"]:
                self.chat_ID=i["userID"]
                exit

        mybot.bot.sendMessage(self.chat_ID, text=self.messaggio)
        return "Ok, messaggio inviato"

    def start(self): 
        self.mqttClient.start() #mi connetto con mosquitto

    def subscribe(self): 
        self.mqttClient.mySubscribe("MyProject/alert/Giulia/#") #sottoscrive l'argomento e ogni volta che lo sottoscrivi ricevi un paylod, un oggetto che contiene dati


class EchoBot:
    def __init__(self, token):
        # Local token
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)


if __name__ == "__main__":

    #TELEGRAM
    conf=json.load(open("C:\\Users\\Giulia\\Desktop\\II ANNO\\IoT\\5\\ES_5\\es2\\settings.json"))
    token = conf["telegramToken"]

    # Echo bot
    mybot=EchoBot(token)

    # MQTT
    mySubscriber=telegram_subscriber('test.mosquitto.org',1883)
    mySubscriber.start()
    mySubscriber.subscribe()

    print("Bot started ...")
    while True:
        time.sleep(3)

