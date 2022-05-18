# SERVER PER LA REGISTRAZIONE DEL PAZIENTE E DEL DOTTORE 
# Il server permette al medico di registrarsi per la prima volta o di inserire un paziente nella sua lista  iscrivendolo

import json                     
import time
import telepot
import cherrypy
from MyMQTT import *
from collections import UserList
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class Registrazione(object):
    exposed=True
    def GET(self,*uri,**params):
        
        # apertura pagina html per registrazione dottore
        if uri[0] == "start": 
            f1 = open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\PageHTML\\doctors.html')   
            fileContent = f1.read()      
            f1.close()
            return fileContent

        # apertura pagina html per registrazione paziente
        if uri[0] == "registrazione_paziente": 
            f2 = open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\PageHTML\\patients.html')   
            fileContent = f2.read()      
            f2.close()
            return fileContent

        # apertura tabella con dati iniziali
        if uri[0] == "tabella": 
            f4 = open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json')   
            self.catalog = json.load(f4)
          
            self.clientID = 1 # DA AGGIORNARE IN REAL TIME

            chat_ID = "786029508"
            self.lista = self.catalog["doctorList"]
            doctor_number = 0
            for doctorObject in self.lista:
                connectedDevice = doctorObject["connectedDevice"]
                telegramID = connectedDevice["telegramID"] 
                if chat_ID == telegramID: 
                    break
                doctor_number += 1
            self.lista = self.catalog["doctorList"][doctor_number] 
            return json.dumps(self.lista) 


    def POST(self,*uri,**params):

        if uri[0] == "doctors": 
 
            # aggiungere un dottore alla lista di dottori
            body = cherrypy.request.body.read() 
            self.record = json.loads(body)

            doctor = {
                "doctorID": 0,
                "doctorName": self.record["doctorName"],
                "doctorSurname": self.record["doctorSurname"],
                "doctorMail": self.record["doctorMail"],
                "lastUpdate": "",
                "connectedDevice": {
                    "telegramID": 0
                },
                "patientList": []
            }

            self.dictionary = json.load(open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json'))
            self.dictionary['doctorList'].append(doctor) 
            with open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json", "w") as f: 
                json.dump(self.dictionary, f, indent=2)  
            return json.dumps(self.dictionary)


        if uri[0] == "patients": 

           # ricerca del giusto dottore tramite telegram ID e chat ID e inserimeno del paziente
            chat_ID = "786029508" # DA AGGIORNARE IN REAL TIME
            body = cherrypy.request.body.read() 
            self.record = json.loads(body) 

            patient = {
                "patientID": 0,
                "patientName": self.record["patientName"],
                "patientSurname": self.record["patientSurname"],
                "personalData": {
                    "taxIDcode": self.record["taxIDcode"],
                    "userEmail": self.record["userEmail"],
                    "pregnancyDayOne": self.record["pregnancyDayOne"]
                },
                "connectedDevice": {
                    "devicesID": "",
                    "mesureType": [
                    "Heart Rate",
                    "Pression",
                    "Temperature",
                    "Glycemia"
                    ],
                    "telegramID": 0,
                    "thingspeakInfo": {
                    "channel": "0",
                    "apikeys": []
                    }
                }
                }

            self.dictionary = json.load(open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json'))
            self.lista = self.dictionary["doctorList"]

            self.LastPatientID = self.dictionary["LastPatientID"]
            self.record["patientID"] = self.LastPatientID + 1
            self.dictionary["LastPatientID"] = self.LastPatientID + 1

            doctor_number = 0
            for doctorObject in self.lista:
                connectedDevice = doctorObject["connectedDevice"]
                telegramID = connectedDevice["telegramID"] 
                if chat_ID == telegramID: 
                    break
                doctor_number += 1
 
            self.dictionary['doctorList'][doctor_number]['patientList'].append(patient)
            with open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json", "w") as f:
                json.dump(self.dictionary, f, indent=2) 
            self.lista = self.dictionary["doctorList"][doctor_number]  
            return json.dumps(self.lista) 

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

# Inviare pagine html per la registrazione al messaggio inviato da un dottore
class EchoBot():
    exposed=True
    def __init__(self, token):
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        self.bot.sendMessage(chat_ID, str(chat_ID))
   

#MAIN
if __name__=="__main__":

    # Server per la registrazione
    cherrypy.tree.mount(Registrazione(),'/')
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }
    cherrypy.tree.mount(Registrazione(),'/',conf)
    cherrypy.config.update(conf)
    cherrypy.engine.start() 
    cherrypy.engine.block() 

    # Telegram per inviare le pagine html per la registrazione
    conf = json.load(open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\settings.json"))
    token = conf["telegramToken"]
    bot=EchoBot(token)
    print("Bot started ...")
    while True:
        time.sleep(3)


