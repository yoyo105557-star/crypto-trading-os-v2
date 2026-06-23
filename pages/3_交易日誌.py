
import streamlit as st
import pandas as pd
st.title("📝 交易日誌")
if "journal" not in st.session_state:
    st.session_state.journal = pd.DataFrame(columns=["日期","幣種","方向","進場","停損","停利","R值","是否照系統","心得"])
edited = st.data_editor(st.session_state.journal, num_rows="dynamic", use_container_width=True)
st.session_state.journal = edited
r = pd.to_numeric(edited.get("R值", pd.Series([])), errors="coerce").dropna()
if len(r):
    st.metric("勝率", f"{(r>0).sum()/len(r)*100:.1f}%")
    st.metric("平均R", f"{r.mean():.2f}")
    st.metric("累積R", f"{r.sum():.2f}")
