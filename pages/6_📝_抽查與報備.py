import streamlit as st
import pandas as pd
import os
import json
from utils import init_sidebar

# 1. 基礎配置
st.set_page_config(page_title="各階段審查：抽查與報備", layout="wide")
curr_proj = init_sidebar()

# --- 💉 視覺修正 ---
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem !important; }
        hr { margin-top: 0.8rem !important; margin-bottom: 1.5rem !important; }
        [data-testid="stForm"] { padding: 0.5rem 0rem !important; border: none !important; }
        [data-testid="stTable"] { overflow: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 2. 路徑設定
project_dir = f"projects/{curr_proj}"
path_gov = os.path.join(project_dir, "process_checklist_gov.csv")
path_report = os.path.join(project_dir, "process_checklist_report.csv")
path_notes = os.path.join(project_dir, "notes_report.json")

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

# --- 頁面標題 ---
st.title("📝 各階段審查：抽查與報備")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 3. 資料處理邏輯 ---

def load_data(path, default_items):
    if os.path.exists(path):
        return pd.read_csv(path, dtype=str).fillna("")
    else:
        return pd.DataFrame({
            "評估項目": default_items, 
            "是否辦理": "⚪ 待確認", "進度狀態": "⚪ 未開始", "備註": ""
        })

def load_notes():
    if not os.path.exists(path_notes):
        return [{"title": "新紀錄", "content": ""}]
    with open(path_notes, "r", encoding="utf-8") as f:
        return json.load(f)

# 載入資料
df_gov = load_data(path_gov, ["建築師公會抽查", "綠建築公會抽查", "行政抽檢"])
df_report = load_data(path_report, ["自行報備審查", "抽查報備審查", "行政抽檢報備"])

if 'temp_notes_rep' not in st.session_state or st.session_state.get('notes_rep_last_proj') != curr_proj:
    st.session_state.temp_notes_rep = load_notes()
    st.session_state.notes_rep_last_proj = curr_proj

# --- 4. 表格配置參數 ---
opt_handle = ["⚪ 待確認", "✅ 需辦理", "➖ 不涉及"]
opt_status = ["⚪ 未開始", "⏳ 辦理中", "📝 補正中", "🆗 已結案", "⚠️ 遇到問題"]
config = {
    "評估項目": st.column_config.TextColumn("評估項目", width="medium"),
    "是否辦理": st.column_config.SelectboxColumn("是否辦理", options=opt_handle, width="small"),
    "進度狀態": st.column_config.SelectboxColumn("進度狀態", options=opt_status, width="small"),
    "備註": st.column_config.TextColumn("備註", width="large")
}

# --- 5. 第一部分：公部門審查 ---
st.subheader("🏛️ 公部門審查")
h_gov = (len(df_gov) * 35.5) + 48 

with st.form("form_gov"):
    e_gov = st.data_editor(df_gov, use_container_width=True, hide_index=True, num_rows="dynamic", height=int(h_gov), column_config=config)
    if st.form_submit_button("💾 儲存公部門審查變更", use_container_width=True):
        e_gov.to_csv(path_gov, index=False, encoding='utf-8-sig')
        st.success("✨ 公部門審查已儲存！")
        st.rerun()

st.write("") # 間距

# --- 6. 第二部分：報備項目 ---
st.subheader("📄 報備項目")
h_report = (len(df_report) * 35.5) + 48 

with st.form("form_report"):
    e_report = st.data_editor(df_report, use_container_width=True, hide_index=True, num_rows="dynamic", height=int(h_report), column_config=config)
    if st.form_submit_button("💾 儲存報備項目變更", use_container_width=True):
        e_report.to_csv(path_report, index=False, encoding='utf-8-sig')
        st.success("✨ 報備項目已儲存！")
        st.rerun()

# --- 7. 第三部分：專屬便利貼 ---
st.divider()
st.subheader("📌 抽查報備重要備忘")

if st.button("➕ 新增便利貼"):
    st.session_state.temp_notes_rep.append({"title": "新紀錄", "content": ""})
    st.rerun()

cols = st.columns(3)
updated_notes = []
for idx, note in enumerate(st.session_state.temp_notes_rep):
    with cols[idx % 3]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1: new_title = st.text_input(f"T_{idx}", value=note["title"], key=f"t_{idx}_rep", label_visibility="collapsed")
            with c2: 
                if st.button("🗑️", key=f"d_{idx}_rep"):
                    st.session_state.temp_notes_rep.pop(idx)
                    st.rerun()
            new_content = st.text_area(f"C_{idx}", value=note["content"], key=f"c_{idx}_rep", height=120, label_visibility="collapsed")
            updated_notes.append({"title": new_title, "content": new_content})

if st.button("💾 儲存便利貼內容", use_container_width=True):
    with open(path_notes, "w", encoding="utf-8") as f:
        json.dump(updated_notes, f, ensure_ascii=False, indent=4)
    st.session_state.temp_notes_rep = updated_notes
    st.success("✅ 便利貼已更新！")
    st.rerun()