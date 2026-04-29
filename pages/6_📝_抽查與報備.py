import streamlit as st
import pandas as pd
import os
import json
from utils import init_sidebar

# 1. 基礎配置
st.set_page_config(page_title="抽查與報備", layout="wide")
curr_proj = init_sidebar()

# --- 💉 視覺修正：緊湊佈局 ---
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
path_public = os.path.join(project_dir, "process_public_review.csv")
path_report = os.path.join(project_dir, "process_report_items.csv")
path_notes = os.path.join(project_dir, "notes_inspection.json") 

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

# --- 頁面標題 ---
st.title("📝 抽查與報備")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 3. 資料處理函數 ---

def load_data(path, default_items):
    # 標準欄位順序：加入審查單位與協力廠商
    cols = ["項目名稱", "是否辦理", "進度狀態", "審查單位", "協力廠商", "備註"]
    
    if os.path.exists(path):
        df = pd.read_csv(path, dtype=str).fillna("")
        # 自動補齊新欄位
        for c in cols:
            if c not in df.columns:
                if c == "是否辦理": df[c] = "⚪ 待確認"
                elif c == "進度狀態": df[c] = "⚪ 未開始"
                else: df[c] = ""
        return df[cols]
    else:
        df = pd.DataFrame({"項目名稱": default_items})
        df["是否辦理"] = "⚪ 待確認"
        df["進度狀態"] = "⚪ 未開始"
        df["審查單位"] = ""
        df["協力廠商"] = ""
        df["備註"] = ""
        return df[cols]

# 載入資料
df_public = load_data(path_public, ["都審抽查", "建照抽查", "結構抽查", "消防抽查"])
df_report = load_data(path_report, ["開工報備", "震後報備", "變更設計報備", "竣工報備"])

# 選單定義
opt_handle = ["⚪ 待確認", "✅ 需辦理", "➖ 不涉及"]
opt_status = ["⚪ 未開始", "⏳ 辦理中", "📝 補正中", "🆗 已結案", "⚠️ 遇到問題"]

column_config = {
    "項目名稱": st.column_config.TextColumn("項目名稱", width="medium"),
    "是否辦理": st.column_config.SelectboxColumn("是否辦理", options=opt_handle, width="small"),
    "進度狀態": st.column_config.SelectboxColumn("進度狀態", options=opt_status, width="small"),
    "審查單位": st.column_config.TextColumn("審查單位", width="small"),
    "協力廠商": st.column_config.TextColumn("協力廠商", width="small"),
    "備註": st.column_config.TextColumn("備註", width="large")
}

# --- 4. 表格渲染 ---

st.subheader("🏛️ 公部門審查 (抽查)")
h_pub = (len(df_public) * 35.5) + 48
with st.form("form_public"):
    e_pub = st.data_editor(df_public, num_rows="dynamic", use_container_width=True, hide_index=True, height=int(h_pub), column_config=column_config)
    if st.form_submit_button("💾 儲存公部門審查變更", use_container_width=True):
        e_pub.to_csv(path_public, index=False, encoding='utf-8-sig'); st.rerun()

st.write("")

st.subheader("📋 報備項目")
h_rep = (len(df_report) * 35.5) + 48
with st.form("form_report"):
    e_rep = st.data_editor(df_report, num_rows="dynamic", use_container_width=True, hide_index=True, height=int(h_rep), column_config=column_config)
    if st.form_submit_button("💾 儲存報備項目變更", use_container_width=True):
        e_rep.to_csv(path_report, index=False, encoding='utf-8-sig'); st.rerun()

# --- 5. 核心：便利貼 ---
st.divider()
st.subheader("📌 抽查與報備重要備忘")

if 'notes_insp' not in st.session_state:
    if os.path.exists(path_notes):
        with open(path_notes, "r", encoding="utf-8") as f:
            st.session_state.notes_insp = json.load(f)
    else:
        st.session_state.notes_insp = [{"title": "新紀錄", "content": ""}]

if st.button("➕ 新增便利貼"):
    st.session_state.notes_insp.append({"title": "新紀錄", "content": ""}); st.rerun()

cols = st.columns(3)
updated_notes = []
for idx, note in enumerate(st.session_state.notes_insp):
    with cols[idx % 3]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1: nt = st.text_input(f"T_{idx}", value=note["title"], key=f"t_{idx}_insp", label_visibility="collapsed")
            with c2: 
                if st.button("🗑️", key=f"d_{idx}_insp"):
                    st.session_state.notes_insp.pop(idx); st.rerun()
            nc = st.text_area(f"C_{idx}", value=note["content"], key=f"c_{idx}_insp", height=120, label_visibility="collapsed")
            updated_notes.append({"title": nt, "content": nc})

if st.button("💾 儲存便利貼內容", use_container_width=True):
    with open(path_notes, "w", encoding="utf-8") as f:
        json.dump(updated_notes, f, ensure_ascii=False, indent=4)
    st.session_state.notes_insp = updated_notes
    st.success("✅ 抽查與報備備忘錄已儲存！")