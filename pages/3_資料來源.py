
import streamlit as st
st.title("🔎 資料來源")
st.markdown("""
目前已接入：
- Binance Spot API：BTC/ETH/SOL 即時價格、24H 漲跌、成交量
- Binance ETHBTC：ETH/BTC 強弱
- CoinGecko Global：BTC Dominance、總市值、24H市值變化
- CoinGecko Categories：AI、RWA、DeFi、MEME、Gaming、Layer1 板塊資料
- Alternative.me：Fear & Greed
- DefiLlama Stablecoins：穩定幣總市值
- Stooq：DXY、Nasdaq

尚未納入正式分數：
- Funding Rate / Open Interest
- ETF Flow
- BTC橫盤、成交量擴大、TOTAL3突破
""")
