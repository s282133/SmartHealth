### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds

from MyMQTT import *
import time
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from unicodedata import name
from telepot.loop import MessageLoop


# TODO: extend to publisher MQTT broker

class dataAnalysisClass():

    # MQTT FUNCTIONS

    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic
        self.thresholdsFile = json.load(open("C:\\Users\\Giulia\\Desktop\\Progetto Iot condiviso\\PostProcessing\\timeshift.json",'r'))
        #self.thresholdsFile = json.load(open("..\\PostProcessing\\timeshift.json",'r'))

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    
    def stop(self):
        self.client.stop()
    
    def notify(self, topic, msg):

        # la gestione del peso e del questionario non è inclusa !

        d = json.loads(msg)
        self.bn = d["bn"]
        sensorName = self.bn.split("/")[3]           # "bn": "http://example.org/sensor1/"  -> "sensor1"
        e = d["e"]
        measureType = e[0]["n"]
        unit = e[0]["u"]
        timestamp = e[0]["t"]
        self.value = e[0]["v"]
        #print(f"{sensorName} measured a {measureType} of {self.value} {unit} at time {timestamp}.\n")
        if (measureType == "heartrate"):
            print(f"DataAnalysisBlock received HEARTRATE measure of: {self.value} at time {timestamp}")
            week = "7"
            self.manageHeartRate(week)
        elif (measureType == "pressure"):
            print(f"DataAnalysisBlock received PRESSURE measure of: {self.value} at time {timestamp}")
            week = "qualcosa da 0 a 36"
            self.managePressure(week)            
        elif (measureType == "glycemia"):
            print(f"DataAnalysisBlock received GLYCEMIA measure of: {self.value} at time {timestamp}")
            week = "qualcosa da 0 a 36"
            self.manageGlycemia(week)
        else:
            print("Measure type not recognized")

        # Da capire il passaggio delle variabili tra le classi!
        # clientID = self.bn.split("/")[3]
        # measure = self.value
        # return clientID

    # per queste funzioni descritte sotto dovremmo anche farci passare la settimana di gravidanza

    def manageHeartRate(self, week):
        # TODO: evaluate heart rate according to thresholds due to week of pregnancy
        
        thresholdsHR = self.thresholdsFile["heartrate"]
        for rangeHR in thresholdsHR:
            weekmin = rangeHR["weekrange"].split("-")[0]
            weekmax = rangeHR["weekrange"].split("-")[1]
   
        if (week >= weekmin and week <= weekmax):
            #if (self.value >= rangeHR["min"] and self.value <= rangeHR["max"]):
            if (int(self.value) >= int(rangeHR["min"]) and int(self.value) <= int(rangeHR["max"])):
                print(f"DataAnalysisBlock: heart rate is in range")
                # TODO: send message to MQTT broker
            else:
                print(f"DataAnalysisBlock: heart rate is NOT in range") 
                # take further action !
                # TODO: send message to MQTT broker OR TELEGRAM or both

                # varifica superamento soglia e invio di un messaggio automatico a telegram 
                self.catalog = json.load(open("C:\\Users\\Giulia\\Desktop\\Progetto Iot condiviso\\CatalogueAndSettings\\catalog.json")) 
                #self.catalog = json.load(open("..\\CatalogueAndSettings\\catalog.json"))
                self.lista = self.catalog["doctorList"]
                messaggio_inviato = False
                for doctorObject in self.lista:
                    patientList = doctorObject["patientList"]
                    for userObject in patientList:
                        patientID = userObject["patientID"] 
                        if  "1" == patientID:
                            self.chat_ID = doctorObject["doctorID"]
                            mybot.send_alert(self)
                            messaggio_inviato = True
                            break
                    if messaggio_inviato: 
                        break
                
    def managePressure(self, week):
        # TODO: evaluate pressure according to thresholds due to week of pregnancy
        thresholdsPR = self.thresholdsFile["pressure"]
        for rangePR in thresholdsPR:
            weekmin = rangePR["weekrange"].split("-")[0]
            weekmax = rangePR["weekrange"].split("-")[1]
            if (week >= weekmin and week <= weekmax):
                if (self.value >= rangePR["min"] and self.value <= rangePR["max"]):
                    print(f"DataAnalysisBlock: pressure is in range")
                    # TODO: send message to MQTT broker
                else:
                    print(f"DataAnalysisBlock: pressure is NOT in range") 
                    # take further action !
                    # TODO: send message to MQTT broker OR TELEGRAM or both

    def manageGlycemia(self, week):
        # TODO: evaluate glycemia according to thresholds due to week of pregnancy
        thresholdsGL = self.thresholdsFile["glycemia"]
        for rangeGL in thresholdsGL:
            weekmin = rangeGL["weekrange"].split("-")[0]
            weekmax = rangeGL["weekrange"].split("-")[1]
            if (week >= weekmin and week <= weekmax):
                if (self.value >= rangeGL["min"] and self.value <= rangeGL["max"]):
                    print(f"DataAnalysisBlock: glycemia is in range")
                    # TODO: send message to MQTT broker
                else:
                    print(f"DataAnalysisBlock: glycemia is NOT in range") 
                    # take further action !
                    # TODO: send message to MQTT broker OR TELEGRAM or both

