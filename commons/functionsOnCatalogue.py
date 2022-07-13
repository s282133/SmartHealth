import json
import sys, os
import json
sys.path.insert(0, os.path.abspath('..'))
import time
import string


def retrievePregnancyDayOne(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    # dictionaryCatalog=json.load(open(filename,'r'))
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                data= _patients["personalData"] 
                filepointer.close()    
                return data["pregnancyDayOne"]

def retrieveOnlineSince(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                device=_patients["connectedDevice"]
                filepointer.close()
                return device["onlineSince"]

def retrieveTSReadAPIfromClientID(patient_ID):
    filename = '..\\CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                connectedDevice = _patients["connectedDevice"]
                #print(f"connectedDevice: {connectedDevice}")
                thingspeakInfo = connectedDevice["thingspeakInfo"]
                #print(f"thingspeakInfo: {thingspeakInfo}")                
                api_keys = list(thingspeakInfo["apikeys"])
                #print(f"api_keys: {api_keys}")  
                filepointer.close()                 
                return api_keys[1]

def retrieveTSWriteAPIfromClientID(patient_ID):
    filename = '..\\CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                #data= _patients["connectedDevice"]["thingspeakInfo"]["apikeys"][0]
                connectedDevice = _patients["connectedDevice"]
                #print(f"connectedDevice: {connectedDevice}")
                thingspeakInfo = connectedDevice["thingspeakInfo"]
                #print(f"thingspeakInfo: {thingspeakInfo}")                
                api_keys = list(thingspeakInfo["apikeys"])
                #print(f"api_keys: {api_keys}")        
                filepointer.close()          
                return api_keys[0]


def getWeek(dayOne):
    print(f"dayone = {dayOne}")
    currTime = time.strftime("%Y-%m-%d")
    currY = currTime.split("-")[0]
    currM = currTime.split("-")[1]
    currD = currTime.split("-")[2]
    #print(f"currY: {currY}, currM: {currM}, currD: {currD}")
    currDays = int(currY)*365 + int(currM)*30 + int(currD)
    #print(f"DataAnalysisBlock: current day is {currDays}")

    #print(f"DataAnalysisBlock: clientID : {self.clientID}" )      
    #print(f"DataAnalysisBlock: dayOne : {dayOne}")
    dayoneY = str(dayOne).split("-")[0]
    dayoneM = str(dayOne).split("-")[1]
    dayoneD = str(dayOne).split("-")[2]
    #print(f"dayoneY: {dayoneY}, dayoneM: {dayoneM}, dayoneD: {dayoneD}")
    dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
    #print(f"dayoneDays of {self.clientID} is {dayoneDays}")

    elapsedDays = currDays - dayoneDays
    week = int(elapsedDays / 7)
    return week


def findDoctorIDwithtelegramID(doctortelegramID):
    doctorID = -1
    dictionary = json.load(open('..\\CatalogueAndSettings\\ServicesAndResourcesCatalogue.json','r'))
    lista = dictionary["resources"]
    for doctorObject in lista:
        connectedDevice = doctorObject["connectedDevice"]
        telegramID = connectedDevice["telegramID"] 
        if doctortelegramID == telegramID: 
            doctorID = doctorObject["doctorID"] 
            break
    return doctorID


def findPatient(chat_ID):
    filename = '..\\CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    f = open(filename)
    catalog = json.load(f)

    patientID=-1
    lista = catalog["resources"]
    for doctorObject in lista:
        patientList = doctorObject["patientList"]
        for userObject in patientList:
            connectedDevice = userObject["connectedDevice"] 
            telegramID = connectedDevice["telegramID"]
            if  chat_ID == telegramID:
                patientID = userObject["patientID"] 
                break
        if patientID >= 0: 
            break
    return patientID   


def findDoctorTelegramIdFromPatientId(parPatientID):

    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    catalog = json.load(filepointer)

    telegramID = -1
    lista = catalog["resources"]
    for doctorObject in lista:
        patientList = doctorObject["patientList"]
        for userObject in patientList:
            patientID = userObject["patientID"] 
            if  patientID == parPatientID:
                connectedDevice = doctorObject["connectedDevice"]
                telegramID = connectedDevice["telegramID"]
                break
        if telegramID >= 0: 
            break
    return telegramID    


def getServiceByName(parServices,parName):
    first_or_default = next((x for x in parServices if x["service_name"]==parName), None)
    return first_or_default 


def getApiByName(parAPIs,parName):
    first_or_default = next((x for x in parAPIs if x["functionality_name"]==parName), None)
    return first_or_default 


def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    #"topic_temperature": "{{base_topic}}/{{patientID}}/temperature",
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", parPatientID) #parPatient da passare come stringa
    return local_topic


def getNameFromClientID(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                patientName=_patients["patientName"]
                patientSurname=_patients["patientSurname"]
                filepointer.close()
                return f"{patientName} {patientSurname}"


def getMonitoringStateFromClientID(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                monitoring=_patients["monitoring"]
                filepointer.close()
                return monitoring
    


def setMonitorinStatefromClientID(monitoring, patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename)
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                _patients["monitoring"] = monitoring
                filepointer.close()
                with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
                    json.dump(dictionaryCatalog, f, indent=2)
    