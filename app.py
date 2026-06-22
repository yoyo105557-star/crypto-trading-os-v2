import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Crypto Trading OS",page_icon="📈",layout="wide")
st.title("📈 Crypto Trading OS")

def price(sym):
    try:
        d=requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}",timeout=8).json()
        return float(d["lastPrice"]),float(d["priceChangePercent"])
    except:
        return None,None

coins=[]
for s in ["BTCUSDT","ETHUSDT","SOLUSDT"]:
    p,ch=price(s)
    coins.append({"Coin":s.replace("USDT",""),"Price":p,"24h%":ch})

bull=80
bear=30
alt=70
market=round(bull*0.55+(100-bear)*0.2+alt*0.25)

c1,c2,c3,c4=st.columns(4)
c1.metric("Market",market)
c2.metric("Bull",bull)
c3.metric("Bear",bear)
c4.metric("Alt",alt)

st.success("Risk ON｜建議風險 2%｜等待回踩，不追價")

st.subheader("Live Price")
st.dataframe(pd.DataFrame(coins),use_container_width=True,hide_index=True)

st.subheader("Position Calculator")
cap=st.number_input("Capital",1000.0)
risk=st.number_input("Risk %",2.0)
stop=st.number_input("Stop %",4.0)
loss=cap*risk/100
pos=loss/(stop/100) if stop else 0
a,b=st.columns(2)
a.metric("Max Loss",round(loss,2))
b.metric("Position Size",round(pos,2))

st.subheader("Watchlist")
st.table(pd.DataFrame([
{"Coin":"RENDER","Sector":"AI"},
{"Coin":"FET","Sector":"AI"},
{"Coin":"ONDO","Sector":"RWA"}]))
