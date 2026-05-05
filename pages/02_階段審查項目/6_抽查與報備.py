import streamlit as st
import pandas as pd
import json
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：在子頁面中不再重複執行設定與渲染側邊欄
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
        hr { margin-top: 0.8rem !important; margin-bottom: 1.5rem !important; }
        [data-testid="stForm"] { padding: 0.5rem 0rem !important; border: none !important; }
        [data-testid="stTable"] { overflow: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 路徑設定 (使用 Path 物件)
project_dir = PROJECTS_DIR / curr_proj
path_public = project_dir / "process_public_review.csv"
path_report = project_dir / "process_report_items.csv"
path_notes = project_dir / "notes_inspection.json"

# 確保目錄存在
if not project_dir.exists():
    project_dir.mkdir(parents=True, exist_ok=True)

# --- 4. 資料處理函數 ---

def load_data(path, default_items):
    # 標準欄位順序
    cols = ["項目名稱", "是否辦理", "進度狀態", "審查單位", "協力廠商", "備註"]
    
    if path.exists():
        try:
            df = pd.read_csv(path, dtype=str, encoding='utf-8-sig').fillna("")
            # 自動補齊缺失欄位
            for c in cols:
                if c not in df.columns:
                    if c == "是否辦理": df[c] = "⚪ 待確認"
                    elif c == "進度狀態": df[c] = "⚪ 未開始"
                    else: df[c] = ""
            return df[cols]
        except Exception as e:
            st.error(f"讀取資料失敗 ({path.name}): {e}")
            return pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame({"項目名稱": default_items})
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

# 5. 狀態管理：切換專案時強制重載便利貼
if 'notes_insp' not in st.session_state or st.session_state.get('last_proj_insp') != curr_proj:
    st.session_state.notes_insp = load_notes()
    st.session_state.last_proj_insp = curr_proj

# 載入表格資料
df_public = load_data(path_public, ["都審抽查", "建照抽查", "結構抽查", "消防抽查"])
df_report = load_data(path_report, ["開工報備", "震後報備", "變更設計報備", "竣工報備"])

# 編輯器選單與配置
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

# --- 6. 介面渲染 ---

st.title("📝 抽查與報備")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# 表格一：公部門審查
st.subheader("🏛️ 公部門審查 (抽查)")
h_pub = (len(df_public) * 35.5) + 48
with st.form("form_public"):
    e_pub = st.data_editor(
        df_public, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        height=int(h_pub), 
        column_config=column_config,
        key=f"editor_pub_{curr_proj}"
    )
    if st.form_submit_button("💾 儲存公部門審查變更", use_container_width=True):
        e_pub.to_csv(path_public, index=False, encoding='utf-8-sig')
        st.success("✨ 公部門審查資料已儲存！")
        st.rerun()

st.write("")

# 表格二：報備項目
st.subheader("📋 報備項目")
h_rep = (len(df_report) * 35.5) + 48
with st.form("form_report"):
    e_rep = st.data_editor(
        df_report, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        height=int(h_rep), 
        column_config=column_config,
        key=f"editor_rep_{curr_proj}"
    )
    if st.form_submit_button("💾 儲存報備項目變更", use_container_width=True):
        e_rep.to_csv(path_report, index=False, encoding='utf-8-sig')
        st.success("✨ 報備項目資料已儲存！")
        st.rerun()

# --- 7. 核心：便利貼 ---
st.divider()
st.subheader("📌 抽查與報備重要備忘")

col_n1, col_n2 = st.columns([1, 4])
with col_n1:
    if st.button("➕ 新增便利貼"):
        st.session_state.notes_insp.append({"title": "新紀錄", "content": ""})
        st.rerun()

cols = st.columns(3)
updated_notes = []

# 使用 list() 包裹以避免刪除時的索引錯誤
for idx, note in enumerate(list(st.session_state.notes_insp)):
    with cols[idx % 3]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1: 
                nt = st.text_input(
                    f"T_{idx}", 
                    value=note["title"], 
                    key=f"t_{idx}_{curr_proj}_insp", 
                    label_visibility="collapsed"
                )
            with c2: 
                if st.button("🗑️", key=f"d_{idx}_{curr_proj}_insp"):
                    st.session_state.notes_insp.pop(idx)
                    st.rerun()
            nc = st.text_area(
                f"C_{idx}", 
                value=note["content"], 
                key=f"c_{idx}_{curr_proj}_insp", 
                height=120, 
                label_visibility="collapsed"
            )
            updated_notes.append({"title": nt, "content": nc})

if st.button("💾 儲存便利貼內容", use_container_width=True):
    try:
        with open(path_notes, "w", encoding="utf-8") as f:
            json.dump(updated_notes, f, ensure_ascii=False, indent=4)
        st.session_state.notes_insp = updated_notes
        st.success("✅ 抽查與報備備忘錄已儲存！")
        st.rerun()
    except Exception as e:
        st.error(f"儲存失敗: {e}")