import json
import sys, os
import json
sys.path.insert(0, os.path.abspath('..'))
import time
import string


def retrievePregnancyDayOne(patient_ID):
    filename = '..\\CatalogueAndSettings\\catalog.json'
    dictionaryCatalog=json.load(open(filename,'r'))
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                data= _patients["personalData"]
                return data["pregnancyDayOne"]

def retrieveOnlineSince(patient_ID):
    filename = '..\\CatalogueAndSettings\\catalog.json'
    dictionaryCatalog=json.load(open(filename,'r'))
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                device=_patients["connectedDevice"]
                return device["onlineSince"]

def retrieveTSReadAPIfromClientID(patient_ID):
    filename = '..\\CatalogueAndSettings\\catalog.json'
    dictionaryCatalog=json.load(open(filename,'r'))
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                data= _patients["connectedDevice"]["apikeys"][0]
                print(f"{patient_ID} has READ API KEY {data}")
                return data

def retrieveTSWriteAPIfromClientID(patient_ID):
    filename = '..\\CatalogueAndSettings\\catalog.json'
    dictionaryCatalog=json.load(open(filename,'r'))
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                data= _patients["connectedDevice"]["apikeys"][1]
                print(f"{patient_ID} has WRITE API KEY {data}")
                return data

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