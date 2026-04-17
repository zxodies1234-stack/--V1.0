import streamlit as st
from utils import init_sidebar

st.set_page_config(layout="wide")
curr_proj = init_sidebar()
st.title("📝 執照前 (測試頁面)") # 這裡依檔案改為執照中、執照後
st.write(f"當前專案：{curr_proj}")