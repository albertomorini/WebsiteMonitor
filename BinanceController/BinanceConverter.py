# # import requests
# # import time
# # import hashlib
# # import hmac

# # # Your Binance API keys
# # api_key = 'your_api_key'
# # api_secret = 'your_api_secret'

# # # Base URL for the API
# # base_url = 'https://api.binance.com'

# # # Define the conversion parameters
# # from_asset = 'BTC'  # The asset you are converting from
# # to_asset = 'USDT'   # The asset you are converting to
# # amount = 0.1        # The amount to convert

# # # Generate the timestamp and signature
# # timestamp = str(int(time.time() * 1000))
# # params = {
# #     'fromAsset': from_asset,
# #     'toAsset': to_asset,
# #     'amount': amount,
# #     'timestamp': timestamp
# # }

# # # Create the query string
# # query_string = '&'.join([f"{key}={value}" for key, value in params.items()])

# # # Create the signature
# # signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# # # Add the signature to the parameters
# # params['signature'] = signature

# # # Headers for authentication
# # headers = {
# #     'X-MBX-APIKEY': api_key
# # }

# # # Send the POST request
# # response = requests.post(f"{base_url}/v3/asset/convert", headers=headers, params=params)

# # # Check the response
# # if response.status_code == 200:
# #     print("Conversion successful:", response.json())
# # else:
# #     print(f"Error: {response.status_code}, {response.json()}")



import requests
import time
import hashlib
import hmac


api_key = 'your_api_key'
api_secret = 'your_api_secret'
base_url = 'https://api.binance.com'

##################################################################################3

def getTimestamp():
    return str(int(time.time() * 1000))


def doConversion(curr_start,curr_end,amount):
    ### PARAMS
    params = params = {
        'fromAsset': curr_start,
        'toAsset': curr_end,
        'amount': amount,
        'timestamp': timestamp
    }
    
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature

    ### HEADERS
    headers = {
        'X-MBX-APIKEY': api_key
    }

    ## DO REQUEST
    response = requests.post(f"{base_url}/v3/asset/convert", headers=headers, params=params)

    if response.status_code == 200:
        print("Conversion successful:", response.json())
    else:
        print(f"Error: {response.status_code}, {response.json()}")