import streamlit as st
from utils import init_sidebar

curr_proj = init_sidebar()

st.title(f"📊 專案進度：{curr_proj}")
# 接下來寫你的進度條/甘特圖內容...