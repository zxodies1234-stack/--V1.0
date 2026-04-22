import streamlit as st
import pandas as pd
import os
import json
from utils import init_sidebar

# 1. 基礎配置
st.set_page_config(page_title="各階段審查：執照中", layout="wide")
curr_proj = init_sidebar()

# --- 💉 視覺修正：強制隱藏滾動軸感與緊湊佈局 ---
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem !important; }
        .main .block-container h1 { padding-bottom: 0rem !important; margin-bottom: -0.5rem !important; }
        hr { margin-top: 0.8rem !important; margin-bottom: 1.5rem !important; }
        
        /* 移除表格周圍多餘的 padding，讓寬度最大化 */
        [data-testid="stForm"] { padding: 0.5rem 0rem !important; border: none !important; }
        
        /* 讓文字編輯器內的滾動軸盡量隱藏 (如果計算精確就不會出現) */
        [data-testid="stTable"] { overflow: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 2. 路徑設定
project_dir = f"projects/{curr_proj}"
path_checklist = os.path.join(project_dir, "process_checklist_mid.csv")
path_notes = os.path.join(project_dir, "notes_mid.json")

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

# --- 頁面標題 ---
st.title("📝 各階段審查：執照中")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 3. 資料處理邏輯 ---

def load_checklist():
    if os.path.exists(path_checklist):
        df = pd.read_csv(path_checklist, dtype=str).fillna("")
        return df
    else:
        return pd.DataFrame({
            "評估項目": [
                "台電預審", "鑽探報告", "現況測量", "容積移轉", "文資審查", 
                "鑑界(建築線與地界線相符)", "消防審查", "廢巷改道", "拆照", 
                "疑似礦區會辦", "樹木保護審查", "山坡地涉及水保計畫", "原容積審查", "畸零地檢討"
            ], 
            "是否辦理": "⚪ 待確認", "進度狀態": "⚪ 未開始", "備註": ""
        })

def load_notes():
    if not os.path.exists(path_notes):
        return [{"title": "新紀錄", "content": ""}]
    with open(path_notes, "r", encoding="utf-8") as f:
        return json.load(f)

def save_notes(notes_list):
    with open(path_notes, "w", encoding="utf-8") as f:
        json.dump(notes_list, f, ensure_ascii=False, indent=4)

if 'temp_notes_mid' not in st.session_state or st.session_state.get('notes_mid_last_proj') != curr_proj:
    st.session_state.temp_notes_mid = load_notes()
    st.session_state.notes_mid_last_proj = curr_proj

# --- 4. 統計看板 ---
df_mid = load_checklist()
status_handle = df_mid["是否辦理"].value_counts()
status_progress = df_mid["進度狀態"].value_counts()

col_stat1, col_stat2, col_spacer = st.columns([1, 1, 3])
with col_stat1:
    st.metric("✅ 需辦理", status_handle.get("✅ 需辦理", 0))
with col_stat2:
    st.metric("🆗 已結案", status_progress.get("🆗 已結案", 0))

st.divider()

# --- 5. 核心：Check List 表格 (移除滾動軸修正) ---
st.subheader("🔍 執照審查階段 Check List")

opt_handle = ["⚪ 待確認", "✅ 需辦理", "➖ 不涉及"]
opt_status = ["⚪ 未開始", "⏳ 辦理中", "📝 補正中", "🆗 已結案", "⚠️ 遇到問題"]

# --- 關鍵修正：計算不產生滾動軸的高度 ---
# 每列約 35.5px + 表頭 38px + 底部緩衝與邊框約 10px
dynamic_height = (len(df_mid) * 35.5) + 48 

with st.form("form_checklist_mid"):
    e_mid = st.data_editor(
        df_mid, 
        use_container_width=True, 
        hide_index=True, 
        num_rows="dynamic", 
        height=int(dynamic_height), # 強制設定計算後的高度
        column_config={
            "評估項目": st.column_config.TextColumn("評估項目", width="medium"),
            "是否辦理": st.column_config.SelectboxColumn("是否辦理", options=opt_handle, width="small"),
            "進度狀態": st.column_config.SelectboxColumn("進度狀態", options=opt_status, width="small"),
            "備註": st.column_config.TextColumn("備註", width="large")
        }
    )
    if st.form_submit_button("💾 儲存 Check List 變更", use_container_width=True):
        e_mid.to_csv(path_checklist, index=False, encoding='utf-8-sig')
        st.success("✨ Check List 已儲存！")
        st.rerun()

# --- 6. 核心：執照中專屬便利貼 ---
st.divider()
st.subheader("📌 執照中重要備忘")

col_note_btn1, col_note_btn2 = st.columns([1, 4])
with col_note_btn1:
    if st.button("➕ 新增便利貼"):
        st.session_state.temp_notes_mid.append({"title": "新紀錄", "content": ""})
        st.rerun()

cols = st.columns(3)
updated_notes = []

for idx, note in enumerate(st.session_state.temp_notes_mid):
    with cols[idx % 3]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                new_title = st.text_input(f"標題_{idx}", value=note["title"], key=f"title_{idx}_mid", label_visibility="collapsed")
            with c2:
                if st.button("🗑️", key=f"del_{idx}_mid"):
                    st.session_state.temp_notes_mid.pop(idx)
                    st.rerun()
            new_content = st.text_area(f"內容_{idx}", value=note["content"], key=f"content_{idx}_mid", height=120, label_visibility="collapsed")
            updated_notes.append({"title": new_title, "content": new_content})

if st.button("💾 儲存便利貼內容", use_container_width=True):
    save_notes(updated_notes)
    st.session_state.temp_notes_mid = updated_notes
    st.success("✅ 便利貼已更新！")
    st.rerun()