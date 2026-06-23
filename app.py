
import streamlit as st
import pandas as pd
from services.market import fetch_all
from core.scoring import score_dashboard, decision, compact

st.set_page_config(page_title="Crypto Trading OS Pro", page_icon="📊", layout="wide")

st.title("📊 Crypto Trading OS Pro")
st.caption("真實 API｜市場評分｜板塊輪動｜山寨季｜Funding / OI｜Stablecoin｜交易決策")

@st.cache_data(ttl=300)
def load_data():
    return fetch_all()

data = load_data()
scores = score_dashboard(data)
state, decision_text, risk, stars = decision(scores)

c1, c2, c3, c4 = st.columns(4)
c1.metric("市場總分", "資料不足" if scores["market"] is None else f"{scores['market']}/100")
c2.metric("牛市分數", "資料不足" if scores["bull"] is None else scores["bull"])
c3.metric("熊市分數", "資料不足" if scores["bear"] is None else scores["bear"])
c4.metric("山寨季分數", "資料不足" if scores["alt"] is None else scores["alt"])

st.subheader("🤖 今日決策")
if state == "Risk ON":
    st.success(decision_text)
elif state == "Risk OFF":
    st.error(decision_text)
else:
    st.warning(decision_text)

st.write(f"**市場星級：{stars}**")
st.write(f"**建議單筆風險：{risk}**")
st.write("**紀律：不追價、不因 FOMO 提高槓桿，只在流動性掃蕩與成交量確認後進場。**")

st.divider()

st.subheader("₿ 加密市場")
rows = []
for x in data["prices"]:
    if x:
        rows.append({
            "標的": x["symbol"],
            "價格": x["price"],
            "24H漲跌%": x["change_24h"],
            "24H成交額": compact(x["quote_volume"])
        })
if data.get("ethbtc"):
    rows.append({
        "標的": "ETHBTC",
        "價格": data["ethbtc"].get("price"),
        "24H漲跌%": data["ethbtc"].get("change_24h"),
        "24H成交額": compact(data["ethbtc"].get("quote_volume"))
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.subheader("⚡ 合約市場：Funding / OI")
frows = []
for x in data["futures"]:
    frows.append({
        "標的": x["symbol"],
        "資金費率%": "資料不足" if x["funding_pct"] is None else round(x["funding_pct"], 5),
        "未平倉量": "資料不足" if x["open_interest"] is None else round(x["open_interest"], 2)
    })
st.dataframe(pd.DataFrame(frows), use_container_width=True, hide_index=True)

st.subheader("🌍 宏觀與全市場")
g = data["global"]
macro = data["macro"]
fear = data["fear"]
stable = data["stablecoins"]
macro_rows = [
    {"指標": "DXY", "數值": macro.get("DXY", "資料不足")},
    {"指標": "Nasdaq", "數值": macro.get("Nasdaq", "資料不足")},
    {"指標": "Fear & Greed", "數值": f"{fear.get('value')}｜{fear.get('label')}"},
    {"指標": "BTC Dominance", "數值": "資料不足" if g.get("btc_d") is None else f"{g['btc_d']:.2f}%"},
    {"指標": "全市場市值24H", "數值": "資料不足" if g.get("market_change_24h") is None else f"{g['market_change_24h']:.2f}%"},
    {"指標": "Stablecoin總市值", "數值": compact(stable.get("total"))},
]
st.dataframe(pd.DataFrame(macro_rows), use_container_width=True, hide_index=True)

st.subheader("🔥 板塊輪動")
if scores["sector_rows"]:
    st.dataframe(pd.DataFrame(scores["sector_rows"]), use_container_width=True, hide_index=True)
else:
    st.warning("板塊資料不足。")

st.subheader("🚀 山寨季儀表")
alt = scores["alt"]
if alt is None:
    st.info("山寨季：資料不足")
elif alt >= 80:
    st.success("全面山寨季 / 擴散期")
elif alt >= 65:
    st.success("山寨季初期擴散")
elif alt >= 50:
    st.warning("山寨季準備階段")
else:
    st.error("山寨季尚未開始")

st.subheader("✅ 今日 Checklist")
best_sector = scores["sector_rows"][0]["板塊"] if scores["sector_rows"] else "資料不足"
st.write(f"- 今天適合做多嗎？{'✅ 可以，但等回踩' if scores['market'] and scores['market'] >= 60 else '❌ 不建議'}")
st.write(f"- 今天適合做空嗎？{'✅ 可觀察反彈空' if scores['bear'] and scores['bear'] > scores.get('bull',0) else '⚠️ 只做破結構'}")
st.write(f"- 可以放大部位嗎？{'✅ 限制加倉' if scores['market'] and scores['market'] >= 80 else '❌ 不建議'}")
st.write(f"- 哪個板塊最強？{best_sector}")
st.write("- 今天最大風險：Funding/OI、宏觀波動、追價風險。")
