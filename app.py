import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Crypto Trading OS 中文版",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Crypto Trading OS 中文版")
st.caption("市場評分｜山寨季判斷｜倉位計算｜交易紀律")

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        data = requests.get(url, timeout=8).json()
        return {
            "幣種": symbol.replace("USDT", ""),
            "價格": round(float(data["lastPrice"]), 4),
            "24H漲跌%": round(float(data["priceChangePercent"]), 2),
            "成交量": round(float(data["volume"]), 2)
        }
    except Exception:
        return {
            "幣種": symbol.replace("USDT", ""),
            "價格": None,
            "24H漲跌%": None,
            "成交量": None
        }

def get_fear_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        data = requests.get(url, timeout=8).json()["data"][0]
        return int(data["value"]), data["value_classification"]
    except Exception:
        return 50, "Neutral"

prices = pd.DataFrame([
    get_price("BTCUSDT"),
    get_price("ETHUSDT"),
    get_price("SOLUSDT")
])

fear_value, fear_label = get_fear_greed()

btc_change = prices.loc[prices["幣種"] == "BTC", "24H漲跌%"].iloc[0] or 0
eth_change = prices.loc[prices["幣種"] == "ETH", "24H漲跌%"].iloc[0] or 0
sol_change = prices.loc[prices["幣種"] == "SOL", "24H漲跌%"].iloc[0] or 0

牛市分數 = 50
熊市分數 = 50
山寨季分數 = 40

if btc_change > 1:
    牛市分數 += 15
    熊市分數 -= 10
elif btc_change < -1:
    牛市分數 -= 10
    熊市分數 += 15

if eth_change > btc_change:
    牛市分數 += 10
    山寨季分數 += 15

if sol_change > btc_change:
    山寨季分數 += 15

if 45 <= fear_value <= 75:
    牛市分數 += 10
elif fear_value > 80:
    熊市分數 += 10
elif fear_value < 30:
    熊市分數 += 10

牛市分數 = max(0, min(100, round(牛市分數)))
熊市分數 = max(0, min(100, round(熊市分數)))
山寨季分數 = max(0, min(100, round(山寨季分數)))
市場總分 = round((牛市分數 * 0.55) + ((100 - 熊市分數) * 0.2) + (山寨季分數 * 0.25))

col1, col2, col3, col4 = st.columns(4)
col1.metric("市場總分", f"{市場總分}/100")
col2.metric("牛市分數", 牛市分數)
col3.metric("熊市分數", 熊市分數)
col4.metric("山寨季分數", 山寨季分數)

st.divider()

st.subheader("🧠 今日交易決策")

if 市場總分 >= 75 and 牛市分數 > 熊市分數:
    st.success("🟢 Risk ON｜偏多操作｜建議風險：2%｜允許加倉：限制加倉｜等待回踩，不追價。")
elif 市場總分 <= 40 or 熊市分數 > 牛市分數 + 20:
    st.error("🔴 Risk OFF｜觀望或反彈做空｜建議風險：0~1%｜不做多山寨，不硬扛。")
else:
    st.warning("🟡 中性震盪｜建議風險：1%｜只做 A+ 訊號，沒有流動性掃蕩不進場。")

st.divider()

st.subheader("📈 即時價格")
st.dataframe(prices, use_container_width=True, hide_index=True)

st.subheader("😱 恐懼貪婪指數")
st.metric("目前指數", fear_value, fear_label)

st.divider()

st.subheader("🔥 今日候選板塊 / 幣種")
watchlist = pd.DataFrame([
    {"幣種": "RENDER", "板塊": "AI", "觀察理由": "AI板塊候選"},
    {"幣種": "FET", "板塊": "AI", "觀察理由": "AI板塊候選"},
    {"幣種": "ONDO", "板塊": "RWA", "觀察理由": "RWA板塊候選"},
    {"幣種": "SOL", "板塊": "Layer1", "觀察理由": "主流山寨代表"}
])
st.dataframe(watchlist, use_container_width=True, hide_index=True)

st.divider()

st.subheader("💰 倉位計算器")

本金 = st.number_input("帳戶本金 USDT", min_value=0.0, value=1000.0, step=100.0)
單筆風險 = st.number_input("單筆風險 %", min_value=0.1, value=2.0, step=0.1)
停損距離 = st.number_input("停損距離 %", min_value=0.1, value=4.0, step=0.1)

最大虧損 = 本金 * 單筆風險 / 100
建議倉位 = 最大虧損 / (停損距離 / 100)

c1, c2 = st.columns(2)
c1.metric("最大可虧損", f"{round(最大虧損, 2)} USDT")
c2.metric("建議倉位", f"{round(建議倉位, 2)} USDT")

st.divider()

st.subheader("✅ 交易前檢查")
st.checkbox("已確認大方向")
st.checkbox("已出現流動性掃蕩")
st.checkbox("成交量有配合")
st.checkbox("停損位置明確")
st.checkbox("沒有 FOMO 追價")

st.info("紀律提醒：看對行情不代表可以亂下單。沒有流動性掃蕩、沒有成交量確認，就不要進場。")
