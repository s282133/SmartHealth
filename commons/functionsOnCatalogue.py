import json
import sys, os
import json
sys.path.insert(0, os.path.abspath('..'))
import time
import string


def retrievePregnancyDayOne(patient_ID):
    filename = 'CatalogueAndSettings\\catalog.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    # dictionaryCatalog=json.load(open(filename,'r'))
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                data= _patients["personalData"] 
                filepointer.close()    
                return data["pregnancyDayOne"]

def retrieveOnlineSince(patient_ID):
    filename = 'CatalogueAndSettings\\catalog.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                device=_patients["connectedDevice"]
                filepointer.close()
                return device["onlineSince"]

def retrieveTSReadAPIfromClientID(patient_ID):
    filename = '..\\CatalogueAndSettings\\catalog.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["doctorList"]
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
    filename = '..\\CatalogueAndSettings\\catalog.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["doctorList"]
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
    dictionary = json.load(open('..\\CatalogueAndSettings\\catalog.json','r'))
    lista = dictionary["doctorList"]
    for doctorObject in lista:
        connectedDevice = doctorObject["connectedDevice"]
        telegramID = connectedDevice["telegramID"] 
        if doctortelegramID == telegramID: 
            doctorID = doctorObject["doctorID"] 
            break
    return doctorID


def findPatient(chat_ID):
    filename = '..\\CatalogueAndSettings\\catalog.json'
    f = open(filename)
    catalog = json.load(f)

    patientID=-1
    lista = catalog["doctorList"]
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

    filename = 'CatalogueAndSettings\\catalog.json'
    filepointer = open(filename, 'r')
    catalog = json.load(filepointer)

    telegramID = -1
    lista = catalog["doctorList"]
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