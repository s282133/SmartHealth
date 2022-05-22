from time import sleep
from rpiPublisher import *
from threading import Thread

# unico modo che mi viene in mente per lanciare piu istanze di rpi dallo stesso file


thread1 = Thread(target=rpiPub, args=("Chiara",))
thread1.start()

#sleep(3)

thread2 = Thread(target=rpiPub, args=("Lucia",))
thread2.start()