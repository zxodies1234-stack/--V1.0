import streamlit as st
import pandas as pd
import json
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：在子頁面中不再執行 st.set_page_config 與 render_sidebar
from state_manager import init_project_state, PROJECTS_DIR

# --- 核心修正：取得主程式選定的專案 ---
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    # 備援方案：若 session 中尚未定義則重新初始化一次
    _, curr_proj = init_project_state()

# --- 2. 視覺修正：注入自定義 CSS ---
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem !important; }
        .main .block-container h1 { padding-bottom: 0rem !important; margin-bottom: -0.5rem !important; }
        hr { margin-top: 0.8rem !important; margin-bottom: 1.5rem !important; }
        [data-testid="stForm"] { padding: 0.5rem 0rem !important; border: none !important; }
        [data-testid="stTable"] { overflow: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 路徑設定 (使用 Path 物件)
project_dir = PROJECTS_DIR / curr_proj
path_checklist = project_dir / "process_checklist_post.csv"
path_notes = project_dir / "notes_post.json"

# 確保專案目錄存在
if not project_dir.exists():
    project_dir.mkdir(parents=True, exist_ok=True)

# --- 4. 資料處理邏輯 ---

def load_checklist():
    # 標準欄位順序
    cols = ["評估項目", "是否辦理", "進度狀態", "審查單位", "協力廠商", "備註"]
    
    if path_checklist.exists():
        try:
            df = pd.read_csv(path_checklist, dtype=str, encoding='utf-8-sig').fillna("")
            # 自動補齊缺失欄位
            for c in cols:
                if c not in df.columns:
                    if c == "是否辦理": df[c] = "⚪ 待確認"
                    elif c == "進度狀態": df[c] = "⚪ 未開始"
                    else: df[c] = ""
            return df[cols]
        except Exception as e:
            st.error(f"讀取 Check List 失敗: {e}")
            return pd.DataFrame(columns=cols)
    else:
        # 預設執照後項目
        items = ["使用執照申報", "室內裝修竣工", "消防竣工查驗", "產權登記保存", "公設點交"]
        df = pd.DataFrame({"評估項目": items})
        df["是否辦理"] = "⚪ 待確認"
        df["進度狀態"] = "⚪ 未開始"
        df["審查單位"] = ""
        df["協力廠商"] = ""
        df["備註"] = ""
        return df[cols]

def load_notes():
    if not path_notes.exists():
        return [{"title": "新紀錄", "content": ""}]
    try:
        with open(path_notes, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if data else [{"title": "新紀錄", "content": ""}]
    except:
        return [{"title": "新紀錄", "content": ""}]

def save_notes(notes_list):
    try:
        with open(path_notes, "w", encoding="utf-8") as f:
            json.dump(notes_list, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

# 5. 狀態管理：切換專案時強制重載數據
if 'temp_notes_post' not in st.session_state or st.session_state.get('notes_post_last_proj') != curr_proj:
    st.session_state.temp_notes_post = load_notes()
    st.session_state.notes_post_last_proj = curr_proj

# --- 6. UI 介面渲染 ---
st.title("📝 各階段審查：執照後")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 統計看板 ---
df_post = load_checklist()
status_handle = df_post["是否辦理"].value_counts()
status_progress = df_post["進度狀態"].value_counts()

col_stat1, col_stat2, col_spacer = st.columns([1, 1, 3])
with col_stat1:
    st.metric("✅ 需辦理", status_handle.get("✅ 需辦理", 0))
with col_stat2:
    st.metric("🆗 已結案", status_progress.get("🆗 已結案", 0))

st.divider()

# --- 核心：Check List 表格 ---
st.subheader("🔍 執照審查階段 Check List")

opt_handle = ["⚪ 待確認", "✅ 需辦理", "➖ 不涉及"]
opt_status = ["⚪ 未開始", "⏳ 辦理中", "📝 補正中", "🆗 已結案", "⚠️ 遇到問題"]

# 動態高度計算 (每列 35.5px + 表頭 48px)
dynamic_height = (len(df_post) * 35.5) + 48 

with st.form("form_checklist_post"):
    e_post = st.data_editor(
        df_post, 
        use_container_width=True, 
        hide_index=True, 
        num_rows="dynamic", 
        height=int(dynamic_height),
        column_config={
            "評估項目": st.column_config.TextColumn("評估項目", width="medium"),
            "是否辦理": st.column_config.SelectboxColumn("是否辦理", options=opt_handle, width="small"),
            "進度狀態": st.column_config.SelectboxColumn("進度狀態", options=opt_status, width="small"),
            "審查單位": st.column_config.TextColumn("審查單位", width="small"),
            "協力廠商": st.column_config.TextColumn("協力廠商", width="small"),
            "備註": st.column_config.TextColumn("備註", width="large")
        }
    )
    if st.form_submit_button("💾 儲存 Check List 變更", use_container_width=True):
        e_post.to_csv(path_checklist, index=False, encoding='utf-8-sig')
        st.success("✨ 執照後 Check List 已儲存！")
        st.rerun()

# --- 核心：執照後專屬便利貼 ---
st.divider()
st.subheader("📌 執照後重要備忘")

col_note_btn1, col_note_btn2 = st.columns([1, 4])
with col_note_btn1:
    if st.button("➕ 新增便利貼"):
        st.session_state.temp_notes_post.append({"title": "新紀錄", "content": ""})
        st.rerun()

cols = st.columns(3)
updated_notes = []

# 使用 list() 包裹以防在循環中 pop 導致 index 錯誤
for idx, note in enumerate(list(st.session_state.temp_notes_post)):
    with cols[idx % 3]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                new_title = st.text_input(
                    f"標題_{idx}", 
                    value=note["title"], 
                    key=f"title_{idx}_{curr_proj}_post", 
                    label_visibility="collapsed"
                )
            with c2:
                if st.button("🗑️", key=f"del_{idx}_{curr_proj}_post"):
                    st.session_state.temp_notes_post.pop(idx)
                    st.rerun()
            
            new_content = st.text_area(
                f"內容_{idx}", 
                value=note["content"], 
                key=f"content_{idx}_{curr_proj}_post", 
                height=120, 
                label_visibility="collapsed"
            )
            updated_notes.append({"title": new_title, "content": new_content})

if st.button("💾 儲存便利貼內容", use_container_width=True):
    if save_notes(updated_notes):
        st.session_state.temp_notes_post = updated_notes
        st.success("✅ 執照後專屬便利貼已更新！")
        st.rerun()