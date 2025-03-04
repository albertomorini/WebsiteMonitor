import requests
import datetime
import json
import time
import telegramTalker # import TelegramTalker
import hashlib ## just for testing
import sys

BASE_URI = 'https://api.binance.com/api/v3/'
MODE = None

TELEGRAM_TOKEN = ''
SLEEP_TIME = 120 # 2 min
INCREMENT_COUNTER = -1
INCREMENT_PERCENTAGE = -1
LOSS_COUNTER= -1
LOSS_PERCENTAGE = -1


REGISTER_GLOBAL = list()
############################################################################################################################################

def loadConfig():
    global SLEEP_TIME
    global TELEGRAM_TOKEN
    global INCREMENT_COUNTER
    global INCREMENT_PERCENTAGE
    global LOSS_COUNTER
    global LOSS_PERCENTAGE

    x = loadJSON('./UltimoNormalized_Config.json') #config

    SLEEP_TIME = x.get("SecondiAggiornamento")
    TELEGRAM_TOKEN = x.get("TELEGRAMTOKEN")
    INCREMENT_COUNTER  = x.get("ContatoreIncremento")
    INCREMENT_PERCENTAGE  = x.get("PercentualeIncremento")
    LOSS_COUNTER = x.get("ContatorePerdita")
    LOSS_PERCENTAGE  = x.get("PercentualePerdita")

############################################################################################################################################
def doRequest(endpoint,guardiaFirstSend=True):
    try:
        res = requests.get(BASE_URI+endpoint)
        if (res.status_code==200):
            return res.json()
        else:
            return null
    except Exception:
        print("ERRORE fetching sito")
        if(guardiaFirstSend):
            time.sleep(5)
            doRequest(endpoint,False)

def getUnixtime():
    return (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()

def convertUnix2HumanTime(p_timestamp):
    ts = int(p_timestamp)
    return str(datetime.datetime.fromtimestamp(ts, datetime.UTC).strftime('%H:%M:%S'))

def loadJSON(path):
    try:
        ff = open(path,'r')
        return json.loads(ff.read())
    except Exception:
        return dict()
############################################################################################################################################

## Just create the message and send to Telegram Bot
def sendAlert(notificationMessage):
    try:
        if(len(notificationMessage)>0):
            str = '<b> BINANCE ALERT </b> %0A%0A'
            for i in notificationMessage:
                symbol= i.get("symbol")
                increment = round(i.get("increment"),2)
                price = i.get("price")
                new_time= convertUnix2HumanTime(i.get("time"))
                old_time= convertUnix2HumanTime(i.get("old_time"))

                # str += "<b><a href='https://www.binance.com/en/trade/"+symbol+"?type=spot'>"+symbol + "</a></b>  " #con URL
                str += "<b>"+symbol + "</b>  " #senza URL
                str += " - increment: " + format(increment)
                str += " - price: " + format(price)
                str += " ||  " + format(old_time) + " - " + format(new_time)
                str +="%0A" # \n

            telegramTalker.sendMessage(TELEGRAM_TOKEN,str)
    except Exception as e:
        pass


############################################################################################################################################



# compare the actual slot of data, with last notified data
def compareRegisters(actual):
    try:
        global REGISTER_GLOBAL
        for indx, i in enumerate(REGISTER_GLOBAL):
            for j in actual:
                symbol = i.get("symbol")
                if(symbol==j.get("symbol")): ## if the same check the prices
                    old_price = float(i.get("price"))
                    new_price = float(j.get("price"))
                    dummy_IncrementCounter = int(i.get("INCREMENT_COUNTER"))
                    dummy_LossCounter = int(i.get("LOSS_COUNTER"))
                    percentageIncrement=0
                    try:
                        percentageIncrement = (new_price-old_price)/ old_price * 100
                    except Exception as e:
                        pass
                    if(percentageIncrement>=INCREMENT_PERCENTAGE): # Up the increment counter
                            dummy_IncrementCounter +=1
                            if(dummy_LossCounter>0): #otherwise the loss won't be detected
                                dummy_LossCounter -=1
                    elif(dummy_IncrementCounter>= INCREMENT_COUNTER ): ## and percentageIncrement<INCREMENT_PERCENTAGE is implicit # "up" the LOSS counter - if has grown in the past otherwise is already decreasing
                            dummy_IncrementCounter = INCREMENT_COUNTER-1 # chef kiss
                            dummy_LossCounter = dummy_LossCounter + 1

                    REGISTER_GLOBAL[indx] = {"symbol":symbol,"time": getUnixtime(), "price":new_price, "increment":percentageIncrement, "INCREMENT_COUNTER": dummy_IncrementCounter, "LOSS_COUNTER":dummy_LossCounter}

    except Exception as e:
        print(e)
        pass


def start():
    print("Binance normalized avviato.")
    while True:
        actual_register = doRequest("ticker/price")
        actual_register = list (filter((lambda x: (x.get('symbol').find('USDT')) != -1), actual_register)) ## filter only the currency with USDT
        #print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.datetime.now()))

        actual_timestamp = getUnixtime()

        ## baptize the set with a timestamp
        for i in actual_register:
            i.update({"time": actual_timestamp})
            i.update({"INCREMENT_COUNTER": 0}) # init
            i.update({"LOSS_COUNTER": 0}) # init


        global REGISTER_GLOBAL
        if(not REGISTER_GLOBAL): #empty list of last value, set the actual
            REGISTER_GLOBAL = actual_register
        else:
            known_currencies = list (map((lambda x: x.get('symbol')), REGISTER_GLOBAL))
            new_ones = list (filter((lambda x: x.get('symbol') not in known_currencies), actual_register))
            if(len(new_ones)>0):
                print("Nuove monete: "+str(new_ones))
                for i in new_ones:
                    i.update({"time": actual_timestamp})
                    i.update({"INCREMENT_COUNTER": 0}) # init
                    i.update({"LOSS_COUNTER": 0}) # init
                REGISTER_GLOBAL = REGISTER_GLOBAL + new_ones


        compareRegisters(actual_register) #compare actual vs the last notified increment (or first one)

        # ##########################################################################################
        notificationMessage = list()
        for i in REGISTER_GLOBAL:
            ## now we tell if is in loss or in grow --> checking the counter
            if(i.get("INCREMENT_COUNTER")>=INCREMENT_COUNTER):
                print("++ SALITA\t", i.get("symbol"), i.get("increment"))
            if(i.get("LOSS_COUNTER")>=LOSS_COUNTER):
                print("--- PERDITA\t", i.get("symbol"), i.get("increment"))
            #     notificationMessage.append(i)
            ##TODO: da rimuovere quando scende di troppo


        sendAlert(notificationMessage)

        # if(MODE=='ultimoprezzo'):
        #     REGISTER_GLOBAL = actual_register

        time.sleep(SLEEP_TIME)
        print("...................\n\n\n")


#############################################################################

loadConfig()
start()
