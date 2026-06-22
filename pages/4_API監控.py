import streamlit as st
import pandas as pd
from services.status import check_all

st.title("⚙️ API 監控")
st.caption("檢查目前 Crypto Trading OS 使用的公開資料來源是否正常。")

if st.button("重新檢查 API"):
    st.cache_data.clear()

@st.cache_data(ttl=300)
def cached_check():
    return check_all()

rows = cached_check()
df = pd.DataFrame(rows)

st.dataframe(df, use_container_width=True, hide_index=True)

ok_count = sum(1 for r in rows if str(r["狀態"]).startswith("✅"))
total = len(rows)

st.metric("正常 API", f"{ok_count}/{total}")

if ok_count == total:
    st.success("所有 API 目前正常。")
elif ok_count >= total * 0.6:
    st.warning("部分 API 異常，Dashboard 可能出現資料不足。")
else:
    st.error("多數 API 異常，今日不建議依賴系統分數交易。")

st.info("如果 API 異常，系統應顯示「資料不足」，而不是使用假數據。")
