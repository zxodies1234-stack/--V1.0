import streamlit as st
import pandas as pd
import os
from datetime import date
from utils import init_sidebar

# 基礎配置
st.set_page_config(page_title="各階段審查：執照前", layout="wide")
curr_proj = init_sidebar()

# 路徑定位
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
project_dir = os.path.join(root_dir, "projects", curr_proj)
path_checklist = os.path.join(project_dir, "review_checklist.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

# --- 🎩 驚喜一：頂部視覺看板 ---
st.title("📝 各階段審查：執照前")
col_info1, col_info2 = st.columns([2, 1])

with col_info1:
    # 里程碑進度
    st.subheader("🚀 掛號衝刺進度")
    # 這裡可以根據 Check List 的結案數量自動計算，我們先給一個示範值
    progress_val = 65 
    st.progress(progress_val / 100)
    st.caption(f"目前執照準備進度：{progress_val}%，距離目標掛照還差最後幾哩路！")

with col_info2:
    # 倒數計時功能
    st.subheader("⏰ 目標掛照日")
    target_date = st.date_input("設定預計掛號日期", date(2026, 6, 30))
    days_left = (target_date - date.today()).days
    if days_left > 0:
        st.metric("倒數天數", f"{days_left} Days", delta="-1 Day", delta_color="inverse")
    else:
        st.error("⚠️ 已超過預計掛號日！")

st.divider()

# --- 📂 驚喜二：執照圖說雲端櫃 (模擬上傳) ---
with st.expander("📂 執照圖說預檢清單 (點開查看上傳狀態)", expanded=False):
    st.info("💡 這裡可以讓你預覽目前手邊已彙整的圖說檔案，確保掛號當天不缺件。")
    files = ["1. 建築執照申請書", "2. 委託書/地主同意書", "3. 面積計算表", "4. 配置圖/各層平面圖", "5. 立面/剖面圖"]
    for f in files:
        col_f1, col_f2 = st.columns([3, 1])
        col_f1.write(f)
        col_f2.checkbox("已備齊", key=f"file_{f}")
    
    st.file_uploader("📥 上傳圖說草案 (PDF/DWG)", accept_multiple_files=True)

st.divider()

# --- 🔍 原有的：評估階段 Check List (搬家過來的內容) ---
check_items = [
    "捷運禁限範圍", "松山機場禁限管制", "海砂審查鑑定", "都審", "都更", 
    "容移", "危老", "歷史建築", "環境風場試驗", 
    "都市計畫指定留設：騎樓/騎樓地/無遮簷人行道"
]

if os.path.exists(path_checklist):
    df_check = pd.read_csv(path_checklist, dtype=str).fillna("")
else:
    df_check = pd.DataFrame({"評估項目": check_items, "確認狀態": "➖ 不涉及", "關鍵說明/結果": ""})

st.subheader("🔍 評估階段 Check List")
with st.form("form_checklist_before"):
    c_status = ["⚪ 待確認", "✅ 需辦理", "➖ 不涉及", "🆗 已結案"]
    e_check = st.data_editor(
        df_check, use_container_width=True, hide_index=True, key="ed_c_before_v2",
        column_config={
            "評估項目": st.column_config.TextColumn(disabled=True, width="medium"),
            "確認狀態": st.column_config.SelectboxColumn(options=c_status, width="small"),
            "關鍵說明/結果": st.column_config.TextColumn(width="large")
        }
    )
    if st.form_submit_button("💾 儲存所有資料", use_container_width=True):
        e_check.to_csv(path_checklist, index=False, encoding='utf-8-sig')
        st.success("✨ 執照前進度與 Check List 已更新！")
        st.balloons() # 儲存成功噴個彩帶慶祝一下
        st.rerun()