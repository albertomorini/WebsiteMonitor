import requests
import time
import base64
import hmac
import hashlib
import json

from datetime import datetime, timezone

config_file = open("./API_CONVERT.json",'r')
config = json.loads(config_file.read())
API_KEY = config.get("API_KEY")
API_SECRET = config.get("API_SECRET")
PASSPHRASE = config.get("PASSPHRASE")



def get_okx_headers(method, request_path, body=""):
    timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    message = f"{timestamp}{method}{request_path}{body}"

    signature = base64.b64encode(
        hmac.new(
            API_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    return {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }

def get_amount(selected_cur):

    if("-" in selected_cur): ## se passo la coppia BASE-QUOTE splitto prendendo la BASE
        selected_cur = selected_cur.split("-")[0]

    headers = get_okx_headers(
        method="GET",
        request_path="/api/v5/account/balance"
    )

    response = requests.get(
        "https://eea.okx.com/api/v5/account/balance",
        headers=headers
    )

    wallet = response.json()

    if wallet.get("code") != "0":
        raise Exception(wallet)

    balances = wallet["data"][0]["details"]

    for balance in balances:
        if balance["ccy"] == selected_cur:
            return balance["availBal"]

    return "0"

def create_spot_order(inst_id, side, size, order_type="market", tgt_ccy="base_ccy"):

    request_path = "/api/v5/trade/order"

    body = {
        "instId": inst_id, #The trading pair (instrument ID) / "BTC-USDT"
        "tdMode": "cash",
        "side": side, # Whether you're buying or selling "buy" or "sell"
        "ordType": order_type, # Type of order / "market" or "limit"
        "sz": str(size), # Amount to trade 0.01 or 100
        "tgtCcy": tgt_ccy # Which currency size refers to "base_ccy" or "quote_ccy"
    }

    body_json = json.dumps(body)

    headers = get_okx_headers(
        method="POST",
        request_path=request_path,
        body=body_json
    )

    response = requests.post(
        "https://eea.okx.com" + request_path,
        headers=headers,
        data=body_json
    )

    result = response.json()

    if result.get("code") != "0":
        raise Exception(result)

    return result["data"][0]
