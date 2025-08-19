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

# def getPropose(from_curr, to_curr, amount):
    

#     # Send POST request
#     response = requests.post(URL_PROPOSE, headers=headers, data=params)

#     return response.json()

def getPropose(headers,params):
    

    # Send POST request
    response = requests.post(URL_PROPOSE, headers=headers, data=params)

    return response.json()


def acceptPropose(from_curr, to_curr, amount):
    
    
    # Parameters for convert
    params = {
        'fromAsset': from_curr,
        'toAsset': to_curr,
        'fromAmount': amount,
        'timestamp': int(time.time() * 1000),
        'recvWindow': 5000
    }

    # Create query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])

    # Generate HMAC SHA256 signature
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    # Add signature to parameters
    params['signature'] = signature

    # Set headers
    headers = {
        'X-MBX-APIKEY': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    dummy_propose = getPropose(headers,params)
    print(dummy_propose)
    print(dummy_propose.get("quoteId"))

    response = requests.post(URL_ACCEPT, headers=headers, data={
        "quoteId": dummy_propose.get("quoteId")
    })
    print(response.text)

    pass

acceptPropose("BTC","USDC",0.000008)