# Classe Bot Telegram
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

    def send_alert(self, MQTTpubsub): 
        chat_ID = 786029508                            # DA AGGIORNARE IN REAL
        #clientID = self.bn.split("/")[3]
        #measure = MQTTpubsub.notify
        clientID = 2
        measure = 1
        buttons = [[InlineKeyboardButton(text=f'MONITORING 🟡', callback_data=f'on'), 
                InlineKeyboardButton(text=f'NOT MONITORING ⚪', callback_data=f'off')]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(chat_ID, text=f'Attention, patient {clientID} heart rate is NOT in range: {measure}. \n What do you want to do?', reply_markup=keyboard)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            #self.bot.sendMessage(chat_ID, text="http://192.168.1.125:8080/registrazione") #funziona per il cellulare
            self.bot.sendMessage(chat_ID, text="Crea un tuo account personale a questo link: http://127.0.0.1:8080/start")

        if message == "/registrazione_paziente": 
            self.bot.sendMessage(chat_ID, text="Registra un nuovo paziente a questo link: http://127.0.0.1:8080/registrazione_paziente")

        if message == "/accesso_dati": 
            self.bot.sendMessage(chat_ID, text='Access to data at this link')

        if message == "/monitora_paziente": 
            self.bot.sendMessage(chat_ID, text='Start monitoring')
        
        # elif message == "/temperature" :
        #     #r = requests.get('http://192.168.1.254:8080/temperature') #funziona per il cellulare
        #     r = requests.get('http://127.0.0.1:8080/temperature') 
        #     j_temp = r.json() 
        #     vett = j_temp['e']
        #     primo = vett[0]
        #     temp = float(primo['v'])
        #     self.bot.sendMessage(chat_ID, text='La temperatura è: '+ str(temp))

    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic, payload)
        self.bot.sendMessage(chat_ID, text=f"Monitoring {query_data}")



if __name__ == "__main__":

    
    # SwitchBot per connettersi al Bot telegram
    conf=json.load(open("C:\\Users\\Giulia\\Desktop\\Progetto Iot condiviso\\CatalogueAndSettings\\settingsTelegram.json"))
    token = conf["telegramToken"]
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    topic = conf["mqttTopic"]
    mybot=SwitchBot(token,broker,port,topic)


    conf = json.load(open("C:\\Users\\Giulia\\Desktop\\Progetto Iot condiviso\\CatalogueAndSettings\\settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    MQTTpubsub = dataAnalysisClass("rpiSub", "P4IoT/SmartHealth/#", broker, port)
    
    MQTTpubsub.start()    

    while True:
        time.sleep(1)

    MQTTsubscriber.stop()


