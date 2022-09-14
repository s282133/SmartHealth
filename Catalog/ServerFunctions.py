import json
import sys, os
import json
import time


sys.path.insert(0, os.path.abspath('..'))

# Questa raccolta di funzioni si trova sullo stesso server del MainServer 
# quindi hanno l'accesso diretto al catalogo, vengono usate solo dal MainServer

def openCatalogue():
    filename = 'ServicesAndResourcesCatalogue.json'

    f = open(filename)
    catalog = json.load(f)
    #time.sleep(1)
    return catalog


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


def retrieveTSReadAPIfromClientID(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    connectedDevice = currentPatient["connectedDevice"]
    thingspeakInfo = connectedDevice["thingspeakInfo"]
    api_keys = list(thingspeakInfo["apikeys"])
    return api_keys[1]


def retrieveTSWriteAPIfromClientID(patient_ID):
    print(f"patient_ID: {patient_ID}")
    currentPatient = get_patient_from_patient_id(patient_ID) 
    #data= currentPatient["connectedDevice"]["thingspeakInfo"]["apikeys"][0]
    connectedDevice = currentPatient["connectedDevice"]
    #print(f"connectedDevice: {connectedDevice}")
    thingspeakInfo = connectedDevice["thingspeakInfo"]
    #p(f"thingspeakInfo: {thingspeakInfo}")                
    api_keys = list(thingspeakInfo["apikeys"])
    #print(f"api_keys: {api_keys}")        
    return api_keys[0]


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
    

def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    #"topic_temperature": "{{base_topic}}/{{patientID}}/temperature",
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", parPatientID) #parPatient da passare come stringa
    return local_topic


def getNameFromClientID(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    patientName=currentPatient["patientName"]
    patientSurname=currentPatient["patientSurname"]
    return f"{patientName} {patientSurname}"


def getMonitoringStateFromClientID(patient_ID):
    currentPatient = get_patient_from_patient_id(patient_ID) 
    monitoring = currentPatient["monitoring"]
    return monitoring


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
         

def main_getServiceByName(parServiceName):
    catalog = openCatalogue()
    services = catalog["services"]
    first_or_default = next((x for x in services if x["service_name"]==parServiceName), None)
    return first_or_default 


def main_getApiByServiceAndName(parAPIs,parApiName):
    first_or_default = next((x for x in parAPIs if x["functionality_name"]==parApiName), None)
    return first_or_default 


def main_getApiByName(parServiceName,parApiName):
    mqtt_service = main_getServiceByName(parServiceName)
    if mqtt_service != None:
        api = mqtt_service["APIs"]
        first_or_default = next((x for x in api if x["functionality_name"]==parApiName), None)
        return first_or_default 
    else: 
        return None


def get_lista_pazienti_simulati():
    json_lista = {
        "lista_pazienti_simulati": []
    }
    catalog = openCatalogue()
    lista = catalog["resources"]
    for currentDoctor in lista:
        patientList = currentDoctor["patientList"]
        for currentPatient in patientList:
            patientID = currentPatient["patientID"]
            idRegistratoSuRaspberry = currentPatient["idRegistratoSuRaspberry"]
            
            # #prova
            # connectedDevice=currentPatient["connectedDevice"]
            # onlineSince = connectedDevice["onlineSince"]
            #aggiunto and
            if idRegistratoSuRaspberry == "no":
                
                json_lista["lista_pazienti_simulati"].append(patientID)
    
    return json.dumps(json_lista)


# esiste una copia identica in functionsOnCatalogue
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


def contolla_scadenza_week():
    catalog = openCatalogue()
    Modificato = False
    doctorList = catalog["resources"]
    for currentDoctor in doctorList:
        patientList = currentDoctor["patientList"]
        for currentPatient in patientList:

            if currentPatient["state"] == "archiviato": 
                continue

            # archive entry in catalogue if pregnancy week is greater than 36 (i.e., 9 months)
            dayOne = currentPatient["personalData"]["pregnancyDayOne"] 
            week = getWeek(dayOne)
            print(f'Patient {currentPatient["patientID"]} is in week {week}')
            if int(week) >= 36:
                currentPatient["state"] = "archiviato"
                #patientList.remove(currentPatient)
                Modificato = True

    if Modificato:
        with open('ServicesAndResourcesCatalogue.json', "w") as f:
            json.dump(catalog, f, indent=2)
            f.close()


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
                print("aggiungerò...")
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


# da eliminare?
# def findDoctorIDwithtelegramID(doctortelegramID):
#     dictionary = json.load(open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json','r'))

#     lista = dictionary["resources"]
#     for currentDoctor in lista:
#         connectedDevice = currentDoctor["connectedDevice"]
#         telegramID = connectedDevice["telegramID"] 
#         if doctortelegramID == telegramID: 
#             doctorID = currentDoctor["doctorID"] 
#             return doctorID
#     return None


def file_in_use(fpath):
    if os.path.exists(fpath):
        try:
            os.rename(fpath, fpath)
            return False
        except OSError as e:
            return True

