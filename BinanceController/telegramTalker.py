import requests

import time

# https://stackoverflow.com/questions/67471470/telegram-bot-getupdates-does-not-contain-data

HEADERS = dict()
HEADERS["Content-Type"] = "application/json"

BASE_URI="https://api.telegram.org/bot"


def getAllSubscribed(token):
    URL = BASE_URI+token+"/getUpdates"
    res = requests.get(URL).json()
    ids = list()
    for chatId in res.get("result"):
        try:
            ids.append(chatId.get("message").get("from").get("id"))
        except Exception:
            # print("Nessun utente iscritto al bot")
            pass
    
    return ids

def sendMessage(token,message,guardiaFirstSend=True):
    # chat_ids = set(getAllSubscribed(token))
    # print(chat_ids)
    try:
        chat_ids = ["49797109", "6406710754"]
        for id in chat_ids:
            try:
                mydata={
                    "chat_id": id,
                    "text" : message,
                    "parse_mode": "HTML",
                    "link_preview_options":{
                        "is_disabled":True
                    }
                }
                headers = {'Authorization': f'Bearer {token}'}
                resp = requests.post(BASE_URI+token+"/sendMessage",json=mydata,headers=headers).json() # this sends the message
                print(resp)
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print("ERRORE MESSAGGIO TELEGRAM: " + str(e))
        if(guardiaFirstSend):
            time.sleep(5)
            sendMessage(token,message,False)
        else:
            pass


# print(getAllSubscribed("token"))
# sendMessage("token","test2")