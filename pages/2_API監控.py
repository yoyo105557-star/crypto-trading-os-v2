
import streamlit as st
import pandas as pd
from services.market import fetch_all
st.title("⚙️ API 監控")
data = fetch_all()
rows = []
rows.append({"API": "Binance Spot", "狀態": "✅" if any(data["prices"]) else "❌"})
rows.append({"API": "Binance Futures", "狀態": "✅" if any(x.get("open_interest") for x in data["futures"]) else "❌"})
rows.append({"API": "CoinGecko Global", "狀態": "✅" if data["global"].get("btc_d") else "❌"})
rows.append({"API": "CoinGecko Categories", "狀態": "✅" if data["categories"] else "❌"})
rows.append({"API": "Alternative Fear & Greed", "狀態": "✅" if data["fear"].get("value") is not None else "❌"})
rows.append({"API": "DefiLlama Stablecoins", "狀態": "✅" if data["stablecoins"].get("total") else "❌"})
rows.append({"API": "Stooq Macro", "狀態": "✅" if any(v is not None for v in data["macro"].values()) else "❌"})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
