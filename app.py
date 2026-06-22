
import streamlit as st
import pandas as pd
from services.market_data import (
    fetch_binance_24h,
    fetch_eth_btc,
    fetch_fear_greed,
    fetch_global_crypto,
    fetch_coin_markets,
    fetch_stablecoins,
    fetch_macro_stooq,
    fetch_categories
)
from engines.scores import build_dashboard

st.set_page_config(page_title="Crypto Trading OS", page_icon="📊", layout="wide")

st.title("📊 Crypto Trading OS 最終版")
st.caption("所有分數皆由公開 API 即時資料計算；抓不到資料時會顯示「資料不足」，不使用假數據。")

with st.spinner("更新市場資料中..."):
    prices = fetch_binance_24h(["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    eth_btc = fetch_eth_btc()
    fear = fetch_fear_greed()
    global_data = fetch_global_crypto()
    coin_markets = fetch_coin_markets(["bitcoin", "ethereum"])
    stable = fetch_stablecoins()
    macro = fetch_macro_stooq()
    categories = fetch_categories()

dashboard = build_dashboard(
    prices=prices,
    eth_btc=eth_btc,
    fear=fear,
    global_data=global_data,
    coin_markets=coin_markets,
    stable=stable,
    macro=macro,
    categories=categories
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("市場總分", dashboard["market_score_display"])
c2.metric("牛市分數", dashboard["bull_score_display"])
c3.metric("熊市分數", dashboard["bear_score_display"])
c4.metric("山寨季分數", dashboard["altseason_score_display"])

st.divider()

st.subheader("🤖 今日決策")
state = dashboard["state"]
if state == "Risk ON":
    st.success(dashboard["decision"])
elif state == "Risk OFF":
    st.error(dashboard["decision"])
else:
    st.warning(dashboard["decision"])

st.markdown(f"""
### ⭐ 市場星級
**{dashboard["stars"]}**

### 💰 今日資金配置
- 現貨 / 合約：**{dashboard["allocation"]}**
- 建議單筆風險：**{dashboard["risk"]}**
- 是否允許做多：**{dashboard["allow_long"]}**
- 是否允許做空：**{dashboard["allow_short"]}**
- 盈利加倉：**{dashboard["pyramid"]}**
- 追價 / 逆勢摸頂：**禁止**
""")

st.divider()

st.subheader("🌍 宏觀環境")
st.dataframe(pd.DataFrame(dashboard["macro_rows"]), use_container_width=True, hide_index=True)

st.subheader("₿ 加密市場")
st.dataframe(pd.DataFrame(dashboard["crypto_rows"]), use_container_width=True, hide_index=True)

st.subheader("🔥 板塊排行榜")
st.dataframe(pd.DataFrame(dashboard["sector_rows"]), use_container_width=True, hide_index=True)

st.subheader("🚀 山寨季儀表")
st.dataframe(pd.DataFrame(dashboard["alt_rows"]), use_container_width=True, hide_index=True)
st.info(dashboard["altseason_phase"])

st.subheader("✅ 今日交易 Checklist")
for item in dashboard["checklist"]:
    st.write(f"- {item}")

st.subheader("🧠 紀律提醒")
st.warning(dashboard["discipline"])

st.divider()
st.caption("資料源：Binance、CoinGecko、Alternative.me、DefiLlama、Stooq。非投資建議。")
