import requests
import datetime
import json
import time
import telegramTalker # import TelegramTalker
import binanceConverter
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
EQUAL_COUNTER = -1

CONVERT_AMOUNT = 0 ## TO BUY
CONVERT_SYMBOL = "" ## TO BUY

TO_IGNORE = []

SELLING_PERCENTAGE = -1

REGISTER_GLOBAL = list()

WALLET = list()
############################################################################################################################################

def loadConfig():
    global SLEEP_TIME
    global TELEGRAM_TOKEN
    global INCREMENT_COUNTER
    global INCREMENT_PERCENTAGE
    global LOSS_PERCENTAGE
    global TO_IGNORE
    global EQUAL_COUNTER
    global SELLING_PERCENTAGE
    global CONVERT_AMOUNT 
    global CONVERT_SYMBOL 


    x = loadJSON('./Normalized_Config.json') #config

    SLEEP_TIME = x.get("SecondiAggiornamento")
    TELEGRAM_TOKEN = x.get("TELEGRAMTOKEN")
    INCREMENT_COUNTER  = x.get("ContatoreIncremento")
    INCREMENT_PERCENTAGE  = x.get("PercentualeIncremento")
    LOSS_PERCENTAGE = x.get("PercentualePerdita")
    TO_IGNORE = x.get("DaIgnorare")
    EQUAL_COUNTER = x.get("ContatoreUguale")
    SELLING_PERCENTAGE = x.get("PercentualeVendita")
    CONVERT_AMOUNT = x.get("CONVERT_AMOUNT")
    CONVERT_SYMBOL = x.get("CONVERT_SYMBOL")



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
        # time.sleep(5)
        # doRequest(endpoint)

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

