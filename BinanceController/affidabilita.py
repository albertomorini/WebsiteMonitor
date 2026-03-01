import requests

def calcola_affidabilita(instId="DOGE-USDT", bar="1H", limit=300):
    """
    Scarica le ultime candele da OKX e restituisce un punteggio di affidabilità %.
    """
    url = "https://www.okx.com/api/v5/market/history-candles"
    params = {"instId": instId, "bar": bar, "limit": limit}

    resp = requests.get(url, params=params)
    data = resp.json()

    if "data" not in data or not data["data"]:
        return None

    candles = data["data"]

    scores = []
    closes = []
    vols = []

    # estrai chiusura, high, low, volume, confirm
    for c in candles:
        ts, o, h, l, close, vol, volCcy, volCcyQuote, confirm = c
        closes.append(float(close))
        vols.append(float(vol))

    media_vol = sum(vols) / len(vols)

    # calcolo score per ogni candela (tranne la prima, che non ha precedente)
    for i in range(1, len(candles)):
        ts, o, h, l, close, vol, volCcy, volCcyQuote, confirm = candles[i]
        prev_close = float(closes[i-1])
        high = float(h)
        low = float(l)
        close = float(close)
        vol = float(vol)
        confirm = int(confirm)

        score = 0

        # 1. Momentum positivo
        if close > prev_close:
            score += 1

        # 2. Range basso (meno dell'1% del close)
        if (high - low)/close < 0.01:
            score += 1

        # 3. Volume sopra la media
        if vol >= media_vol:
            score += 1

        # 4. Candela confermata
        if confirm == 1:
            score += 1

        # Normalizza su 100%
        percent = (score / 4) * 100
        scores.append(percent)

    # restituisco media affidabilità ultime candele
    affidabilita_media = sum(scores) / len(scores)
    return round(affidabilita_media, 2)

# Esempio di utilizzo
# aff = calcola_affidabilita("DOGE-USDT", "1H", 300)
# aff = calcola_affidabilita("SHIB-USDT", "1H", 300)
# aff = calcola_affidabilita("SNX-USDT", "1H", 300)
aff = calcola_affidabilita("FIOB-USD", "1H", 300)
print(f"Affidabilità media: {aff}%")