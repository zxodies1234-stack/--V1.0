import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta

# --- 1. 全域配置 ---
st.set_page_config(layout="wide", page_title="建築開發管理系統", page_icon="🏗️")

# 使用 CSS 隱藏預設的導航標題，並調整間距
st.markdown("""
    <style>
        /* 隱藏預設的 "Navigation" 文字 */
        [data-testid="stSidebarNav"]::before {
            content: "🚀 主要功能模組";
            margin-left: 20px;
            margin-top: 20px;
            font-size: 1.2rem;
            font-weight: bold;
        }
        /* 隱藏 app.py 本身的連結 */
        [data-testid="stSidebarNav"] ul li:nth-child(1) {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. 專案管理中心 (釘選在側邊欄最上方) ---
st.sidebar.markdown("### 🏢 專案管理中心")

SAVE_DIR = "projects"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# A. 新增專案功能
with st.sidebar.expander("➕ 新增專案", expanded=False):
    new_name = st.text_input("專案名稱", key="new_proj_input")
    if st.button("確認建立"):
        if new_name:
            proj_path = os.path.join(SAVE_DIR, new_name)
            if not os.path.exists(proj_path):
                os.makedirs(proj_path)
                # 初始化檔案
                pd.DataFrame([{"階段": "設計初期", "預計開始": date.today(), "預計結束": date.today() + timedelta(days=30)}]).to_csv(os.path.join(proj_path, "progress.csv"), index=False)
                pd.DataFrame([{"項目": "基地面積", "內容/數值": "0"}]).to_csv(os.path.join(proj_path, "area.csv"), index=False)
                st.rerun()

# B. 選擇專案
all_projs = [d for d in os.listdir(SAVE_DIR) if os.path.isdir(os.path.join(SAVE_DIR, d))]
if all_projs:
    if 'current_project' not in st.session_state or st.session_state['current_project'] not in all_projs:
        st.session_state['current_project'] = all_projs[0]
    
    selected_proj = st.sidebar.selectbox("選擇目前執行專案", all_projs, index=all_projs.index(st.session_state['current_project']))
    st.session_state['current_project'] = selected_proj
else:
    st.sidebar.warning("請先新增專案")
    st.stop()

st.sidebar.divider()
# 注意：這裡不需要手動寫「主要功能模組」標題，因為我們已透過 CSS 注入