def getSymbolWOBase(symbol):
    print(symbol)
    indxBase=0
    try:
        indxBase = symbol.index("USD")
    except Exception:
        indxBase = symbol.index("BTC")
    
    return symbol[0:indxBase]


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


                increment = round( ((data.get("price")-data.get("historyPurchasing"))/data.get("price")*100), 2)


                if(i.get("flag")==0):
                    print("🟥",data.get("symbol"),str(increment))
                    symbol = "🟥"
                    symbol += "<b><a href='"+(BASE_URI_CONVERT +  dummy_symbol[0:indexUSD] + "/" +dummy_symbol[indexUSD:len(dummy_symbol)])
                    symbol += "'>"+dummy_symbol+"</a></b> " + data.get("sell_cause")+ "  "
                else:
                    print("🟢",data.get("symbol"), str(increment))
                    symbol = "🟢"
                    symbol += "<b><a href='"+(BASE_URI_CONVERT + dummy_symbol[indexUSD:len(dummy_symbol)] + "/" +  dummy_symbol[0:indexUSD])
                    symbol += "'>"+dummy_symbol+"</a></b> "


                strTMP += symbol 
                strTMP += str(data.get("price"))  
                if(i.get("flag")==0):
                    strTMP += " // "+str(data.get("historyMaxPrice")) +"("+ str(data.get("historyPurchasing")) +")  <b>" + format(increment)+"%</b> "
                else:
                    strTMP += "  <i>" + format(increment)+"%</i>"

                strTMP += " || " + format(convertUnix2HumanTime(data.get("time"))) +" \n"

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
                        percentageIncrement = ((new_price-max_price)/ max_price) * 100 ## MAX_PRICE aka prezzo alto
                    except Exception as e:
                        percentageIncrement = 0 #ignoring the division by 0

                    #############################~#############################~#############################    
                    incrementCounter = int(i.get("INCREMENT_COUNTER"))
                    equal_counter = int(i.get("equal_counter"))
                    isPurchased = i.get("isPurchased")

                    notifyExchange=0

                    historyMaxPrice = i.get("historyMaxPrice")
                    historyPurchasing = i.get("historyPurchasing")

                    sell_cause = None

                    earningPercentage = 0
                    if(historyPurchasing != None):
                        earningPercentage = (new_price-historyPurchasing)/historyPurchasing * 100 ## CASE 0 - TICK  PERCENTAGE 

                    if(earningPercentage>=SELLING_PERCENTAGE and isPurchased):
                        notifyExchange=-1
                        # max_price=None
                        incrementCounter=0
                        equal_counter=0
                        isPurchased=False

                        sell_cause="Top"
                        ### CONVERT - OUTCOME::SELL
                        if(getSymbolWOBase(symbol) in WALLET): ## if still on wallet, to avoid the double sell that would go to error dued to double couple USDT and USD
                            binanceConverter.acceptPropose(getSymbolWOBase(symbol),CONVERT_SYMBOL,binanceConverter.getAmount(getSymbolWOBase(symbol)))
                            WALLET.remove(getSymbolWOBase(symbol))
                    elif(percentageIncrement>INCREMENT_PERCENTAGE): # Up the increment counter - currency is growning ## ~ se PREZZO ATTUALE > del 0,5% di PREZZO ALTO :  # case 1
                        incrementCounter += 1 #if up, increment the counter -- contatore notifica
                        max_price=new_price ## update max_price
                        historyMaxPrice=new_price
                        equal_counter = 0
                    elif(new_price>max_price and percentageIncrement<=INCREMENT_PERCENTAGE): ## case 2 
                        incrementCounter=0
                        max_price=new_price ## update max_price
                        historyMaxPrice=new_price
                        equal_counter = 0
                    elif(new_price==max_price): ##EQUAL no increment, no loss
                        equal_counter += 1
                        incrementCounter=0
                    
                    elif((-1*percentageIncrement>=LOSS_PERCENTAGE) and isPurchased): ## case 4, in this case we sell the purchased symbol ## OUTCOME::SELL
                        print("VENDO: ", symbol, " - causa percentuale increment minore") 
                        sell_cause="Perc"

                        notifyExchange=-1
                        max_price=None
                        incrementCounter=0
                        equal_counter=0
                        isPurchased=False
                        ### CONVERT - SELL
                        if(getSymbolWOBase(symbol) in WALLET): ## if still on wallet, to avoid the double sell that would go to error dued to double couple USDT and USD
                            binanceConverter.acceptPropose(getSymbolWOBase(symbol),CONVERT_SYMBOL,binanceConverter.getAmount(getSymbolWOBase(symbol)))
                            WALLET.remove(getSymbolWOBase(symbol))
                    elif(new_price<max_price and isPurchased):
                        incrementCounter=0
                        equal_counter+=1
                        new_price<max_price



                    ## Notifying
                    if(incrementCounter==INCREMENT_COUNTER and not isPurchased): #OUTCOME::BUY
                        notifyExchange=1
                        equal_counter=0
                        isPurchased=True
                        incrementCounter=0
                        historyPurchasing=new_price
                        ### CONVERT - BUY
                        dummyValue=getSymbolWOBase(symbol)
                        print(dummyValue)
                        if(dummyValue not in WALLET):
                            print("ACQUISTO",getSymbolWOBase(symbol))
                            binanceConverter.acceptPropose(CONVERT_SYMBOL,getSymbolWOBase(symbol), CONVERT_AMOUNT)
                            WALLET.append(dummyValue)

                    elif(equal_counter==EQUAL_COUNTER and isPurchased): #OUTCOME::SELL
                        print("VENDO: ", symbol, " - causa contatore UGUALE PER "+str(equal_counter)+" VOLTE") 
                        sell_cause="Ugual"

                        notifyExchange=-1
                        max_price=None
                        incrementCounter=0
                        equal_counter=0
                        isPurchased=False
                        ### CONVERT - SELL
                        if(getSymbolWOBase(symbol) in WALLET): ## if still on wallet, to avoid the double sell that would go to error dued to double couple USDT and USD
                            binanceConverter.acceptPropose(getSymbolWOBase(symbol),CONVERT_SYMBOL,binanceConverter.getAmount(getSymbolWOBase(symbol)))
                            WALLET.remove(getSymbolWOBase(symbol))
                    REGISTER_GLOBAL[indx] = {
                        "symbol":symbol,
                        "time": getUnixtime(),
                        "sell_cause": sell_cause,
                        "price":new_price, 
                        "equal_counter": equal_counter,
                        "max_price":max_price, 
                        "increment":percentageIncrement,
                        "INCREMENT_COUNTER": incrementCounter,
                        "notifyExchange": notifyExchange,
                        "isPurchased": isPurchased,
                        "historyMaxPrice": historyMaxPrice,
                        "historyPurchasing": historyPurchasing
                    }

    except Exception as e:
        print("ERROR: ", e)
        pass


def start():
    print("Binance normalized avviato.")
    counter = 0
    while True:
        actual_register = doRequest("ticker/price")
        # actual_register = list (filter((lambda x:  (x.get('symbol').find('USDC')) != -1 or (x.get('symbol').find('USDT')) != -1 or (x.get('symbol')[-3:]) == "BTC"  ), actual_register)) ## filter only the currency with USDC
        actual_register = list (filter((lambda x:  (x.get('symbol').find('USDC')) != -1 or (x.get('symbol').find('USDT')) != -1   ), actual_register)) ## filter only the currency with USDC

        print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.datetime.now()))

        ## ADDED LATELY: removing unwanted symbols
        for x in actual_register:
            if(x.get("symbol") in TO_IGNORE):
                actual_register.remove(x)

        actual_timestamp = getUnixtime()

        ## baptize the set with a timestamp
        for i in actual_register:
            i.update({"time": actual_timestamp})
            i.update({"INCREMENT_COUNTER": 0, "equal_counter":0}) # init


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
            dummyverse= i.get("notifyExchange")
            if(dummyverse==1): #to notify with profit
                notificationMessage.append({"cur": i, "flag": 1})
            elif(dummyverse==-1): #to notify with loss
                notificationMessage.append({"cur": i, "flag": 0})
          
        if(len(notificationMessage)==0):
            print("Attendi...")
            pass
        else:
            print("Messaggio inviato")
        print("................................................")
        sendAlert(notificationMessage)

        time.sleep(SLEEP_TIME)


#############################################################################

loadConfig()
start()

