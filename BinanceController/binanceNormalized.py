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
            # str = '<b> BINANCE ALERT </b> %0A%0A'
            strTMP = ''
            for i in notificationMessage:
                data = i.get("cur")
                if(i.get("flag")==0):
                    symbol = "🟥 "+ data.get("symbol")#loosing
                else:
                    symbol = "🟢 " + data.get("symbol")

                increment = round(data.get("increment"),2)
                decrement = data.get("LOSS_COUNTER")
                price = data.get("price")

                new_time= convertUnix2HumanTime(data.get("time"))

                # str += "<b><a href='https://www.binance.com/en/trade/"+symbol+"?type=spot'>"+symbol + "</a></b>  " #con URL
                strTMP += "<b>"+symbol + "</b>  " #senza URL
                strTMP += str(price)   #senza URL
                if(i.get("flag")==0):
                    strTMP += " // "+str(data.get("prezzoAlto")) + "  <b>" + format(increment)+"%</b> "
                else:
                    strTMP += "  <i>" + format(increment)+"%</i>"

                strTMP += " || " + format(new_time) +" \n"
                # strTMP +="\%0A" # \n

                print(strTMP)

            telegramTalker.sendMessage(TELEGRAM_TOKEN,strTMP)
    except Exception as e:
        print(e)
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
                    prezzoAlto = 0
                    try:
                        prezzoAlto = float(i.get("prezzoAlto"))
                    except:
                        pass
                    prezzoAlto = max(prezzoAlto,new_price)

                    percentageIncrement=0
                    try:
                        percentageIncrement = (new_price-prezzoAlto)/ prezzoAlto * 100
                    except Exception as e:
                        percentageIncrement = 0 #ignoring the division by 0
                    

                    incrementCounter = int(i.get("INCREMENT_COUNTER"))
                    toNotify= False
                    verse=0
                    if(percentageIncrement>=INCREMENT_PERCENTAGE ): # Up the increment counter - currency is growning
                        incrementCounter += 1 #if up, increment the counter
                    elif(incrementCounter>=INCREMENT_COUNTER and abs(percentageIncrement)>=LOSS_PERCENTAGE): # loosing 
                        toNotify=True
                        verse=-1
                        incrementCounter = 0 # stop grow then, reset the counter
                    
                    # if(incrementCounter%INCREMENT_COUNTER==0 and incrementCounter>0 and percentageIncrement>0): 
                    if(incrementCounter==INCREMENT_COUNTER and percentageIncrement>=INCREMENT_PERCENTAGE): 
                        toNotify=True
                        verse=1

                    REGISTER_GLOBAL[indx] = {
                        "prezzoAlto": prezzoAlto,
                        "symbol":symbol,
                        "time": getUnixtime(),
                        "price":new_price, 
                        "priceAlto":new_price, 
                        "increment":percentageIncrement,
                        "INCREMENT_COUNTER": incrementCounter,
                        "toNotify": toNotify,
                        "old_price": old_price,
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
        actual_register = list (filter((lambda x: (x.get('symbol').find('USDT')) != -1), actual_register)) ## filter only the currency with USDT
        #print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.datetime.now()))

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
            if(i.get("toNotify")):
                if(i.get("verse")>0):
                    notificationMessage.append({"cur": i, "flag": 1})
                else:
                    notificationMessage.append({"cur": i, "flag": 0})

        sendAlert(notificationMessage)


        # TODO: remove in production
        time.sleep(SLEEP_TIME)
        counter+=1
        if(counter>20000):
            break
            
        # print("...................\n\n\n")


#############################################################################

loadConfig()
start()