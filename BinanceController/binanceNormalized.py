import requests
import datetime
import json
import time
import telegramTalker # import TelegramTalker
import hashlib ## just for testing
import sys

BASE_URI = 'https://api.binance.com/api/v3/'
BASE_URI_CONVERT = "https://www.binance.com/en/convert/"
MODE = None

TELEGRAM_TOKEN = ''
SLEEP_TIME = 120 # 2 min
INCREMENT_COUNTER = -1
INCREMENT_PERCENTAGE = -1
LOSS_PERCENTAGE = -1

TO_IGNORE = []

REGISTER_GLOBAL = list()
############################################################################################################################################

def loadConfig():
    global SLEEP_TIME
    global TELEGRAM_TOKEN
    global INCREMENT_COUNTER
    global INCREMENT_PERCENTAGE
    global LOSS_PERCENTAGE
    global TO_IGNORE

    x = loadJSON('./Normalized_Config.json') #config

    SLEEP_TIME = x.get("SecondiAggiornamento")
    TELEGRAM_TOKEN = x.get("TELEGRAMTOKEN")
    INCREMENT_COUNTER  = x.get("ContatoreIncremento")
    INCREMENT_PERCENTAGE  = x.get("PercentualeIncremento")
    LOSS_PERCENTAGE = x.get("PercentualePerdita")
    TO_IGNORE = x.get("DaIgnorare")

############################################################################################################################################
def doRequest(endpoint):
    try:
        res = requests.get(BASE_URI+endpoint)
        if (res.status_code==200):
            return res.json()
        else:
            return null
    except Exception:
        print("ERRORE fetching sito")
        return []
        # if(guardiaFirstSend):
        #     time.sleep(5)
        #     doRequest(endpoint,False)

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
            strTMP = ''
            for i in notificationMessage:
                data = i.get("cur")
                
                dummy_symbol=data.get("symbol")
                try:
                    indexUSD = dummy_symbol.index("USD")
                except Exception:
                    indexUSD = dummy_symbol.index("BTC")
                
                if(i.get("flag")==0):
                    symbol = "🟥"
                    symbol += "<b><a href='"+(BASE_URI_CONVERT +  dummy_symbol[0:indexUSD] + "/" +dummy_symbol[indexUSD:len(dummy_symbol)])
                    symbol += "'>"+dummy_symbol+"</a></b> "
                else:
                    symbol = "🟢"
                    symbol += "<b><a href='"+(BASE_URI_CONVERT + dummy_symbol[indexUSD:len(dummy_symbol)] + "/" +  dummy_symbol[0:indexUSD])
                    symbol += "'>"+dummy_symbol+"</a></b> "

                increment = round(data.get("increment"),2)

                strTMP += symbol 
                strTMP += str(data.get("price"))  
                if(i.get("flag")==0):
                    strTMP += " // "+str(data.get("max_price")) + "  <b>" + format(increment)+"%</b> "
                else:
                    strTMP += "  <i>" + format(increment)+"%</i>"

                strTMP += " || " + format(convertUnix2HumanTime(data.get("time"))) +" \n"


            print(TELEGRAM_TOKEN,strTMP)
            telegramTalker.sendMessage(TELEGRAM_TOKEN,strTMP)
    except Exception as e:
        print(e)
        

############################################################################################################################################


# compare the actual slot of data, with last notified data
def compareRegisters(actual):
    try:
        global REGISTER_GLOBAL
        for indx, i in enumerate(REGISTER_GLOBAL):
            for j in actual:
                symbol = i.get("symbol")
                if(symbol==j.get("symbol")): ## if the same check the prices
                    new_price = float(j.get("price"))
               
                    if(i.get("max_price")==None):
                        max_price=float(i.get("price"))
                    else:
                        max_price=float(i.get("max_price"))

                    percentageIncrement=0
                    try:
                        percentageIncrement = ((new_price-max_price)/ max_price) * 100
                    except Exception as e:
                        percentageIncrement = 0 #ignoring the division by 0
                    
                    incrementCounter = int(i.get("INCREMENT_COUNTER"))
                    verse=0
                    if(percentageIncrement>=INCREMENT_PERCENTAGE): # Up the increment counter - currency is growning
                        incrementCounter += 1 #if up, increment the counter
                        max_price=new_price
                    elif(incrementCounter>=INCREMENT_COUNTER and  -1*percentageIncrement>=LOSS_PERCENTAGE): # loosing 
                        print(percentageIncrement)
                        verse=-1
                        incrementCounter = 0 # stop grow then, reset the counter
                        #max_price=None #TODO: CHIEDERE AD ANDREA
                    
                    if(incrementCounter==INCREMENT_COUNTER and percentageIncrement>=INCREMENT_PERCENTAGE): 
                        verse=1

                    REGISTER_GLOBAL[indx] = {
                        "symbol":symbol,
                        "time": getUnixtime(),
                        "price":new_price, 
                        "max_price":max_price, 
                        "increment":percentageIncrement,
                        "INCREMENT_COUNTER": incrementCounter,
                        "verse": verse
                    }

    except Exception as e:
        print("ERROR: ", e)
        pass


def start():
    print("Binance normalized avviato.")
    counter = 0
    while True:
        actual_register = doRequest("ticker/price")
        actual_register = list (filter((lambda x:  (x.get('symbol').find('USDC')) != -1 or (x.get('symbol').find('USDT')) != -1 or (x.get('symbol')[-3:]) == "BTC"  ), actual_register)) ## filter only the currency with USDC
        print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.datetime.now()))

        ## ADDED LATELY: removing unwanted symbols
        for x in actual_register:
            if(x.get("symbol") in TO_IGNORE):
                actual_register.remove(x)

        actual_timestamp = getUnixtime()

        ## baptize the set with a timestamp
        for i in actual_register:
            i.update({"time": actual_timestamp})
            i.update({"INCREMENT_COUNTER": 0}) # init


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
                REGISTER_GLOBAL = REGISTER_GLOBAL + new_ones


        compareRegisters(actual_register) #compare actual vs the last notified increment (or first one)

        # ##########################################################################################
        notificationMessage = list()
        for i in REGISTER_GLOBAL:
            dummyverse= i.get("verse")
            if(dummyverse==1): #to notify and positive
                notificationMessage.append({"cur": i, "flag": 1})
            elif(dummyverse==-1): #to notify and loss
                notificationMessage.append({"cur": i, "flag": 0})
        
        if(len(notificationMessage)==0):
            print("Attendi...")
        else:
            print("Messaggio inviato")
        print("................................................")
        sendAlert(notificationMessage)

        time.sleep(SLEEP_TIME)



#############################################################################

loadConfig()
start()
