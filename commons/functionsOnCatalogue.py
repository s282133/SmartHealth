import json
import sys, os
import json
sys.path.insert(0, os.path.abspath('..'))

filename = 'CatalogueAndSettings\\catalog.json'

dictionaryCatalog=json.load(open(filename,'r'))


def retrievePregnancyDayOne(patient_ID):
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                data= _patients["personalData"]
                return data["pregnancyDayOne"]

def retrieveOnlineSince(patient_ID):
    docList=dictionaryCatalog["doctorList"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                device=_patients["connectedDevice"]
                return device["onlineSince"]