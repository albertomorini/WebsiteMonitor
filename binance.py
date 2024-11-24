import requests
from datetime import datetime
import json 
import time
import telegramTalker # import TelegramTalker
import hashlib ## just for testing
# import urllib ## to parse URI for examle

PATHNAME_STORED= "./stored.json"
BASE_URI = 'https://api.binance.com/api/v3/'

PERCENTAGE_ALERT = 2
SLEEP_TIME = 120 # 2 min
STORE_FILE=False

REGISTER_NOTIFICATION = list()


############################################################################################################################################
def doRequest(endpoint):
    res = requests.get(BASE_URI+endpoint)
    if (res.status_code==200):
        return res.json()
    else:
        return null

def getUnixtime():
    return (datetime.now() - datetime(1970, 1, 1)).total_seconds()

def convertUnix2HumanTime(p_timestamp):
    ts = int(p_timestamp)
    # return str(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    return str(datetime.utcfromtimestamp(ts).strftime('%H:%M:%S'))

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
    global REGISTER_NOTIFICATION
    for indx, i in enumerate(REGISTER_NOTIFICATION):
        for j in actual:
            if(i.get("symbol")==j.get("symbol")): ## if the same check the prices
                symbol = i.get("symbol")
                old_price = float(i.get("price"))
                new_price = float(j.get("price"))
                percentageIncrement = (new_price-old_price)/ old_price * 100
                if(percentageIncrement>PERCENTAGE_ALERT): # UPDATE THE REGISTER
                    try:
                        REGISTER_NOTIFICATION[indx] = {"symbol":symbol,"time": getUnixtime(), "price":new_price, "increment":percentageIncrement, "old_time": i.get("time")}
                    except Exception:
                        print(Exception)


def sendAlert(notificationMessage):
    
    if(len(notificationMessage)>0):
        str = '<b> Binance alert </b> %0A%0A'
        for i in notificationMessage:
            symbol= i.get("symbol")
            increment = round(i.get("increment"),2)
            price = i.get("price")
            new_time= convertUnix2HumanTime(i.get("time"))
            old_time= convertUnix2HumanTime(i.get("old_time"))

            str += "<b><a href='https://www.binance.com/en/trade/"+symbol+"?type=spot'>"+symbol + "</a></b>  "
            str += " - increment: " + format(increment)
            str += " - price: " + format(price)
            str += " ||  " + format(old_time) + " - " + format(new_time)
            str +="%0A" # \n
            print(symbol)
        telegramTalker.sendMessage(str)
        print('message sent')


##########################################################################################################################################
def start():
    
    while True:
        actual_register = doRequest("ticker/price")
        actual_timestamp = getUnixtime()
        print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.now()))
        
        ## filter only the currency with USDC and USDT
        actual_register = list (filter((lambda x: (x.get('symbol').find('USD')) != -1), actual_register))
        
        ## baptize the set with a timestamp
        for i in actual_register:
            i.update({"time": actual_timestamp})

        global REGISTER_NOTIFICATION
        if(not REGISTER_NOTIFICATION): #empty list of last value, set the actual
            REGISTER_NOTIFICATION = actual_register
        else:
            known_currencies = list (map((lambda x: x.get('symbol')), REGISTER_NOTIFICATION))
            print()
            new_ones = list (filter((lambda x: x.get('symbol') not in known_currencies), actual_register))
            if(len(new_ones)>0):
                print("new currencies: "+str(new_ones))
            for i in new_ones:
                i.update({"time": actual_timestamp})
            REGISTER_NOTIFICATION = REGISTER_NOTIFICATION + new_ones

        

        compareRegisters(actual_register) #compare actual vs the last notified increment (or first one)

        ##########################################################################################
        notificationMessage = list()
        for i in REGISTER_NOTIFICATION:
            if(i.get("time")>actual_timestamp): #just the currency updated that we need to notifiy
                notificationMessage.append(i)

        sendAlert(notificationMessage)        

        time.sleep(SLEEP_TIME)
        print("...................\n\n\n")

start()
