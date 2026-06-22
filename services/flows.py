import requests

HEADERS = {"User-Agent": "CryptoTradingOS/1.0"}

def get_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def _usd(x):
    try:
        x = float(x)
    except Exception:
        return "資料不足"
    if x >= 1_000_000_000_000:
        return f"${x/1_000_000_000_000:.2f}T"
    if x >= 1_000_000_000:
        return f"${x/1_000_000_000:.2f}B"
    if x >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    return f"${x:,.0f}"

def stablecoin_summary():
    """
    DefiLlama stablecoins API.
    回傳總穩定幣市值，以及 USDT / USDC / USDe / FDUSD 等主要穩定幣市值。
    """
    data = get_json("https://stablecoins.llama.fi/stablecoins?includePrices=true")
    if not data or "peggedAssets" not in data:
        return [{"項目": "Stablecoin", "數值": "資料不足", "說明": "DefiLlama API 未回傳"}]

    wanted = {
        "Tether": "USDT",
        "USD Coin": "USDC",
        "USDe": "USDe",
        "First Digital USD": "FDUSD",
        "Dai": "DAI"
    }

    total = 0
    rows = []
    for item in data.get("peggedAssets", []):
        circ = item.get("circulating", {}).get("peggedUSD")
        try:
            value = float(circ)
        except Exception:
            value = 0
        total += value

        name = item.get("name")
        symbol = wanted.get(name)
        if symbol:
            rows.append({
                "項目": symbol,
                "數值": _usd(value),
                "說明": "主要穩定幣市值"
            })

    rows.insert(0, {
        "項目": "Stablecoin 總市值",
        "數值": _usd(total),
        "說明": "加密市場可用美元流動性"
    })

    return rows

def etf_flow_status():
    """
    ETF Flow 的公開資料多半來自網頁表格，格式常變動。
    這裡先不把 ETF 數字納入評分，避免錯誤資料影響交易決策。
    """
    return "ETF Flow：尚未接入穩定 API。為避免資料錯誤，目前不納入 Market Score。"
