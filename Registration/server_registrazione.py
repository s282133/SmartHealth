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
import sys, os
sys.path.insert(0, os.path.abspath('..'))

from PageHTML import *

class Registrazione(object):
    exposed=True
    def GET(self,*uri,**params):
        
        # apertura pagina html per registrazione dottore
        if uri[0] == "start": 
            self.telegramID = params["chat_ID"]
            #f1 = open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\PageHTML\\doctors.html')   
            filename = sys.path[0] + '\\PageHTML\\doctors.html'
            f1 = open(filename)
            fileContent = f1.read()      
            f1.close()
            return fileContent

        # apertura pagina html per registrazione paziente
        if uri[0] == "registrazione_paziente": 
            self.doctortelegramID = params["chat_ID"]
            #f2 = open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\PageHTML\\patients.html')   
            filename = sys.path[0] + '\\PageHTML\\patients.html'
            f2 = open(filename)
            fileContent = f2.read()      
            f2.close()
            return fileContent

        # apertura tabella con dati iniziali
        if uri[0] == "tabella": 

            # anto commented here
            # cur_path = os.path.dirname(__file__)
            # new_path = os.path.relpath('..\\CatalogueAndSettings\\catalog.json', cur_path)
            # f4 = open(new_path,'catalog.json')
            # self.catalog = json.load(f4)
            # end comment
            filename = sys.path[0] + '\\CatalogueAndSettings\\catalog.json'
            f4 = open(filename)
            self.catalog = json.load(f4)
        
            # f4 = open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json')   
            # self.catalog = json.load(f4)
          
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

    # aggiungere un dottore alla lista di dottori al SUBMIT
    def POST(self,*uri,**params):

        if uri[0] == "doctors": 
            
            # 1))) prendere informazioni inserite 
            body = cherrypy.request.body.read() 
            self.record = json.loads(body)

            # 2))) formare la struttura per il catalogo
            doctor = {
                "doctorID": 0,
                "doctorName": self.record["doctorName"],
                "doctorSurname": self.record["doctorSurname"],
                "doctorMail": self.record["doctorMail"],
                "lastUpdate": "",
                "connectedDevice": {
                    "telegramID": self.telegramID
                },
                "patientList": []
            }

            # 3))) apro il catalogo
            #self.dictionary = json.load(open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json'))
            self.dictionary = json.load(open(sys.path[0] + '\\CatalogueAndSettings\\catalog.json'))

            # 4))) inserisco ID del dottore
            self.LastDoctorID = self.dictionary["LastDoctorID"]
            doctor["doctorID"] = self.LastDoctorID + 1
            self.dictionary["LastDoctorID"] = self.LastDoctorID + 1

            # 5))) inserisco il dottore nella lista
            self.dictionary['doctorList'].append(doctor) 

            # 6))) salvo il catalogo aggiornato
            #with open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json", "w") as f: 
            with open(sys.path[0] + '\\CatalogueAndSettings\\catalog.json', "w") as f:
                json.dump(self.dictionary, f, indent=2)
            return json.dumps(self.dictionary)


        if uri[0] == "patients": 

            # ricerca del giusto dottore tramite telegram ID e chat ID e inserimeno del paziente
            #chat_ID = "786029508" # DA AGGIORNARE IN REAL TIME
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
                    "devicesID": self.record["devicesID"],
                    "mesureType": [
                    "Heart Rate",
                    "Pression",
                    "Temperature",
                    "Glycemia"
                    ],
                    "telegramID": 0,
                    "thingspeakInfo": {
                    "channel": 0,
                    "apikeys": []
                    }
                }
                }

            self.dictionary = json.load(open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json'))
            #self.dictionary = json.load(open(sys.path[0] + '\\CatalogueAndSettings\\catalog.json'))

            self.LastPatientID = self.dictionary["LastPatientID"]
            patient["patientID"] = self.LastPatientID + 1
            self.dictionary["LastPatientID"] = self.LastPatientID + 1

            #da cambiare in una ricerca in base al patient ID (il chat id non ce l'ho prima dell'iscrizione del paziente dal suo telefono)
            # doctor_number = 0
            # self.lista = self.dictionary["doctorList"]
            # for doctorObject in self.lista:
            #     connectedDevice = doctorObject["connectedDevice"]
            #     telegramID = connectedDevice["telegramID"] 
            #     if chat_ID == telegramID: 
            #         break
            #     doctor_number += 1
            
            doctor_number = self.findDoctorwithpatientID(self.doctortelegramID)
            self.dictionary['doctorList'][doctor_number]['patientList'].append(patient)
            with open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json", "w") as f:
            #with open(sys.path[0] + '\\CatalogueAndSettings\\catalog.json', "w") as f:
                json.dump(self.dictionary, f, indent=2)
            self.lista = self.dictionary["doctorList"][doctor_number]  
            return json.dumps(self.lista) 

    # def findDoctor(self, patientID):
    #     telegramID = 0
    #     for doctorObject in self.lista:
    #         patientList = doctorObject["patientList"]
    #         for userObject in patientList:
    #             patientID = userObject["patientID"] 
    #             if  patientID == patientID:
    #                 connectedDevice = userObject["connectedDevice"]
    #                 telegramID = connectedDevice["telegramID"]
    #                 break
    #         if telegramID > 0: 
    #             break
    #     return telegramID    

    def findDoctorwithpatientID(self, doctortelegramID):
        doctor_number = 0
        self.lista = self.dictionary["doctorList"]
        for doctorObject in self.lista:
            connectedDevice = doctorObject["connectedDevice"]
            telegramID = connectedDevice["telegramID"] 
            if doctortelegramID == telegramID: 
                break
            doctor_number += 1
        return doctor_number


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
    #conf = json.load(open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\settings.json"))
    
    # anto commented here
    # cur_path = os.path.dirname(__file__)
    # new_path = os.path.relpath('..\\CatalogueAndSettings\\settings.json', cur_path)
    # conf = json.load(open(new_path,'settings.json'))
    # end comment

    conf_file = sys.path[0] + '\\CatalogueAndSettings\\settings.json'
    conf = json.load(open(conf_file))
    token = conf["telegramToken"]
    bot=EchoBot(token)
    print("Bot started ...")
    while True:
        time.sleep(3)


