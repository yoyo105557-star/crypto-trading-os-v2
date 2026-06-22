
def clamp(x):
    if x is None:
        return None
    return max(0, min(100, round(x)))

def score_change(change, pos_good=True):
    if change is None:
        return None
    if pos_good:
        if change >= 3: return 100
        if change >= 1: return 80
        if change >= 0: return 60
        if change >= -1: return 40
        return 20
    else:
        if change <= -1: return 100
        if change <= 0: return 75
        if change <= 1: return 50
        return 25

def avg_available(values):
    vals = [v for v in values if v is not None]
    return None if not vals else sum(vals) / len(vals)

def compact(x):
    if x is None:
        return "資料不足"
    if x >= 1_000_000_000_000: return f"${x/1_000_000_000_000:.2f}T"
    if x >= 1_000_000_000: return f"${x/1_000_000_000:.2f}B"
    if x >= 1_000_000: return f"${x/1_000_000:.2f}M"
    return f"${x:,.0f}"

def pct_text(x):
    return "資料不足" if x is None else f"{x:.2f}%"

def price_text(x):
    return "資料不足" if x is None else f"${x:,.4f}"

def show_score(x):
    return "資料不足" if x is None else f"{x}/100"

def yesno(score, threshold):
    if score is None:
        return "資料不足"
    return "✅ 成立" if score >= threshold else "❌ 未成立"

def score_sector(row):
    ch = row.get("change_24h")
    vol = row.get("volume_24h")
    cap = row.get("market_cap")
    s1 = score_change(ch, True)
    ratio = (vol / cap) if vol and cap else None
    if ratio is None: s2 = 50
    elif ratio > 0.2: s2 = 90
    elif ratio > 0.08: s2 = 75
    elif ratio > 0.03: s2 = 60
    else: s2 = 40
    return clamp((s1 or 50) * 0.75 + s2 * 0.25)

def decision_fields(market, bull, bear):
    if market is None:
        return "資料不足", "☆☆☆☆☆", "0%", "保留現金", "❌ 否", "❌ 否", "❌ 否"
    if market >= 80 and (bull or 0) > (bear or 0):
        return "Risk ON", "★★★★★", "2~3%", "現貨60% / 合約40%", "✅ 可以", "⚠️ 只做弱勢反彈空", "✅ 限制加倉"
    if market >= 60:
        return "震盪偏多", "★★★★☆", "1~2%", "現貨70% / 合約30%", "✅ 等回踩", "⚠️ 破結構才做空", "⚠️ 僅A+"
    if market >= 40:
        return "震盪", "★★★☆☆", "1%", "現貨80% / 合約20%", "⚠️ 僅A+訊號", "⚠️ 僅A+訊號", "❌ 否"
    return "Risk OFF", "★☆☆☆☆", "0~1%", "現金/現貨為主", "❌ 否", "✅ 反彈空優先", "❌ 否"

def make_decision(state, market, risk):
    if state == "Risk ON":
        return f"🟢 {state}｜市場總分 {market}/100｜建議風險 {risk}｜偏多操作，等待回踩，不追價。"
    if state == "Risk OFF":
        return f"🔴 {state}｜市場總分 {market}/100｜建議風險 {risk}｜保護本金，不硬做多。"
    if state == "資料不足":
        return "⚪ 資料不足｜部分 API 未回傳，今日不依賴分數交易。"
    return f"🟡 {state}｜市場總分 {market}/100｜建議風險 {risk}｜只做 A+ 訊號。"

def alt_phase(score):
    if score is None: return "山寨季判斷：資料不足"
    if score >= 80: return "山寨季判斷：全面山寨季 / 擴散期"
    if score >= 65: return "山寨季判斷：初期擴散"
    if score >= 50: return "山寨季判斷：準備階段"
    return "山寨季判斷：尚未開始"

