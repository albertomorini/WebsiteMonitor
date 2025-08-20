import time
import hmac
import hashlib
import requests
import json

config_file = open("./API_CONVERT.json",'r')
config = json.loads(config_file.read())
API_KEY = config.get("API_KEY")
API_SECRET = config.get("API_SECRET")


URL_PROPOSE = 'https://api.binance.com/sapi/v1/convert/getQuote'
URL_ACCEPT = 'https://api.binance.com/sapi/v1/convert/acceptQuote'
URL_FULLAMOUNT="https://api.binance.com/api/v3/account"

# Set headers
HEADERS = {
    'X-MBX-APIKEY': API_KEY,
    'Content-Type': 'application/x-www-form-urlencoded'
}

def getTimestamp():
    return int(time.time() * 1000)

###################################################################################

## TO RETRIEVE THE FULL AMOUNT OF SELECTED CURRENCY
## @selectedCur string - the symbol (BTC,USDC,....)
def getAmount(selectedCur):

    query_string = f"timestamp={getTimestamp()}&recvWindow=5000"

    # Create signature
    signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    final_uri = URL_FULLAMOUNT + "?"+query_string+"&signature="+signature

    response = requests.get(final_uri, headers=HEADERS)
    wallet = response.json()
    for cur in wallet.get("balances"): ## all currences
        if(cur.get("asset")==selectedCur):
            return cur.get("free")

def getPropose(from_curr, to_curr, amount):
    try:
        # BODY OF REQUEST
        params = {
            'fromAsset': from_curr,
            'toAsset': to_curr,
            'fromAmount': amount,
            'timestamp': getTimestamp(),
            'recvWindow': 5000
        }

        # Create query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])

        # Generate HMAC SHA256 signature
        signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

        params['signature'] = signature ## ADD THE SIGNATURE

        # Send POST request
        response = requests.post(URL_PROPOSE, headers=HEADERS, data=params)

        return response.json()
    except Exception as e:
        print(e)


def acceptPropose(from_curr, to_curr, amount):
    try:
        dummy_propose = getPropose(from_curr, to_curr, amount)
        dummy_quoteId = dummy_propose.get("quoteId")

        print(dummy_propose)

        bodyAccept = {
            "quoteId": dummy_quoteId,
            'timestamp': getTimestamp(),
        }
        query_string = '&'.join([f"{k}={v}" for k, v in bodyAccept.items()])
        signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        bodyAccept['signature'] = signature
        

        response = requests.post(URL_ACCEPT, headers=HEADERS, data=bodyAccept)
        if(response.status_code==200):
            print(response.json())
        else:
            print(response.text)
    except Exception as e:
        print(e)


# acceptPropose("BTC","USDC",0.000008)
acceptPropose("USDC","BTC",getAmount("USDC"))
# getAmount("BTC")
