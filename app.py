import streamlit as st
from utils import init_sidebar

# 必須放在第一行
st.set_page_config(page_title="專案管理中心", layout="wide")

# 這裡就是呼叫 utils.py 裡我們寫好的選單
curr_proj = init_sidebar()

# 主畫面內容
st.title("🏢 專案管理中心")
st.write(f"目前正在執行的專案：**{curr_proj}**")
st.divider()
st.info("💡 請點選左側選單的功能開始操作。")