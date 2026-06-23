
def clamp(x):
    if x is None:
        return None
    return max(0, min(100, round(x)))

def avg(vals):
    vals = [v for v in vals if v is not None]
    return None if not vals else sum(vals) / len(vals)

def score_change(x):
    if x is None:
        return None
    if x >= 5: return 100
    if x >= 3: return 90
    if x >= 1: return 75
    if x >= 0: return 60
    if x >= -1: return 40
    if x >= -3: return 25
    return 10

def score_fear(v):
    if v is None:
        return None, None
    if 45 <= v <= 75:
        return 80, 30
    if v > 80:
        return 55, 75
    if v < 30:
        return 30, 75
    return 55, 50

def score_funding(x):
    if x is None:
        return None
    ax = abs(x)
    if ax <= 0.01: return 85
    if ax <= 0.03: return 65
    if ax <= 0.06: return 45
    return 20

def score_sector(row):
    ch = row.get("change_24h")
    vol = row.get("volume_24h")
    cap = row.get("market_cap")
    momentum = score_change(ch)
    ratio_score = 50
    if vol and cap:
        r = vol / cap
        if r > 0.2: ratio_score = 90
        elif r > 0.08: ratio_score = 75
        elif r > 0.03: ratio_score = 60
        else: ratio_score = 40
    return clamp((momentum or 50) * 0.7 + ratio_score * 0.3)

def compact(x):
    if x is None:
        return "資料不足"
    if x >= 1_000_000_000_000: return f"${x/1_000_000_000_000:.2f}T"
    if x >= 1_000_000_000: return f"${x/1_000_000_000:.2f}B"
    if x >= 1_000_000: return f"${x/1_000_000:.2f}M"
    return f"${x:,.0f}"

def score_dashboard(data):
    prices = {x["symbol"]: x for x in data["prices"] if x}
    btc = prices.get("BTCUSDT", {})
    eth = prices.get("ETHUSDT", {})
    sol = prices.get("SOLUSDT", {})
    ethbtc = data.get("ethbtc") or {}
    g = data.get("global") or {}
    fear = data.get("fear") or {}
    stable = data.get("stablecoins") or {}
    futures = data.get("futures") or []

    btc_score = score_change(btc.get("change_24h"))
    ethbtc_score = score_change(ethbtc.get("change_24h"))
    total_score = score_change(g.get("market_change_24h"))
    sol_score = score_change(sol.get("change_24h"))

    fear_bull, fear_bear = score_fear(fear.get("value"))

    btc_d = g.get("btc_d")
    btc_d_alt = None
    if btc_d is not None:
        btc_d_alt = 100 if btc_d < 50 else 75 if btc_d < 55 else 45 if btc_d < 60 else 20

    funding_scores = [score_funding(x.get("funding_pct")) for x in futures]
    funding_score = avg(funding_scores)

    sector_rows = []
    sector_scores = []
    for row in data.get("categories", []):
        s = score_sector(row)
        sector_scores.append(s)
        sector_rows.append({
            "板塊": row["sector"],
            "分數": s if s is not None else "資料不足",
            "24H變化%": round(row["change_24h"], 2) if row.get("change_24h") is not None else "資料不足",
            "成交量": compact(row.get("volume_24h")),
            "市值": compact(row.get("market_cap")),
            "代表幣": row.get("top_3", "")
        })
    sector_rows = sorted(sector_rows, key=lambda x: -1 if isinstance(x["分數"], str) else -x["分數"])

    sector_score = avg(sector_scores)
    stable_score = 55 if stable.get("total") else None

    macro_score = 55 if any(v is not None for v in (data.get("macro") or {}).values()) else None

    bull = clamp(avg([btc_score, ethbtc_score, total_score, fear_bull, sector_score, stable_score, funding_score, macro_score]))
    bear = clamp(avg([
        100 - btc_score if btc_score is not None else None,
        100 - ethbtc_score if ethbtc_score is not None else None,
        fear_bear,
        100 - total_score if total_score is not None else None,
        100 - funding_score if funding_score is not None else None
    ]))
    alt = clamp(avg([ethbtc_score, btc_d_alt, total_score, sol_score, sector_score, stable_score]))
    market = clamp(avg([bull, 100 - bear if bear is not None else None, alt]))

    return {
        "market": market,
        "bull": bull,
        "bear": bear,
        "alt": alt,
        "sector_rows": sector_rows,
        "funding_score": clamp(funding_score)
    }

def decision(scores):
    m = scores.get("market")
    bull = scores.get("bull") or 0
    bear = scores.get("bear") or 0
    if m is None:
        return "資料不足", "⚪ 資料不足｜今日不依賴系統分數交易。", "0%", "☆☆☆☆☆"
    if m >= 80 and bull > bear:
        return "Risk ON", f"🟢 Risk ON｜市場總分 {m}/100｜偏多操作，等待回踩，不追價。", "2~3%", "★★★★★"
    if m >= 60:
        return "震盪偏多", f"🟡 震盪偏多｜市場總分 {m}/100｜只做 A+ 訊號。", "1~2%", "★★★★☆"
    if m >= 40:
        return "震盪", f"🟡 震盪｜市場總分 {m}/100｜降低交易頻率。", "1%", "★★★☆☆"
    return "Risk OFF", f"🔴 Risk OFF｜市場總分 {m}/100｜保護本金，不做多山寨。", "0~1%", "★☆☆☆☆"
