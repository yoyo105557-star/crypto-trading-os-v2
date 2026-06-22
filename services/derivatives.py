import requests

HEADERS = {"User-Agent": "CryptoTradingOS/1.0"}

def get_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def funding_rate(symbol="BTCUSDT"):
    data = get_json(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1")
    if not data:
        return {"symbol": symbol, "funding": None}
    return {
        "symbol": symbol,
        "funding": float(data[0]["fundingRate"]) * 100
    }

def open_interest(symbol="BTCUSDT"):
    data = get_json(f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}")
    if not data:
        return {"symbol": symbol, "open_interest": None}
    return {
        "symbol": symbol,
        "open_interest": float(data["openInterest"])
    }

def derivatives_summary():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    rows = []
    for s in symbols:
        f = funding_rate(s)
        oi = open_interest(s)
        rows.append({
            "標的": s,
            "資金費率%": f["funding"],
            "未平倉量": oi["open_interest"]
        })
    return rows