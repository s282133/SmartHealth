import time
import cherrypy
import json
import requests


if __name__ == "__main__":
  
    cont = 0
    sum = 0


    parametro = input('Che parmetro vuoi utilizzare? \n 1.Temperature \n 2.Humidity \n Parametro:') 

    if parametro == '1':
        st_parametro = 'temperature'
    else:
        st_parametro = 'humidity'


    done=False
    while not done:
        time.sleep(3)

        r = requests.get('http://127.0.0.1:8080/temperature') 
        #r = requests.get('http://192.168.1.254:8080/'+st_parametro) #collegarsi al programma che è in esecuzione su quell'indirizzo ip attraverso una chiamata get

        j_temp = r.json() 

        vett = j_temp['e']
        primo = vett[0]
        temp = float(primo['v'])

        cont += 1
        sum += temp

        print('Temperatura ' + str(cont) + ': ' + str(temp))

        if cont == 10:
            media = sum/cont
            print('Media Temperatura: ', media)
            cont = 0
            sum = 0

