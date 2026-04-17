import streamlit as st
import pandas as pd
import os
from utils import init_sidebar

# 0. 基礎配置與路徑鎖定
st.set_page_config(layout="wide")
curr_proj = init_sidebar()

# 絕對路徑定位
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
project_dir = os.path.join(root_dir, "projects", curr_proj)

# 定義三個 CSV 的實體路徑
path_checklist = os.path.join(project_dir, "review_checklist.csv")
path_review = os.path.join(project_dir, "review_items_process.csv")
path_cert = os.path.join(project_dir, "review_items_final.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

st.title(f"📝 審查項目管理")
st.caption(f"當前專案：{curr_proj}")

# 通用進度選項
status_options = [
    "⚪ 未開始", "📂 彙整中", "📨 掛號中", "📝 補正中", 
    "✅ 已完成", "🔥 緊急趕工", "⚠️ 遇到問題", "➖ 未涉及"
]

# --- 1. 資料載入函數群 ---

def load_all_data():
    # A. 載入評估階段 Check List
    check_items = [
        "捷運禁限範圍", "松山機場禁限管制", "海砂審查鑑定", "都審", "都更", 
        "容移", "危老", "歷史建築", "環境風場試驗", 
        "都市計畫指定留設：騎樓/騎樓地/無遮簷人行道"
    ]
    if os.path.exists(path_checklist):
        df_c = pd.read_csv(path_checklist, dtype=str).fillna("")
    else:
        df_c = pd.DataFrame({"評估項目": check_items, "確認狀態": "➖ 不涉及", "關鍵說明/結果": ""})

    # B. 載入表格 1 (審查與候選)
    cols = ["審查項目", "列管時間", "審查單位", "進度", "協力單位", "備註"]
    if os.path.exists(path_review):
        df_1 = pd.read_csv(path_review, encoding='utf-8-sig', dtype=str).fillna("")
    else:
        data_1 = [
            {"審查項目": "耐震設計審查", "列管時間": "放樣勘驗前", "審查單位": "建築中心"},
            {"審查項目": "無障礙性能評估", "列管時間": "1F樓板-勘驗前", "審查單位": "建築中心"},
            {"審查項目": "結構安全性能審查", "列管時間": "放樣勘驗前", "審查單位": "建築中心"},
            {"審查項目": "綠建築候選", "列管時間": "1F樓板-勘驗前", "審查單位": "建築中心"},
            {"審查項目": "智慧建築候選", "列管時間": "1F樓板-勘驗前", "審查單位": "建築中心"},
            {"審查項目": "1+級能效候選", "列管時間": "1F樓板-勘驗前", "審查單位": "建築中心"},
            {"審查項目": "綠建築自治條例專章", "列管時間": "", "審查單位": "建築中心"}
        ]
        df_1 = pd.DataFrame(data_1, columns=cols).fillna("")
        df_1["進度"] = "⚪ 未開始"

    # C. 載入表格 2 (取得標章)
    if os.path.exists(path_cert):
        df_2 = pd.read_csv(path_cert, encoding='utf-8-sig', dtype=str).fillna("")
    else:
        data_2 = [
            {"審查項目": "耐震設計標章", "列管時間": "使照前", "審查單位": "建築中心"},
            {"審查項目": "無障礙性能標章", "列管時間": "使照後 / 3個月內", "審查單位": "建築中心"},
            {"審查項目": "結構安全性能標章", "列管時間": "使照後 / 3個月內", "審查單位": "建築中心"},
            {"審查項目": "綠建築標章", "列管時間": "使照後 / 2年內", "審查單位": "建築中心"},
            {"審查項目": "智慧建築", "列管時間": "使照後 / 2年內", "審查單位": "建築中心"},
            {"審查項目": "1+級能效標章", "列管時間": "使照後 / 2年內", "審查單位": "建築中心"}
        ]
        df_2 = pd.DataFrame(data_2, columns=cols).fillna("")
        df_2["進度"] = "⚪ 未開始"

    # 統一補齊欄位，確保 data_editor 不會報錯
    for d in [df_1, df_2]:
        for c in cols:
            if c not in d.columns: d[c] = ""
    
    return df_c, df_1, df_2

# 執行載入
df_check, df_r1, df_r2 = load_all_data()

# --- 2. 頁面渲染：三大塊 ---

# 【區塊一：評估階段 Check List】
st.subheader("🔍 評估階段 Check List")
with st.form("form_checklist"):
    c_status = ["⚪ 待確認", "✅ 需辦理", "➖ 不涉及", "🆗 已結案"]
    e_check = st.data_editor(
        df_check, use_container_width=True, hide_index=True, key="ed_c",
        column_config={
            "評估項目": st.column_config.TextColumn(disabled=True, width="medium"),
            "確認狀態": st.column_config.SelectboxColumn(options=c_status, width="small"),
            "關鍵說明/結果": st.column_config.TextColumn(width="large")
        }
    )
    if st.form_submit_button("💾 儲存評估階段變更", use_container_width=True):
        e_check.to_csv(path_checklist, index=False, encoding='utf-8-sig')
        st.success("✅ 評估階段已儲存")
        st.rerun()

st.divider()

# 【區塊二：表格 1：獎勵項目-審查與候選】
st.subheader("🏆 表格 1：獎勵項目-審查與候選")
with st.form("form_t1"):
    e_t1 = st.data_editor(
        df_r1, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_t1",
        column_config={
            "審查項目": st.column_config.TextColumn(width="medium"),
            "列管時間": st.column_config.TextColumn(width="medium"),
            "進度": st.column_config.SelectboxColumn(options=status_options, width="medium"),
            "備註": st.column_config.TextColumn(width="medium")
        }
    )
    if st.form_submit_button("💾 儲存表格 1 變更", use_container_width=True):
        e_t1.to_csv(path_review, index=False, encoding='utf-8-sig')
        st.success("✅ 表格 1 已儲存")
        st.rerun()

st.divider()

# 【區塊三：表格 2：獎勵項目-取得標章】
st.subheader("🏅 表格 2：獎勵項目-取得標章")
with st.form("form_t2"):
    e_t2 = st.data_editor(
        df_r2, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_t2",
        column_config={
            "審查項目": st.column_config.TextColumn(width="medium"),
            "列管時間": st.column_config.TextColumn(width="medium"),
            "進度": st.column_config.SelectboxColumn(options=status_options, width="medium"),
            "備註": st.column_config.TextColumn(width="medium")
        }
    )
    if st.form_submit_button("💾 儲存表格 2 變更", use_container_width=True):
        e_t2.to_csv(path_cert, index=False, encoding='utf-8-sig')
        st.success("✅ 表格 2 已儲存")
        st.rerun()