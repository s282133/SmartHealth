import json
import sys, os
import json
import time
import requests


sys.path.insert(0, os.path.abspath('..'))


def openCatalogue():
    filename = 'ServicesAndResourcesCatalogue.json'
    f = open(filename)
    catalog = json.load(f)
    return catalog

# recupera le info dei canali su Thingspeak
def getListsOfTSinfo():
    catalog = openCatalogue()
    lista = catalog["resources"]
    patientIDs_channels = {}
    for currentDoctor in lista:
        patientList = currentDoctor["patientList"]
        for currentPatient in patientList:
            patientID = currentPatient["patientID"]
            connectedDevice = currentPatient["connectedDevice"]
            ts_info = connectedDevice["thingspeakInfo"]
            channelID = ts_info["channel"]
            key_patientID = int(patientID)
            patientIDs_channels[f"{key_patientID}"] = channelID
    return_dict = dict(patientIDs_channels)
    return json.dumps(patientIDs_channels)

# cerca il paziente a partire dal patientID
def get_patient_from_patient_id(patientID):
    catalog = openCatalogue()
    lista = catalog["resources"]
    for currentDoctor in lista:
        patientList = currentDoctor["patientList"]
        currentPatient = next((x for x in patientList if int(x["patientID"])==int(patientID)), None)
        if currentPatient != None:
            return currentPatient   
    return None
       

