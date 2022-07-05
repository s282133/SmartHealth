### Description: MQTT subscriber that processes data from the MQTT broker, evaluating if it is according to thresholds
#se dovesse servire: self.telegramID=491287865 #telegramID Laura

#ulteriore commento
from gettext import Catalog
# from MyMQTT import *
import time
import socket
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from unicodedata import name
from telepot.loop import MessageLoop
import sys, os
from pprint import pprint

sys.path.insert(0, os.path.abspath('..'))

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

class dataAnalysisClass():

    # MQTT FUNCTIONS

    def __init__(self, clientID, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        timeshift_fn = 'PostProcessing\\timeshift.json'
        self.thresholdsFile = json.load(open(timeshift_fn,'r'))

    def start(self):
        self.client.start()
        self.client.mySubscribe("P4IoT/SmartHealth/+/heartrate")
        self.client.mySubscribe("P4IoT/SmartHealth/+/pressure")
        self.client.mySubscribe("P4IoT/SmartHealth/+/glycemia")
        self.client.mySubscribe("P4IoT/SmartHealth/+/temperature")
    
    def stop(self):
        self.client.stop()
        
    def myPublish(self, topic, message):
        self.client.myPublish(topic, message) 
        print(f"Published on {topic}")
    
    def notify(self, topic, msg):

        print(f"Il topic è: {topic}")
        d = json.loads(msg)
        self.bn = d["bn"]
        self.clientID = self.bn.split("/")[3]  
        self.e = d["e"]
        self.measureType = self.e[0]["n"]
        self.unit = self.e[0]["u"]
        self.timestamp = self.e[0]["t"]
        self.value = self.e[0]["v"]

        # currY = self.timestamp.split("-")[0]
        # currM = self.timestamp.split("-")[1]
        # currD_hms = self.timestamp.split("-")[2]
        # currD = currD_hms.split(" ")[0]
        # #print(f"currY: {currY}, currM: {currM}, currD: {currD}")
        # currDays = int(currY)*365 + int(currM)*30 + int(currD)
        # #print(f"DataAnalysisBlock: current day is {currDays}")

        # #print(f"DataAnalysisBlock: clientID : {self.clientID}")
        # dayOne = retrievePregnancyDayOne(int(self.clientID))            
        # #print(f"DataAnalysisBlock: dayOne : {dayOne}")
        # dayoneY = dayOne.split("-")[0]
        # dayoneM = dayOne.split("-")[1]
        # dayoneD = dayOne.split("-")[2]
        # #print(f"dayoneY: {dayoneY}, dayoneM: {dayoneM}, dayoneD: {dayoneD}")
        # dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
        # #print(f"dayoneDays of {self.clientID} is {dayoneDays}")

        # elapsedDays = currDays - dayoneDays
        # week = int(elapsedDays / 7)
        # if(week == 0): 
        #     week = 1

        dayOne = retrievePregnancyDayOne(int(self.clientID))

        week = getWeek(dayOne)

        #print(f"TEST: week of pregnancy of patient {self.clientID} is {week}, from {dayOne} to {currY}-{currM}-{currD}, {elapsedDays} elapsed days")

        #print(f"DataAnalysisBlock: patient dayOne is {dayOne}")
        #print(f"DataAnalysisBlock: timestamp is {self.timestamp}")
        #print(f"week of pregnancy of patient {self.clientID} is {week}")
    

        if (self.measureType == "heartrate"):
            print(f"DataAnalysisBlock received HEARTRATE measure of: {self.value} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.manageHeartRate(week)
        elif (self.measureType == "pressureHigh"):
            self.sensed_pressureHigh=self.e[0]["v"]
            self.sensed_pressureLow=self.e[1]["v"]
            print(f"DataAnalysisBlock received PRESSURE measure of: {self.sensed_pressureHigh}, {self.sensed_pressureLow} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.managePressure(week)            
        elif (self.measureType == "glycemia"):
            print(f"DataAnalysisBlock received GLYCEMIA measure of: {self.value} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.manageGlycemia(week)
        elif (self.measureType == "temperature"):
            print(f"DataAnalysisBlock received TEMPERATURE measure of: {self.value} at time {self.timestamp}, by {self.clientID}, week of pregnancy {week}")
            self.manageTemperature(week)
        else:
            print("Measure type not recognized")

    def manageHeartRate(self, week):
        thresholdsHR = self.thresholdsFile["heartrate"]
        for rangeHR in thresholdsHR:
            weekmin = rangeHR["weekrange"].split("-")[0]
            weekmax = rangeHR["weekrange"].split("-")[1]   
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeHR["min"]) and int(self.value) <= int(rangeHR["max"])):
                    print(f"DataAnalysisBlock: heart rate is in range")
                else:
                    print(f"DataAnalysisBlock: heart rate is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID > 0:
                        mybot_dr.send_alert(self.telegramID, messaggio, "heartrate on", "heartrate off")
                    else:
                        print("Doctor not found for this patient")

    def managePressure(self, week):
        thresholdsPR = self.thresholdsFile["pressure"]
        for rangePR in thresholdsPR:
            weekmin = rangePR["weekrange"].split("-")[0]
            weekmax = rangePR["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                highmax=rangePR["high"]["max"]
                highmin=rangePR["high"]["min"]
                lowmax=rangePR["low"]["max"]
                lowmin=rangePR["low"]["min"]
                if (int(self.sensed_pressureHigh) >= int(highmax) and int(self.sensed_pressureHigh) <= int(highmin)) and  \
                    (int(self.sensed_pressureLow) >= int(lowmax) and int(self.sensed_pressureLow) <= int(lowmin)) :
                    print(f"DataAnalysisBlock: pressure is in range")
                else:
                    print(f"DataAnalysisBlock: pressure is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?"
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID > 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, "pression on", "pression off")
                    else:
                        print("Doctor not found for this patient")

    def manageGlycemia(self, week):
        thresholdsGL = self.thresholdsFile["glycemia"]
        for rangeGL in thresholdsGL:
            weekmin = rangeGL["weekrange"].split("-")[0]
            weekmax = rangeGL["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeGL["min"]) and int(self.value) <= int(rangeGL["max"])):
                    print(f"DataAnalysisBlock: glycemia is in range")
                else:
                    print(f"DataAnalysisBlock: glycemia is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID > 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, "glycemia on", "glycemia off")
                    else:
                        print("Doctor not found for this patient")

    def manageTemperature(self, week):
        thresholdsTE = self.thresholdsFile["temperature"]
        for rangeTE in thresholdsTE:
            weekmin = rangeTE["weekrange"].split("-")[0]
            weekmax = rangeTE["weekrange"].split("-")[1]
            if (int(week) >= int(weekmin) and int(week) <= int(weekmax)):
                if (int(self.value) >= int(rangeTE["min"]) and int(self.value) <= int(rangeTE["max"])):
                    print(f"DataAnalysisBlock: temperature is in range")
                else:
                    print(f"DataAnalysisBlock: temperature is NOT in range") 
                    catalog_fn = 'CatalogueAndSettings\\catalog.json'
                    self.catalog = json.load(open(catalog_fn))
                    self.lista = self.catalog["doctorList"]
                    messaggio = f"Attention, patient {self.clientID} {self.measureType} is NOT in range, the value is: {self.value} {self.unit}. \n What do you want to do?" 
                    self.telegramID = findDoctorTelegramIdFromPatientId(self.clientID)
                    if self.telegramID > 0:
                        mybot_dr.send_alert(self.telegramID,messaggio, "temperature on", "temperature off")
                    else:
                        print("Doctor not found for this patient")



class SwitchBot:
    def __init__(self, token, broker, port, topic):
        self.tokenBot = token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"] # Catalog token
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBot", broker, port, None)
        self.client.start()
        self.topic = topic
        self.previous_message="previous_message"
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
        self.cmd_on=cmd_on
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(telegramID, text=messaggio, reply_markup=keyboard)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            self.bot.sendMessage(chat_ID, text=f"Create a personal doctor account at this link: http://{ipAddressServerRegistrazione}:8080/start?chat_ID={chat_ID}")

        if message == "/registrazione_paziente": 
            self.bot.sendMessage(chat_ID, text=f"Sign in a new patient at this link: http://{ipAddressServerRegistrazione}:8080/registrazione_paziente?chat_ID={chat_ID}")

        if message == "/accesso_dati": 
            self.bot.sendMessage(chat_ID, text='Access to data at this link: ')

    def on_callback_query(self, messaggio):
        query_ID , chat_ID , query_data = telepot.glance(messaggio,flavor='callback_query')
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic, payload)
        if query_data==f"{self.cmd_on}":
            monitoring = "ON"      
        else:
            monitoring = "OFF"

        mes=messaggio["message"]["text"]
        print(mes)
        self.patientID = mes.split(" ")[2]
        print(self.patientID)
        
        top = f"{mqttTopic}/{self.patientID}/monitoring"   
        message =  {"status": monitoring}
        MQTTpubsub.myPublish(top, message)
        print(f"{message}")
        self.bot.sendMessage(chat_ID, text=f"Monitoring {query_data}")
 
    def on_chat_patient_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            self.bot.sendMessage(chat_ID, text="Bot successfully started, send your patientID given you by doctor")
            self.previous_message="/start"
        
        elif  self.previous_message == "/start" and int(message) < 0:
            self.bot.sendMessage(chat_ID, text=f"Your patientID is not possible") 
            self.previous_message="" 
        elif self.previous_message == "/start" and int(message) > 0:
            self.bot.sendMessage(chat_ID, text=f"Your patientID is: {message}")                 
            self.Update_PatientTelegramID(chat_ID,message)
            self.previous_message=""

        elif message == "/help":
            self.bot.sendMessage(chat_ID, text="You can send /start to log in\n You can send /peso toregister your weight\n You can send /survey to complete a survey") 
            self.previous_message="/help"

        elif message == "/survey":
            self.bot.sendMessage(chat_ID, text="You can complete the survey at this link: ")
            self.previous_message="/survey"

        elif message == "/peso": 
            self.bot.sendMessage(chat_ID, text="Please send your weight in kg")
            self.previous_message="/peso"
        
        elif self.previous_message == "/peso":
            
            if(int(message) < 0 or (int(message) > 100)):
                self.bot.sendMessage(chat_ID, text=f"Your weight is not possible")  
            else:
                self.bot.sendMessage(chat_ID, text=f"Your weight is: {message} Kg")
                print (f"Chat ID: {chat_ID}")
                self.patientID = findPatient(chat_ID)
                
                if self.patientID == 0:
                    print("Paziente non trovato")
                    exit
                
                topic=f"{mqttTopic}/{self.patientID}/peso" 
                peso =  {"status": message}
                MQTTpubsub.myPublish(topic, peso)
                print("published")
                self.previous_message=""

    def Update_PatientTelegramID (self,chat_ID, message):
            filename = 'CatalogueAndSettings\\catalog.json'
            f = open(filename)
            self.catalog = json.load(f)
            self.lista = self.catalog["doctorList"]
            for doctorObject in self.lista:
                patientList = doctorObject["patientList"]
                for patientObject in patientList:
                    patientID = patientObject["patientID"]
                    if patientID == int(message):
                        connectedDevice = patientObject["connectedDevice"]
                        connectedDevice["telegramID"]=chat_ID
                        print(f"{chat_ID}")
            with open('CatalogueAndSettings\\catalog.json', "w") as f:
                json.dump(self.catalog, f,indent=2)
    
                              

if __name__ == "__main__":
    
    # Settings
    conf_fn = 'CatalogueAndSettings\\settings.json'
    conf=json.load(open(conf_fn))
    brokerIpAddress = conf["brokerIpAddress"]
    brokerPort = conf["brokerPort"]
    mqttTopic = conf["mqttTopic"]
    baseTopic = conf["baseTopic"]
    ipAddressServerRegistrazione = conf["ipAddressServerRegistrazione"]

    if ipAddressServerRegistrazione == "":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipAddressServerRegistrazione = s.getsockname()[0]
        s.close()  

    # SwitchBot per connettersi al Bot telegram del dottore e del paziente
    doctortelegramToken = conf["doctortelegramToken"]
    mybot_dr=SwitchBot(doctortelegramToken,brokerIpAddress,brokerPort,baseTopic)
    patientTelegramToken = conf["patientTelegramToken"]
    mybot_pz=SwitchBot(patientTelegramToken,brokerIpAddress,brokerPort,baseTopic)

    MQTTpubsub = dataAnalysisClass("rpiSub", brokerIpAddress, brokerPort)
    MQTTpubsub.start()    

    while True:
        time.sleep(10)


