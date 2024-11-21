import requests
from bs4 import *
import hashlib
import json
from datetime import datetime
import sys
import json 
import time
import calendar
import urllib
import re
from pprint import pprint


PATHNAME_STORED= "./stored.json"
BASE_URI = 'https://api.binance.com/api/v3/'

PERCENTAGE_ALERT = 0.2

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


def compareRegisters(prev,actual):
    for i in prev: # all old currencies
        for j in actual: # all new currencies
            if(i.get("symbol")==j.get("symbol")): ## if the same check the prices
                symbol = i.get("symbol")
                old_price = float(i.get("price"))
                new_price = float(j.get("price"))
                percentage = (new_price-old_price)/ old_price * 100
                if(percentage>PERCENTAGE_ALERT):
                    print(symbol,"\t",percentage, new_price)


def start():
    registers = loadJSON()
    for i in range(0,2):
        actual_register = doRequest("ticker/price")
        print("Scaricati i prezzi di "+str(len(actual_register))+" valute","- INFO", str(datetime.now()))
        
        #compare with previous
        try:
            compareRegisters(registers[list(registers.keys())[-1]],actual_register)
        except Exception:
            pass

        registers[getUnixtime()] = actual_register #store into JSON
        time.sleep(120)
        
    # print(dummyDict)

    ff = open("stored.json","w")
    ff.write(json.dumps(registers))
    ff.close

    

start()