def retrievePregnancyDayOne(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    personalData = currentPatient["personalData"] 
    return personalData["pregnancyDayOne"]
                
 
def retrieveOnlineSince(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    connectedDevice=currentPatient["connectedDevice"]
    return connectedDevice["onlineSince"]

# READ API thingspeak 
def retrieveTSReadAPIfromClientID(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    connectedDevice = currentPatient["connectedDevice"]
    thingspeakInfo = connectedDevice["thingspeakInfo"]
    api_keys = list(thingspeakInfo["apikeys"])
    return api_keys[1]

# WRITE API thingspeak 
def retrieveTSWriteAPIfromClientID(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    connectedDevice = currentPatient["connectedDevice"]
    thingspeakInfo = connectedDevice["thingspeakInfo"]
    api_keys = list(thingspeakInfo["apikeys"])
    return api_keys[0]

# cerca il paziente a partire dal telegramID
def findPatientFromChatID(chat_ID):
    catalog = openCatalogue()
    lista = catalog["resources"]
    for currentDoctor in lista:
        patientList = currentDoctor["patientList"]
        for currentPatient in patientList:
            connectedDevice = currentPatient["connectedDevice"] 
            telegramID = connectedDevice["telegramID"]
            if  int(chat_ID) == int(telegramID):
                patientID = currentPatient["patientID"] 
                return patientID   
    return None

# trova il dottore del paziente a partire dal patientID
def findDoctorTelegramIdFromPatientId(parPatientID):
    catalog = openCatalogue()
    lista = catalog["resources"]
    for currentDoctor in lista:
        patientList = currentDoctor["patientList"]
        for currentPatient in patientList:
            patientID = currentPatient["patientID"] 
            if  int(patientID) == int(parPatientID):
                connectedDevice = currentDoctor["connectedDevice"]
                telegramID = connectedDevice["telegramID"]
                return telegramID    
    return None
    
# recupera il topic in base al nome del parametro
def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    #"topic_temperature": "{{base_topic}}/{{patientID}}/temperature",
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", parPatientID) 
    return local_topic

# nome del paziente a partire dal patientID
def getNameFromClientID(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    patientName=currentPatient["patientName"]
    patientSurname=currentPatient["patientSurname"]
    return f"{patientName} {patientSurname}"

# cerca lo stato di monitoraggio on/off
def getMonitoringStateFromClientID(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    monitoring = currentPatient["monitoring"]
    return monitoring

# setta lo stato di monitoraggo on/off
def setMonitorinStatefromClientID(patient_ID, monitoring):
    catalog = openCatalogue()
    docList=catalog["resources"]
    for currentDoctor in docList:
        patientList = currentDoctor["patientList"] 
        for currentPatient in patientList: 
            if int(patient_ID) == int(currentPatient["patientID"]):
                currentPatient["monitoring"] = monitoring
                with open('ServicesAndResourcesCatalogue.json', "w") as f:
                    json.dump(catalog, f, indent=2)
                    f.close()
                return True    
    return False
         
# trova il servizio a partire dal nome
def main_getServiceByName(parServiceName):
    catalog = openCatalogue()
    services = catalog["services"]
    first_or_default = next((x for x in services if x["service_name"]==parServiceName), None)
    return first_or_default 

# trova l'API a partire dal nome
def main_getApiByServiceAndName(parAPIs,parApiName):
    first_or_default = next((x for x in parAPIs if x["functionality_name"]==parApiName), None)
    return first_or_default 

# trova l'API a partire dal nome del servizio e dell'api
def main_getApiByName(parServiceName,parApiName):
    mqtt_service = main_getServiceByName(parServiceName)
    if mqtt_service != None:
        api = mqtt_service["APIs"]
        first_or_default = next((x for x in api if x["functionality_name"]==parApiName), None)
        return first_or_default 
    else: 
        return None
    
# cerca la lista dei pazienti che non hanno il raspberry
def get_lista_pazienti_simulati():
    json_lista = {
        "lista_pazienti_simulati": []
    }
    catalog = openCatalogue()
    lista = catalog["resources"]
    if len(lista)!=0:
        for currentDoctor in lista:
            patientList = currentDoctor["patientList"]
            if len(patientList)!=0:
                for currentPatient in patientList:
                    patientID = currentPatient["patientID"]
                    idRegistratoSuRaspberry = currentPatient["idRegistratoSuRaspberry"]
                    if idRegistratoSuRaspberry == "no":    
                        json_lista["lista_pazienti_simulati"].append(patientID)
        return json.dumps(json_lista)


# trova la settimana attuale di gravidanza
def getWeek(dayOne):
    currTime = time.strftime("%Y-%m-%d")
    currY = currTime.split("-")[0]
    currM = currTime.split("-")[1]
    currD = currTime.split("-")[2]
    currDays = int(currY)*365 + int(currM)*30 + int(currD)
    dayoneY = str(dayOne).split("-")[0]
    dayoneM = str(dayOne).split("-")[1]
    dayoneD = str(dayOne).split("-")[2]
    dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
    elapsedDays = currDays - dayoneDays
    week = int(elapsedDays / 7)
    return week

# elimina paziente dal catalogo dopo la 36esima settimana
def delete_ex_patients():
    catalog = openCatalogue()
    Modificato = False
    doctorList = catalog["resources"]
    for currentDoctor in doctorList:
        patientList = currentDoctor["patientList"]
        devicesList = currentDoctor["devicesList"]
        for currentPatient in patientList:
            dayOne = currentPatient["personalData"]["pregnancyDayOne"] 
            week = getWeek(dayOne)
            if int(week) >= 36:
                patientID_to_delete = int(currentPatient["patientID"])
                for currentDevice in devicesList:
                    if int(currentDevice["patientID"]) == patientID_to_delete and len(devicesList)>1:
                        devicesList.remove(currentDevice)
                    elif int(currentPatient["patientID"]) == patientID_to_delete and len(devicesList)==1:    
                        devicesList=[]
                    currentDoctor["devicesList"]=devicesList
                if  len(patientList)>1:    
                    patientList.remove(currentPatient)
                elif len(patientList)==1:
                        patientList=[]
                currentDoctor["patientList"]=patientList
                api=main_getApiByName("Thingspeak","delete_channel_thingspeak")
                local_uri=api["uri"]
                body = api["api_key"]
                map_patientID_channelID = getListsOfTSinfo()
                map_dict = dict(json.loads(map_patientID_channelID))
                for k in map_dict:
                    if int(k) == int(patientID_to_delete):
                        associated_channelID = map_dict[k]
                final_local_uri = str(local_uri).replace("{{channelID}}", str(associated_channelID))
                r=requests.delete(final_local_uri, data=body)
        catalog["resources"] = doctorList
        Modificato = True

    if Modificato:
        with open('ServicesAndResourcesCatalogue.json', "w") as f:
            json.dump(catalog, f, indent=2)
            f.close()

# trova la lista dei pazienti da monitorare
def get_lista_pazienti_da_monitorare():
    json_lista = {
        "lista_pazienti_da_monitorare": []
    }

    catalog = openCatalogue()
    doctorList = catalog["resources"]
    for currentDoctor in doctorList:
        patientList = currentDoctor["patientList"]
        for currentPatient in patientList:

            if currentPatient["state"] == "archiviato": 
                continue

            connectedDevice = currentPatient["connectedDevice"]
            if connectedDevice["onlineSince"] == -1 :
                patientID = currentPatient["patientID"]
                json_lista["lista_pazienti_da_monitorare"].append(patientID)
    return json.dumps(json_lista)


def set_lista_pazienti_in_monitoring(patient_ID):
    catalog = openCatalogue()
    docList=catalog["resources"]
    for currentDoctor in docList:
        patientList=currentDoctor["patientList"] 
        for currentPatient in patientList: 
            if int(patient_ID) == int(currentPatient["patientID"]):
                connectedDevice = currentPatient["connectedDevice"]
                connectedDevice["onlineSince"] = time.strftime("%Y-%m-%d") 
                with open('ServicesAndResourcesCatalogue.json', "w") as f:
                    json.dump(catalog, f, indent=2)
                    f.close()
                return True    
    return False

# trova i pazienti a partire dal telegramID del medico
def get_patient_from_doctortelegram_id(doctortelegramID):
    catalog = openCatalogue()
    docList=catalog["resources"]
    doctor_number = 0
    for doctorObject in docList:
        connectedDevice = doctorObject["connectedDevice"]
        telegramID = connectedDevice["telegramID"] 
        if doctortelegramID == telegramID: 
            break
        doctor_number += 1
        lista = catalog["resources"][doctor_number] 
    return json.dumps(lista) 


def file_in_use(fpath):
    if os.path.exists(fpath):
        try:
            os.rename(fpath, fpath)
            return False
        except OSError as e:
            return True

def resetCatalog():
    catalog = openCatalogue()
    docList=catalog["resources"]
    if len(docList) > 0:
        for _doctors in docList:
            patientList=_doctors["patientList"] 
            if len(patientList) > 0:
                for _patients in patientList: 
                    _patients["connectedDevice"]["onlineSince"] = -1
                    with open('ServicesAndResourcesCatalogue.json', "w") as f:
                        json.dump(catalog, f, indent=2)