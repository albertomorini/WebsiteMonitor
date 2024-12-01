import requests
from datetime import datetime
import json 
import time
import telegramTalker # import TelegramTalker
import hashlib ## just for testing
import sys


BASE_URI = 'https://api.binance.com/api/v3/'
MODE = sys.argv[1]

PERCENTAGE_ALERT = 2
SLEEP_TIME = 120 # 2 min
TELEGRAM_TOKEN = ''

REGISTER_NOTIFICATION = list()

def loadConfig():
    global PERCENTAGE_ALERT 
    global SLEEP_TIME
    global TELEGRAM_TOKEN
    x = loadJSON('./UltimaNotifica_Config.json') #default ultima modifica
    if(MODE=='UltimoPrezzo'):
        x = loadJSON('./UltimoPrezzo_Config.json') #default ultima modifica

    PERCENTAGE_ALERT=x.get('PercentualeAvviso')
    SLEEP_TIME=x.get('SecondiAttesa')
    TELEGRAM_TOKEN=x.get("TelegramToken")

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

def loadJSON(path):
    try:
        ff = open(path,'r')
        return json.loads(ff.read())
    except Exception:
        return dict()

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
                if(percentageIncrement>=PERCENTAGE_ALERT): # UPDATE THE REGISTER
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

            # str += "<b><a href='https://www.binance.com/en/trade/"+symbol+"?type=spot'>"+symbol + "</a></b>  " #con URL
            str += "<b>"+symbol + "</b>  " #senza URL
            str += " - increment: " + format(increment)
            str += " - price: " + format(price)
            str += " ||  " + format(old_time) + " - " + format(new_time)
            str +="%0A" # \n
            
        telegramTalker.sendMessage(TELEGRAM_TOKEN,str)
        print('Messaggio telegram partito')


##########################################################################################################################################
def start():
    
    while True:
        # if(datetime.now().hour < 22 and  datetime.now().hour>9):
        actual_register = doRequest("ticker/price")
        actual_timestamp = getUnixtime()
        print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.now()))
        
        ## filter only the currency with USDT
        actual_register = list (filter((lambda x: (x.get('symbol').find('USDT')) != -1), actual_register))
        ## baptize the set with a timestamp
        for i in actual_register:
            i.update({"time": actual_timestamp})

        global REGISTER_NOTIFICATION
        if(not REGISTER_NOTIFICATION): #empty list of last value, set the actual
            REGISTER_NOTIFICATION = actual_register
        else:
            known_currencies = list (map((lambda x: x.get('symbol')), REGISTER_NOTIFICATION))
            new_ones = list (filter((lambda x: x.get('symbol') not in known_currencies), actual_register))
            if(len(new_ones)>0):
                print("Nuove monete: "+str(new_ones))
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

        if(MODE=='UltimoPrezzo'):
            REGISTER_NOTIFICATION= actual_register
        
        time.sleep(SLEEP_TIME)
        print("...................\n\n\n")
        # else:
        #     time.sleep(1590) # wait ah hour



#############################################################################

def main():
    loadConfig()
    print("Programma avviato - modalità: "+MODE)
    start()

main()