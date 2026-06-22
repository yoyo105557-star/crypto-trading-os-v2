
import requests
import pandas as pd

HEADERS = {"User-Agent": "CryptoTradingOS/1.0"}

def safe_get_json(url, timeout=12):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def to_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None

def fetch_binance_24h(symbols):
    rows = []
    for symbol in symbols:
        data = safe_get_json(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}")
        if not data:
            rows.append({"symbol": symbol, "price": None, "change_24h": None, "volume": None, "quote_volume": None})
            continue
        rows.append({
            "symbol": symbol,
            "price": to_float(data.get("lastPrice")),
            "change_24h": to_float(data.get("priceChangePercent")),
            "volume": to_float(data.get("volume")),
            "quote_volume": to_float(data.get("quoteVolume"))
        })
    return rows

def fetch_eth_btc():
    data = safe_get_json("https://api.binance.com/api/v3/ticker/24hr?symbol=ETHBTC")
    if not data:
        return {"price": None, "change_24h": None}
    return {"price": to_float(data.get("lastPrice")), "change_24h": to_float(data.get("priceChangePercent"))}

def fetch_fear_greed():
    data = safe_get_json("https://api.alternative.me/fng/?limit=1")
    try:
        item = data["data"][0]
        return {"value": int(item["value"]), "classification": item["value_classification"]}
    except Exception:
        return {"value": None, "classification": "資料不足"}

def fetch_global_crypto():
    data = safe_get_json("https://api.coingecko.com/api/v3/global")
    try:
        d = data["data"]
        return {
            "btc_dominance": to_float(d["market_cap_percentage"].get("btc")),
            "eth_dominance": to_float(d["market_cap_percentage"].get("eth")),
            "total_market_cap_usd": to_float(d["total_market_cap"].get("usd")),
            "total_volume_usd": to_float(d["total_volume"].get("usd")),
            "market_cap_change_24h": to_float(d.get("market_cap_change_percentage_24h_usd"))
        }
    except Exception:
        return {"btc_dominance": None, "eth_dominance": None, "total_market_cap_usd": None, "total_volume_usd": None, "market_cap_change_24h": None}

def fetch_coin_markets(ids):
    ids_str = ",".join(ids)
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids_str}&price_change_percentage=24h,7d"
    data = safe_get_json(url)
    out = {}
    if not isinstance(data, list):
        return out
    for item in data:
        out[item.get("id")] = {
            "market_cap": to_float(item.get("market_cap")),
            "change_24h": to_float(item.get("price_change_percentage_24h")),
            "change_7d": to_float(item.get("price_change_percentage_7d_in_currency")),
            "total_volume": to_float(item.get("total_volume"))
        }
    return out

def fetch_stablecoins():
    data = safe_get_json("https://stablecoins.llama.fi/stablecoins?includePrices=true")
    try:
        total = 0
        for item in data.get("peggedAssets", []):
            total += to_float(item.get("circulating", {}).get("peggedUSD")) or 0
        return {"total_stablecoin_mcap": total}
    except Exception:
        return {"total_stablecoin_mcap": None}

def fetch_macro_stooq():
    symbols = {"DXY": "dxy", "Nasdaq": "^ndq"}
    out = {}
    for name, sym in symbols.items():
        try:
            url = f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv"
            df = pd.read_csv(url)
            row = df.iloc[0].to_dict()
            out[name] = {"value": to_float(row.get("Close")), "raw": row}
        except Exception:
            out[name] = {"value": None, "raw": {}}
    return out

def fetch_categories():
    data = safe_get_json("https://api.coingecko.com/api/v3/coins/categories")
    if not isinstance(data, list):
        return []
    aliases = {
        "Artificial Intelligence (AI)": "AI",
        "Real World Assets (RWA)": "RWA",
        "Decentralized Finance (DeFi)": "DeFi",
        "Meme": "MEME",
        "Gaming (GameFi)": "Gaming",
        "Layer 1 (L1)": "Layer1"
    }
    rows = []
    for item in data:
        name = item.get("name")
        if name in aliases:
            rows.append({
                "sector": aliases[name],
                "source_name": name,
                "market_cap": to_float(item.get("market_cap")),
                "volume_24h": to_float(item.get("volume_24h")),
                "change_24h": to_float(item.get("market_cap_change_24h")),
                "top_3_coins": ", ".join(item.get("top_3_coins", [])) if isinstance(item.get("top_3_coins"), list) else ""
            })
    return rows
