
import pandas as pd
from .api_client import get_json, get_text, to_float

def binance_24h(symbol):
    data = get_json(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}")
    if not data:
        return None
    return {
        "symbol": symbol,
        "price": to_float(data.get("lastPrice")),
        "change_24h": to_float(data.get("priceChangePercent")),
        "quote_volume": to_float(data.get("quoteVolume")),
        "source": "Binance"
    }

def eth_btc():
    return binance_24h("ETHBTC")

def fear_greed():
    data = get_json("https://api.alternative.me/fng/?limit=1")
    try:
        x = data["data"][0]
        return {"value": int(x["value"]), "label": x["value_classification"], "source": "Alternative.me"}
    except Exception:
        return {"value": None, "label": "資料不足", "source": "Alternative.me"}

def coingecko_global():
    data = get_json("https://api.coingecko.com/api/v3/global")
    try:
        d = data["data"]
        return {
            "btc_d": to_float(d["market_cap_percentage"].get("btc")),
            "eth_d": to_float(d["market_cap_percentage"].get("eth")),
            "total_market_cap": to_float(d["total_market_cap"].get("usd")),
            "total_volume": to_float(d["total_volume"].get("usd")),
            "market_change_24h": to_float(d.get("market_cap_change_percentage_24h_usd")),
            "source": "CoinGecko"
        }
    except Exception:
        return {"btc_d": None, "eth_d": None, "total_market_cap": None, "total_volume": None, "market_change_24h": None, "source": "CoinGecko"}

def stablecoins():
    data = get_json("https://stablecoins.llama.fi/stablecoins?includePrices=true")
    if not data or "peggedAssets" not in data:
        return {"total": None, "items": [], "source": "DefiLlama"}
    total = 0
    rows = []
    wanted = {
        "Tether": "USDT",
        "USD Coin": "USDC",
        "USDe": "USDe",
        "First Digital USD": "FDUSD",
        "Dai": "DAI"
    }
    for item in data.get("peggedAssets", []):
        val = to_float(item.get("circulating", {}).get("peggedUSD")) or 0
        total += val
        if item.get("name") in wanted:
            rows.append({"symbol": wanted[item.get("name")], "value": val})
    return {"total": total, "items": rows, "source": "DefiLlama"}

def categories():
    data = get_json("https://api.coingecko.com/api/v3/coins/categories")
    if not isinstance(data, list):
        return []
    aliases = {
        "Artificial Intelligence (AI)": "AI",
        "Real World Assets (RWA)": "RWA",
        "Decentralized Finance (DeFi)": "DeFi",
        "Meme": "MEME",
        "Gaming (GameFi)": "Gaming",
        "Layer 1 (L1)": "Layer1",
        "Layer 2 (L2)": "Layer2",
        "Decentralized Physical Infrastructure (DePIN)": "DePIN",
        "Infrastructure": "Infrastructure"
    }
    rows = []
    for x in data:
        if x.get("name") in aliases:
            rows.append({
                "sector": aliases[x.get("name")],
                "change_24h": to_float(x.get("market_cap_change_24h")),
                "market_cap": to_float(x.get("market_cap")),
                "volume_24h": to_float(x.get("volume_24h")),
                "top_3": ", ".join(x.get("top_3_coins", [])) if isinstance(x.get("top_3_coins"), list) else "",
                "source": "CoinGecko"
            })
    return rows

def futures_row(symbol):
    funding = get_json(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1")
    oi = get_json(f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}")
    f = None
    o = None
    try:
        f = to_float(funding[0]["fundingRate"]) * 100
    except Exception:
        pass
    try:
        o = to_float(oi["openInterest"])
    except Exception:
        pass
    return {"symbol": symbol, "funding_pct": f, "open_interest": o, "source": "Binance Futures"}

def macro():
    out = {}
    for name, sym in {"DXY": "dxy", "Nasdaq": "^ndq"}.items():
        try:
            txt = get_text(f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv")
            from io import StringIO
            df = pd.read_csv(StringIO(txt))
            out[name] = to_float(df.iloc[0]["Close"])
        except Exception:
            out[name] = None
    return out

def fetch_all():
    return {
        "prices": [binance_24h(s) for s in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]],
        "ethbtc": eth_btc(),
        "fear": fear_greed(),
        "global": coingecko_global(),
        "stablecoins": stablecoins(),
        "categories": categories(),
        "futures": [futures_row(s) for s in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]],
        "macro": macro()
    }
