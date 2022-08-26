import threading
import requests
import time

import random as rand

threadHell = []
mainThreadList = []

def death():
    print(time.perf_counter())

def threadCycleStart():
    #creates new thread objects
    for i in range(rand.randint(15, 45)):
        newThread = threading.Thread(target=death)
        threadHell.append(newThread)
    
    print(threadHell)
    #starts new thread objects
    for index in range(len(threadHell)):
        print(index)
        currentThread = threadHell[index]
        currentThread.start()

    mainThreadList.append(threadHell)

    #clears temp thread creation list
    threadHell.clear()

    tCS_two()

def tCS_two():
    #creates new thread objects
    for i in range(30):
        newThread = threading.Thread(target=death)
        threadHell.append(newThread)
    
    print(threadHell)

    #starts new thread objects
    for index in range(len(threadHell)):
        print(index)
        currentThread = threadHell[index]
        currentThread.start()

    mainThreadList.append(threadHell)

    #clears temp thread creation list
    threadHell.clear

threadCycleStart()

print(mainThreadList)

mainThreadList.clear()

