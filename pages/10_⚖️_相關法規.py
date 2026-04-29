import streamlit as st
from utils import init_sidebar

st.set_page_config(layout="wide")
curr_proj = init_sidebar() # 呼叫更新後的導航

st.title("⚖️ 相關法規") # 請根據上表修改標題
st.write(f"當前專案：{curr_proj}")
# ... 後續功能程式碼 ...