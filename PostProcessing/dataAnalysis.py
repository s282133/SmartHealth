### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds

from gettext import Catalog
from MyMQTT import *
import time
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from unicodedata import name
from telepot.loop import MessageLoop
import sys, os
sys.path.insert(0, os.path.abspath('..'))

class dataAnalysisClass():

    # MQTT FUNCTIONS

    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic
        timeshift_fn = sys.path[0] + '\\PostProcessing\\timeshift.json'
        self.thresholdsFile = json.load(open(timeshift_fn,'r'))

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    
    def stop(self):
        self.client.stop()
        
    def myPublish(self, topic, message):
        self.client.myPublish(topic, message) 
        print(f"Published on {topic}")
    
    def notify(self, topic, msg):

        d = json.loads(msg)
        print(str(d))
        self.bn = d["bn"]
        self.clientID = self.bn.split("/")[3]  #splittare stringhe dei topic -> "bn": "http://example.org/sensor1/"  -> "sensor1"
        e = d["e"]
        self.measureType = e[0]["n"]
        self.unit = e[0]["u"]
        self.timestamp = e[0]["t"]
        self.value = e[0]["v"]

        if (self.measureType == "heartrate"):
            print(f"DataAnalysisBlock received HEARTRATE measure of: {self.value} at time {self.timestamp}")
            week = "35"
            self.manageHeartRate(week)
        elif (self.measureType == "pressureHigh")or(self.measureType == "pressureLow"):
            print(f"DataAnalysisBlock received PRESSURE measure of: {self.value} at time {self.timestamp}")
            week = "1"
            self.managePressure(week)            
        elif (self.measureType == "glycemia"):
            print(f"DataAnalysisBlock received GLYCEMIA measure of: {self.value} at time {self.timestamp}")
            week = "1"
            self.manageGlycemia(week)
        else:
            print("Measure type not recognized")



    # Funzioni di varifica del superamento della soglia e invio di un messaggio automatico a telegram 
    # TODO: per queste funzioni descritte sotto dovremmo anche farci passare la SETTIMANA DI GRAVIDANZA

    def manageHeartRate(self, week):
        
        thresholdsHR = self.thresholdsFile["heartrate"]
        for rangeHR in thresholdsHR:
            weekmin = rangeHR["weekrange"].split("-")[0]
            weekmax = rangeHR["weekrange"].split("-")[1]
   
        if (week >= weekmin and week <= weekmax):
            if (int(self.value) >= int(rangeHR["min"]) and int(self.value) <= int(rangeHR["max"])):
                print(f"DataAnalysisBlock: heart rate is in range")
            else:
                print(f"DataAnalysisBlock: heart rate is NOT in range") 
                catalog_fn = sys.path[0] + '\\CatalogueAndSettings\\catalog.json'
                self.catalog = json.load(open(catalog_fn))
                self.lista = self.catalog["doctorList"]
                messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                self.telegramID = self.findDoctor(self.clientID)
                #self.telegramID=491287865 #telegramID Laura
                if self.telegramID > 0:
                    mybot.send_alert(self.telegramID, messaggio, "heartrate on", "heartrate off")
                else:
                    print("Doctor not found for this patient")

    def managePressure(self, week):
        thresholdsPR = self.thresholdsFile["pressure"]
        for rangePR in thresholdsPR:
            weekmin = rangePR["weekrange"].split("-")[0]
            weekmax = rangePR["weekrange"].split("-")[1]
            if (week >= weekmin and week <= weekmax):
                if (int(self.value) >= int(rangePR["min"]) and int(self.value) <= 1):

                    print(f"DataAnalysisBlock: pressure is in range")
                else:
                    print(f"DataAnalysisBlock: pressure is NOT in range") 
                    catalog_fn = sys.path[0] + '\\CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = self.findDoctor(self.clientID)
                    #self.telegramID=491287865 #telegramID Laura
                    if self.telegramID > 0:
                        mybot.send_alert(self.telegramID,messaggio, "pression on", "pression off")
                    else:
                        print("Doctor not found for this patient")

    def manageGlycemia(self, week):
        thresholdsGL = self.thresholdsFile["glycemia"]
        for rangeGL in thresholdsGL:
            weekmin = rangeGL["weekrange"].split("-")[0]
            weekmax = rangeGL["weekrange"].split("-")[1]
            if (week >= weekmin and week <= weekmax):
                if (int(self.value) >= int(rangeGL["min"]) and int(self.value) <= int(rangeGL["max"])):
                    print(f"DataAnalysisBlock: glycemia is in range")
                else:
                    print(f"DataAnalysisBlock: glycemia is NOT in range") 
                    catalog_fn = sys.path[0] + '\\CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    self.telegramID = self.findDoctor(self.clientID)
                    #self.telegramID=491287865 #telegramID Laura
                    if self.telegramID > 0:
                        mybot.send_alert(self.telegramID,messaggio, "glycemia on", "glycemia off")
                    else:
                        print("Doctor not found for this patient")

    def findDoctor(self, patientID):
        telegramID = 0
        for doctorObject in self.lista:
            patientList = doctorObject["patientList"]
            for userObject in patientList:
                patientID = userObject["patientID"] 
                if  patientID == patientID:
                    connectedDevice = userObject["connectedDevice"]
                    telegramID = connectedDevice["telegramID"]
                    break
            if telegramID > 0: 
                break
        return telegramID    



