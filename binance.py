import requests
from datetime import datetime
import json 
import time
import hashlib ## just for testing
# import urllib ## to parse URI for examle

PATHNAME_STORED= "./stored.json"
BASE_URI = 'https://api.binance.com/api/v3/'

PERCENTAGE_ALERT = 0.5
SLEEP_TIME = 120 # 2 min
STORE_FILE=False

lastNotifications = list()

############################################################################################################################################
def doRequest(endpoint):
    res = requests.get(BASE_URI+endpoint)
    if (res.status_code==200):
        return res.json()
    else:
        return null

def getUnixtime():
    return (datetime.now() - datetime(1970, 1, 1)).total_seconds()

def loadJSON():
    try:
        ff = open(PATHNAME_STORED,'r')
        return json.loads(ff.read())
    except Exception:
        return dict()

# compare two dataslot from each other (actual, the previous one with the actual one)
def compareRegisters(prev,actual):
    for i in prev: # all old currencies
        for j in actual: # all new currencies
            if(i.get("symbol")==j.get("symbol")): ## if the same check the prices
                symbol = i.get("symbol")
                old_price = float(i.get("price"))
                new_price = float(j.get("price"))
                percentageIncrement = (new_price-old_price)/ old_price * 100
                if(percentageIncrement>PERCENTAGE_ALERT):
                    print(symbol,"\t",percentageIncrement, new_price)

# compare the actual slot of data, with last notified data 
def compareRegisters(actual):
    global lastNotifications
    for i in lastNotifications:
        for j in actual:
            if(i.get("symbol")==j.get("symbol")): ## if the same check the prices
                symbol = i.get("symbol")
                old_price = float(i.get("price"))
                new_price = float(j.get("price"))
                percentageIncrement = (new_price-old_price)/ old_price * 100
                if(percentageIncrement>PERCENTAGE_ALERT):
                    i.update({"time": getUnixtime()},{"price":new_price},{"increment":percentageIncrement})
                    #TODO: telegram API integration (bot)
                    # print(symbol,"\t",percentageIncrement, new_price)


##########################################################################################################################################
def start():
    registers = loadJSON() #TODO: gestire il flag di non lettura
    ff = getUnixtime()
    while True:
        actual_register = doRequest("ticker/price")
        dummyTimestamp = getUnixtime()
        print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.now()))
        
        global lastNotifications
        if(not lastNotifications): #empty list of last value, set the actual
            for i in actual_register:
                i.update({"time": dummyTimestamp})
            lastNotifications = actual_register
        else:
            pass ## TODO: add the new cryptos
        
        try: #compare with previous
            # compareRegisters(registers[list(registers.keys())[-1]],actual_register) #compare actual vs last one
            # compareRegisters(registers[list(registers.keys())[0]],actual_register) #compare actual vs the last notified increment (or first one)
            compareRegisters(actual_register) #compare actual vs the last notified increment (or first one)
        except Exception:
            pass

        for i in lastNotifications:
            if(i.get('time')>ff):
                print(i)

        print("...................\n\n\n")
        registers[getUnixtime()] = actual_register #store into JSON
        time.sleep(SLEEP_TIME)
        
    # print(dummyDict)

    # ff = open("stored.json","w")
    # ff.write(json.dumps(registers))
    # ff.close

    

start()
