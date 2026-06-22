import requests
import time

HEADERS = {"User-Agent": "CryptoTradingOS/1.0"}

ENDPOINTS = [
    {
        "名稱": "Binance Spot",
        "用途": "BTC/ETH/SOL 即時價格、24H漲跌",
        "網址": "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
    },
    {
        "名稱": "Binance Futures",
        "用途": "Funding Rate / Open Interest",
        "網址": "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"
    },
    {
        "名稱": "CoinGecko Global",
        "用途": "BTC Dominance、總市值、全市場變化",
        "網址": "https://api.coingecko.com/api/v3/global"
    },
    {
        "名稱": "CoinGecko Categories",
        "用途": "AI / RWA / DeFi / MEME / Gaming 板塊資料",
        "網址": "https://api.coingecko.com/api/v3/coins/categories"
    },
    {
        "名稱": "Alternative Fear & Greed",
        "用途": "恐懼貪婪指數",
        "網址": "https://api.alternative.me/fng/?limit=1"
    },
    {
        "名稱": "DefiLlama Stablecoins",
        "用途": "穩定幣總市值與主要穩定幣市值",
        "網址": "https://stablecoins.llama.fi/stablecoins?includePrices=true"
    },
    {
        "名稱": "Stooq DXY",
        "用途": "美元指數 DXY",
        "網址": "https://stooq.com/q/l/?s=dxy&f=sd2t2ohlcv&h&e=csv"
    },
    {
        "名稱": "Stooq Nasdaq",
        "用途": "Nasdaq 指數",
        "網址": "https://stooq.com/q/l/?s=^ndq&f=sd2t2ohlcv&h&e=csv"
    }
]

def check_endpoint(endpoint):
    start = time.time()
    try:
        r = requests.get(endpoint["網址"], headers=HEADERS, timeout=10)
        ms = round((time.time() - start) * 1000)
        ok = 200 <= r.status_code < 300
        return {
            "API": endpoint["名稱"],
            "用途": endpoint["用途"],
            "狀態": "✅ 正常" if ok else f"⚠️ HTTP {r.status_code}",
            "延遲(ms)": ms
        }
    except Exception as e:
        return {
            "API": endpoint["名稱"],
            "用途": endpoint["用途"],
            "狀態": "❌ 失敗",
            "延遲(ms)": "-"
        }

def check_all():
    return [check_endpoint(e) for e in ENDPOINTS]