class SwitchBot:
    def __init__(self, token, broker, port, topic):
        self.tokenBot = token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"] # Catalog token
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBotOrlando", broker, port, None)
        self.client.start()
        self.topic = topic
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()

    def send_alert(self,telegramID,messaggio,cmd_on,cmd_off): 
        buttons = [[InlineKeyboardButton(text=f'MONITORING 🟡',    callback_data=cmd_on), 
                   InlineKeyboardButton(text=f'NOT MONITORING ⚪', callback_data=cmd_off)]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(telegramID, text=messaggio, reply_markup=keyboard)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            #self.bot.sendMessage(chat_ID, text="http://192.168.1.125:8080/registrazione") #funziona per il cellulare
            self.bot.sendMessage(chat_ID, text=f"Crea un tuo account personale a questo link: http://127.0.0.1:8080/start?chat_ID={chat_ID}")

        if message == "/registrazione_paziente": 
            self.bot.sendMessage(chat_ID, text=f"Registra un nuovo paziente a questo link: http://127.0.0.1:8080/registrazione_paziente?chat_ID={chat_ID}")

        if message == "/accesso_dati": 
            self.bot.sendMessage(chat_ID, text='Access to data at this link')

        if message == "/monitora_paziente": 
            self.bot.sendMessage(chat_ID, text='Start monitoring')

    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic, payload)
        #if query_data=="on":
        MQTTpubsub.myPublish("P4IoT/SmartHealth/clientID/+/monitoring", "on")
        self.bot.sendMessage(chat_ID, text=f"Monitoring {query_data}")
        



if __name__ == "__main__":
    
    # SwitchBot per connettersi al Bot telegram
    conf_fn = sys.path[0] + '\\CatalogueAndSettings\\settingsTelegram.json'
    conf=json.load(open(conf_fn))
    
    token = conf["telegramToken"]
    #token="5156513440:AAEpBKPKf2curml2BNurrhGzQTE_kdHF45U" #token Laura 
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    topic = conf["mqttTopic"]
    mybot=SwitchBot(token,broker,port,topic)

    # dataAnalysis per analizzare le soglie e mandare il messaggio telegram
    conf_fn2 = sys.path[0] + '\\CatalogueAndSettings\\settings.json'
    conf = json.load(open(conf_fn2))
    broker = conf["broker"]
    port = conf["port"]
    MQTTpubsub = dataAnalysisClass("rpiSub", "P4IoT/SmartHealth/#", broker, port)
    MQTTpubsub.start()    

    while True:
        time.sleep(1)



