import requests

def calcola_affidabilita_binance(symbol="DOGEUSDT", interval="1h", limit=300):
    """
    Scarica le ultime candele da Binance e restituisce un punteggio di affidabilità in %.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    resp = requests.get(url, params=params)
    data = resp.json()

    if not data:
        return None

    scores = []
    closes = []
    vols = []

    # estrai chiusura, high, low, volume
    for c in data:
        ts, o, h, l, close, vol, close_time, qav, trades, tb_base_av, tb_quote_av, ignore = c
        closes.append(float(close))
        vols.append(float(vol))

    media_vol = sum(vols) / len(vols)

    # calcolo score per ogni candela (tranne la prima)
    for i in range(1, len(data)):
        ts, o, h, l, close, vol, *_ = data[i]
        prev_close = float(closes[i-1])
        high = float(h)
        low = float(l)
        close = float(close)
        vol = float(vol)

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

        # 4. Candela confermata (su Binance tutte le candele restituite sono confermate)
        score += 1

        # Normalizza su 100%
        percent = (score / 4) * 100
        scores.append(percent)

    # restituisco media affidabilità ultime candele
    affidabilita_media = sum(scores) / len(scores)
    return round(affidabilita_media, 2)

# Esempio di utilizzo
aff = calcola_affidabilita_binance("DOGEU", "1h", 300)
print(f"Affidabilità media su Binance: {aff}%")