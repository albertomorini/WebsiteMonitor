

import requests




TOKEN = ""

HEADERS = dict()
HEADERS["Content-Type"] = "application/json"



BASE_URI="https://api.telegram.org/bot"


def loadToken(path="./TelegramToken.txt"):
    token_file = open(path,"r")
    global TOKEN
    TOKEN = token_file.read()
    token_file.close()


def getAllSubscribed():
    URL = BASE_URI+TOKEN+"/getUpdates"
    print(URL)
    res = requests.get(URL).json()
    print(res)
    ids = list()
    for chatId in res.get("result"):
        ids.append(chatId.get("message").get("from").get("id"))
    
    return ids


def sendMessage(message):
    chat_ids = getAllSubscribed()
    print(chat_ids)
    for id in chat_ids:
        url = BASE_URI+TOKEN+f"/sendMessage?chat_id={id}&text={message}&parse_mode=HTML"
        print(requests.get(url).json()) # this sends the message



loadToken()