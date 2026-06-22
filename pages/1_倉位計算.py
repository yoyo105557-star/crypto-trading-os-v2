
import streamlit as st
st.title("💰 倉位計算器")
capital = st.number_input("帳戶本金 USDT", min_value=0.0, value=1000.0, step=100.0)
risk_pct = st.number_input("單筆風險 %", min_value=0.1, value=2.0, step=0.1)
entry = st.number_input("進場價格", min_value=0.0, value=100.0, step=1.0)
stop = st.number_input("停損價格", min_value=0.0, value=96.0, step=1.0)
leverage = st.number_input("槓桿倍數", min_value=1.0, value=3.0, step=1.0)
risk_amount = capital * risk_pct / 100
stop_distance = abs(entry - stop) / entry if entry else 0
position = risk_amount / stop_distance if stop_distance else 0
qty = position / entry if entry else 0
margin = position / leverage if leverage else position
c1, c2, c3, c4 = st.columns(4)
c1.metric("最大虧損", f"{risk_amount:.2f} USDT")
c2.metric("停損距離", f"{stop_distance*100:.2f}%")
c3.metric("建議倉位", f"{position:.2f} USDT")
c4.metric("可買數量", f"{qty:.6f}")
st.info(f"使用 {leverage:.0f}x 槓桿時，約需保證金：{margin:.2f} USDT")
