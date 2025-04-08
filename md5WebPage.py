
# DO THE MD5 OF A WEBPAGE AND CHECK WITH A PREVIOUS ONE TO SEE IF SOMETHING HAS CHANGED
import requests
from bs4 import *
import hashlib
import json
import datetime
import sys


# store the webpage into the filesystem
def storeWebPage2FS(url):
    urllib.request.urlretrieve(url, doMD5(url)+".html") # saving with the hash of the url

#get the content (text) of the webpage
def getHTML(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser').get_text() # get the content (text/info/data) of the page
    return (soup)

#return the hash of MD5 function
def doMD5(val):
    return hashlib.md5(val.encode()).hexdigest()



########################################


def compareRegister():
    file = open("./register.json","r")
    register = json.load(file)  
    for i in register.keys():
        print("processing:" + i)
        currentPage = doMD5(getHTML(register[i]["URL"]))
        if(currentPage != register[i]["last_hash"]):
            print("Page changed!")
            if(register[i]["dwnChanged"]):
                storeWebPage2FS(register[i]["URL"])
        else:
            print("Page hasn't changed")
        print("\n")


# add a new website to the register (if this doesn't exists it creates one)
def addEntry(url,dwnChanged):

    try:
        file = open("./register.json", "r") # read the register to add/update the new entry
        register = json.load(file)
        file.close() # close the file thus to avoid concurrency when writing
    except:
        register= dict()
    
    # create a new entry on the dictionary of websites
    register[doMD5(url)] = {
        "URL" : url,
        "dwnChanged": dwnChanged,
        "date_last": str(datetime.datetime.now()),
        "last_hash": doMD5(getHTML(url))
    }
    
    # if dwnChanged flag is on, we download and store the page
    if(dwnChanged):
        storeWebPage2FS(url)

    # store the new register
    with open('register.json', 'w', encoding='utf-8') as f:
        json.dump(register, f, ensure_ascii=False, indent=4)
    

########################################
def main():
    if(len(sys.argv)==1):
        print("Welcome!\nMenu:")
        print("\t 1) Compare existing website")
        print("\t 2) Add a new website")
        choice = int(input("Insert your choice: "))
    else:
        choice=int(sys.argv[1])

    if(choice==1):
        compareRegister()
    elif(choice==2): #add a new entry
        url=input("Put the url of the website you want to monitor: ")
        dwnChanged = input("Download the new webpage if will change? (Yes or No)")
        addEntry(url, True if dwnChanged.upper()=="YES" else False)
        
    else:
        print("I dunno, bye!")


main()
