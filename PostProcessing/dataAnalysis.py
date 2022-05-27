### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds
#se dovesse servire: self.telegramID=491287865 #telegramID Laura

from gettext import Catalog
from MyMQTT import *
import time
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from unicodedata import name
from telepot.loop import MessageLoop
import sys, os
from pprint import pprint

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
        if topic != "P4IoT/SmartHealth/clientID/monitoring" and topic != "P4IoT/SmartHealth/peso":
            d = json.loads(msg)
            self.bn = d["bn"]
            self.clientID = self.bn.split("/")[3]  #splittare stringhe dei topic -> "bn": "http://example.org/sensor1/"  -> "sensor1"
            self.e = d["e"]
            self.measureType = self.e[0]["n"]
            self.unit = self.e[0]["u"]
            self.timestamp = self.e[0]["t"]
            self.value = self.e[0]["v"]

        if (self.measureType == "heartrate"):
            print(f"DataAnalysisBlock received HEARTRATE measure of: {self.value} at time {self.timestamp}")
            week = "35"
            self.manageHeartRate(week)
        elif (self.measureType == "pressureHigh"):
            self.sensed_pressureHigh=self.e[0]["v"]
            self.sensed_pressureLow=self.e[1]["v"]
            print(f"DataAnalysisBlock received PRESSURE measure of: {self.sensed_pressureHigh}, {self.sensed_pressureLow} at time {self.timestamp}")
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
                highmax=rangePR["high"]["max"]
                highmin=rangePR["high"]["min"]
                lowmax=rangePR["low"]["max"]
                lowmin=rangePR["low"]["min"]
                if (int(self.sensed_pressureHigh) >= int(highmax) and int(self.sensed_pressureHigh) <= int(highmin)) and  \
                    (int(self.sensed_pressureLow) >= int(lowmax) and int(self.sensed_pressureLow) <= int(lowmin)) :
                    print(f"DataAnalysisBlock: pressure is in range")
                else:
                    print(f"DataAnalysisBlock: pressure is NOT in range") 
                    catalog_fn = sys.path[0] + '\\CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = self.findDoctor(self.clientID)
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
        self.client = MyMQTT("telegramBot", broker, port, None)
        self.client.start()
        self.topic = topic
        self.previous_message="qualcosa"
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
        print(f"self.tokenBot is {self.tokenBot}")
        if self.tokenBot == "5373152293:AAESoB5LMU3JUunXegFryWk484twuniHinE":
            MessageLoop(self.bot, {'chat': self.on_chat_message,
                                'callback_query': self.on_callback_query}).run_as_thread()
            print(f"token if is {self.tokenBot}")
            
        else:
            MessageLoop(self.bot, {'chat': self.on_chat_patient_message,
                    'callback_query': self.on_callback_query}).run_as_thread()
            print(f"token else is {self.tokenBot}")

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

    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic, payload)
        if query_data=="heartrate on":
            monitoring = "ON"      
        else:
            monitoring = "OFF"
        top = "P4IoT/SmartHealth/clientID/monitoring" 
        message =  {"status": monitoring}
        MQTTpubsub.myPublish(top, message)
        self.bot.sendMessage(chat_ID, text=f"Monitoring {query_data}")
    
    # def on_chat_weight_message(self, msg):
    #     content_type, chat_type, patient_ID= telepot.glance(msg)
    #     self.weight = msg['text']        

 
    def on_chat_patient_message(self, msg):
        content_type, chat_type, patient_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            #self.bot.sendMessage(chat_ID, text="http://192.168.1.125:8080/registrazione") #funziona per il cellulare
            self.bot.sendMessage(patient_ID, text="Bot avviato correttamente, riceverai presto dei promemoria")
   
        if message == "/peso": 
            self.bot.sendMessage(patient_ID, text="Puoi inserire il tuo peso")
            self.previous_message="/peso"
        
        elif  self.previous_message == "/peso":
            if(int(message) < 0 or (int(message) > 100)):
                self.bot.sendMessage(patient_ID, text=f"Il tuo peso è impossibile")  
            else:
                self.bot.sendMessage(patient_ID, text=f"Il tuo peso è: {message} Kg")
                topicc="P4IoT/SmartHealth/peso"
                peso =  {"status": message}
                MQTTpubsub.myPublish(topicc, peso)
                print("published")
                self.previous_message="qualcosa"
            

          
# self.telegramID=491287865 #telegramID Laura                  
# messaggio = "Ricorda di pesarti oggi e di mandare a questo bot il tuo peso in kg scrivendo /pesati e poi il tuo peso, senza lasciare spazi, conserva due cifre dopo la virgola (Esempio: \pesati54)"
# mybot.send_weight(self.telegramID,messaggio)

if __name__ == "__main__":
    
    # Broker e porta
    conf_fn = sys.path[0] + '\\CatalogueAndSettings\\catalog.json'
    conf=json.load(open(conf_fn))
    info = conf["broker"]
    broker = info["IPadress"]
    port = info["port"]
    #topic = conf["mqttTopic"]

    # SwitchBot per connettersi al Bot telegram del dottore
    token = conf["telegramToken"]
    mybot=SwitchBot(token,broker,port,"IoT_project")

    # SwitchBot per connettersi al Bot telegram del paziente
    token_pz = conf["telegramToken"]
    mybot_pz=SwitchBot(token_pz,broker,port,"IoT_project")

    MQTTpubsub = dataAnalysisClass("rpiSub", "P4IoT/SmartHealth/#", broker, port)
    MQTTpubsub.start()    

    while True:
        time.sleep(1)





    # SwitchBot per connettersi al Bot telegram del dottore
    conf_fn = sys.path[0] + '\\CatalogueAndSettings\\settingsDoctorTelegram.json'
    conf=json.load(open(conf_fn))
    token = conf["telegramToken"]
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    topic = conf["mqttTopic"]
    mybot=SwitchBot(token,broker,port,topic)

    # SwitchBot per connettersi al Bot telegram del paziente
    # token="5156513440:AAEpBKPKf2curml2BNurrhGzQTE_kdHF45U" #token Laura 
    conf_pz = sys.path[0] + '\\CatalogueAndSettings\\settingsPatientTelegram.json'
    conf=json.load(open(conf_pz))
    token_pz = conf["telegramToken"]
    broker_pz = conf["brokerIP"]
    port_pz = conf["brokerPort"]
    topic_pz = conf["mqttTopic"]
    mybot_pz=SwitchBot(token_pz,broker_pz,port_pz,topic_pz)

    # dataAnalysis per analizzare le soglie e mandare il messaggio telegram 
    conf_fn2 = sys.path[0] + '\\CatalogueAndSettings\\settingsDoctorTelegram.json' #non ci andrebbe quello del dottore? quindi usiam quello già preso sopra 
    conf = json.load(open(conf_fn2))
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    MQTTpubsub = dataAnalysisClass("rpiSub", "P4IoT/SmartHealth/#", broker, port)
    MQTTpubsub.start()    

    while True:
        time.sleep(1)



