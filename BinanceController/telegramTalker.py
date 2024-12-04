import requests

# https://stackoverflow.com/questions/67471470/telegram-bot-getupdates-does-not-contain-data

HEADERS = dict()
HEADERS["Content-Type"] = "application/json"

BASE_URI="https://api.telegram.org/bot"


def getAllSubscribed(token):
    URL = BASE_URI+token+"/getUpdates"
    res = requests.get(URL).json()
    # print(res)
    ids = list()
    for chatId in res.get("result"):
        try:
            ids.append(chatId.get("message").get("from").get("id"))
        except Exception:
            print("Nessun utente iscritto al bot")
            return []
    
    return ids


def sendMessage(token,message):
    chat_ids = set(getAllSubscribed(token))
    print(chat_ids)
    for id in chat_ids:
        url = BASE_URI+token+f"/sendMessage?chat_id={id}&text={message}&parse_mode=HTML"
        print(requests.get(url).json()) # this sends the message

print(getAllSubscribed("7716948042:AAEzTwh_SzMfjysg-ptxm8GN7EoaHf1haJU"))