def build_dashboard(prices, eth_btc, fear, global_data, coin_markets, stable, macro, categories):
    btc = next((x for x in prices if x["symbol"] == "BTCUSDT"), {})
    eth = next((x for x in prices if x["symbol"] == "ETHUSDT"), {})
    sol = next((x for x in prices if x["symbol"] == "SOLUSDT"), {})

    btc_score = score_change(btc.get("change_24h"), True)
    ethbtc_score = score_change(eth_btc.get("change_24h"), True)
    global_score = score_change(global_data.get("market_cap_change_24h"), True)

    btc_d = global_data.get("btc_dominance")
    btc_d_score = None
    if btc_d is not None:
        btc_d_score = 100 if btc_d < 50 else 70 if btc_d < 55 else 45 if btc_d < 60 else 25

    fg = fear.get("value")
    fear_score = bear_fear_score = None
    if fg is not None:
        if 45 <= fg <= 75:
            fear_score, bear_fear_score = 80, 30
        elif fg > 80:
            fear_score, bear_fear_score = 55, 70
        elif fg < 30:
            fear_score, bear_fear_score = 30, 75
        else:
            fear_score, bear_fear_score = 55, 50

    dxy = macro.get("DXY", {}).get("value")
    nasdaq = macro.get("Nasdaq", {}).get("value")
    macro_score = 55 if (dxy is not None or nasdaq is not None) else None
    stable_score = 55 if stable.get("total_stablecoin_mcap") else None

    sector_rows = []
    sector_scores = []
    for row in categories:
        s = score_sector(row)
        sector_scores.append(s)
        sector_rows.append({
            "排名": None,
            "板塊": row["sector"],
            "分數": s if s is not None else "資料不足",
            "24H市值變化%": round(row["change_24h"], 2) if row.get("change_24h") is not None else "資料不足",
            "24H成交量": compact(row.get("volume_24h")),
            "代表幣": row.get("top_3_coins", "")
        })
    sector_rows = sorted(sector_rows, key=lambda x: -1 if isinstance(x["分數"], str) else -x["分數"])
    for i, r in enumerate(sector_rows, 1):
        r["排名"] = i

    sector_score = avg_available(sector_scores)
    bull_score = clamp(avg_available([btc_score, ethbtc_score, fear_score, global_score, macro_score, stable_score, sector_score]))
    bear_score = clamp(avg_available([
        100 - btc_score if btc_score is not None else None,
        100 - ethbtc_score if ethbtc_score is not None else None,
        bear_fear_score,
        100 - global_score if global_score is not None else None
    ]))
    altseason_score = clamp(avg_available([
        ethbtc_score,
        btc_d_score,
        global_score,
        stable_score,
        sector_score,
        score_change(sol.get("change_24h"), True)
    ]))
    market_score = clamp(avg_available([
        bull_score,
        100 - bear_score if bear_score is not None else None,
        altseason_score
    ]))

    state, stars, risk, allocation, allow_long, allow_short, pyramid = decision_fields(market_score, bull_score, bear_score)

    macro_rows = [
        {"指標": "DXY 美元指數", "數值": round(dxy, 2) if dxy is not None else "資料不足", "判斷": "已連接資料源；趨勢判斷待加入歷史資料"},
        {"指標": "Nasdaq", "數值": round(nasdaq, 2) if nasdaq is not None else "資料不足", "判斷": "已連接資料源；趨勢判斷待加入歷史資料"},
        {"指標": "恐懼貪婪", "數值": fg if fg is not None else "資料不足", "判斷": fear.get("classification", "資料不足")}
    ]
    crypto_rows = [
        {"指標": "BTC價格", "數值": price_text(btc.get("price")), "判斷": pct_text(btc.get("change_24h"))},
        {"指標": "ETH價格", "數值": price_text(eth.get("price")), "判斷": pct_text(eth.get("change_24h"))},
        {"指標": "SOL價格", "數值": price_text(sol.get("price")), "判斷": pct_text(sol.get("change_24h"))},
        {"指標": "ETH/BTC", "數值": eth_btc.get("price") or "資料不足", "判斷": pct_text(eth_btc.get("change_24h"))},
        {"指標": "BTC Dominance", "數值": f"{btc_d:.2f}%" if btc_d is not None else "資料不足", "判斷": "越低越利於山寨輪動"},
        {"指標": "Stablecoin MC", "數值": compact(stable.get("total_stablecoin_mcap")), "判斷": "已連接 DefiLlama"},
        {"指標": "TOTAL市值24H", "數值": compact(global_data.get("total_market_cap_usd")), "判斷": pct_text(global_data.get("market_cap_change_24h"))}
    ]
    alt_rows = [
        {"條件": "BTC是否橫盤", "狀態": "資料不足：需加入K線波動率"},
        {"條件": "ETH是否強於BTC", "狀態": yesno(ethbtc_score, 60)},
        {"條件": "BTC.D是否下降/低位", "狀態": yesno(btc_d_score, 60)},
        {"條件": "TOTAL是否擴張", "狀態": yesno(global_score, 60)},
        {"條件": "Stablecoin是否流入", "狀態": "中性：目前僅抓總市值"},
        {"條件": "成交量是否擴大", "狀態": "資料不足：需加入歷史均量"}
    ]
    checklist = [
        f"今天適合做多嗎？{'✅ 可以，但等回踩' if allow_long.startswith('✅') else '❌ 不建議'}",
        f"今天適合做空嗎？{allow_short}",
        f"可以放大部位嗎？{pyramid}",
        f"哪個板塊最強？{sector_rows[0]['板塊'] if sector_rows else '資料不足'}",
        "今天最大的風險：Funding/OI 尚未納入，槓桿過熱需自行確認。"
    ]

    return {
        "market_score_display": show_score(market_score),
        "bull_score_display": show_score(bull_score),
        "bear_score_display": show_score(bear_score),
        "altseason_score_display": show_score(altseason_score),
        "state": state,
        "stars": stars,
        "decision": make_decision(state, market_score, risk),
        "risk": risk,
        "allocation": allocation,
        "allow_long": allow_long,
        "allow_short": allow_short,
        "pyramid": pyramid,
        "macro_rows": macro_rows,
        "crypto_rows": crypto_rows,
        "sector_rows": sector_rows if sector_rows else [{"排名": "-", "板塊": "資料不足", "分數": "資料不足", "24H市值變化%": "資料不足", "24H成交量": "資料不足", "代表幣": ""}],
        "alt_rows": alt_rows,
        "altseason_phase": alt_phase(altseason_score),
        "checklist": checklist,
        "discipline": "不因 FOMO 提高槓桿；不追價；只在流動性掃蕩 + 成交量確認 + 停損明確時進場。"
    }
