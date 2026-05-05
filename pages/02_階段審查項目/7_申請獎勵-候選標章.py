import streamlit as st
import pandas as pd
import json
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：子頁面不再重複執行配置與側邊欄渲染
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
path_review = project_dir / "review_items_process.csv"
path_cert = project_dir / "review_items_final.csv"
path_notes = project_dir / "notes_reward.json"

# 確保目錄存在
if not project_dir.exists():
    project_dir.mkdir(parents=True, exist_ok=True)

# --- 4. 資料載入函數 ---
def load_reward_data(path, is_table_2=False):
    cols = ["評估項目", "是否辦理", "進度狀態", "列管時間", "審查單位", "協力單位", "備註"]
    
    if path.exists():
        try:
            df = pd.read_csv(path, dtype=str, encoding='utf-8-sig').fillna("")
            # 自動檢查並補齊新欄位
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
        # 預設項目清單
        if not is_table_2:
            data = [
                {"評估項目": "耐震設計審查", "列管時間": "放樣勘驗前"},
                {"評估項目": "無障礙性能評估", "列管時間": "1F樓板勘驗前"},
                {"評估項目": "結構安全性能審查", "列管時間": "放樣勘驗前"},
                {"評估項目": "綠建築候選", "列管時間": "1F樓板勘驗前"},
                {"評估項目": "智慧建築候選", "列管時間": "1F樓板勘驗前"},
                {"評估項目": "1+級能效候選", "列管時間": "1F樓板勘驗前"},
                {"評估項目": "綠建築自治條例專章", "列管時間": "1F樓板勘驗前"}
            ]
        else:
            data = [
                {"評估項目": "耐震設計標章", "列管時間": "使照前"},
                {"評估項目": "無障礙性能標章", "列管時間": "使照後3個月"},
                {"評估項目": "結構安全性能標章", "列管時間": "使照後3個月"},
                {"評估項目": "綠建築標章", "列管時間": "使照後2年內"},
                {"評估項目": "智慧建築標章", "列管時間": "使照後2年內"},
                {"評估項目": "1+級能效標章", "列管時間": "使照後2年內"}
            ]
        df = pd.DataFrame(data)
        df["是否辦理"] = "⚪ 待確認"
        df["進度狀態"] = "⚪ 未開始"
        df["審查單位"] = ""
        df["協力單位"] = ""
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
if 'notes_reward' not in st.session_state or st.session_state.get('last_proj_reward') != curr_proj:
    st.session_state.notes_reward = load_notes()
    st.session_state.last_proj_reward = curr_proj

# 載入表格資料
df_r1 = load_reward_data(path_review, False)
df_r2 = load_reward_data(path_cert, True)

# 選單定義
opt_handle = ["⚪ 待確認", "✅ 需辦理", "➖ 不涉及"]
opt_status = ["⚪ 未開始", "⏳ 辦理中", "📝 補正中", "🆗 已結案", "⚠️ 遇到問題"]

column_config = {
    "評估項目": st.column_config.TextColumn("評估項目", width="medium"),
    "是否辦理": st.column_config.SelectboxColumn("是否辦理", options=opt_handle, width="small"),
    "進度狀態": st.column_config.SelectboxColumn("進度狀態", options=opt_status, width="small"),
    "列管時間": st.column_config.TextColumn("列管時間", width="small"),
    "審查單位": st.column_config.TextColumn("審查單位", width="small"),
    "協力單位": st.column_config.TextColumn("協力單位", width="small"),
    "備註": st.column_config.TextColumn("備註", width="large")
}

# --- 6. 介面渲染 ---

st.title("📝 申請獎勵項目-候選 / 標章")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# 表格一：勘驗前後
st.subheader("🏆 審查與候選：勘驗前後")
h1 = (len(df_r1) * 35.5) + 48
with st.form("form_t1"):
    e_t1 = st.data_editor(
        df_r1, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        height=int(h1), 
        column_config=column_config,
        key=f"editor_rw1_{curr_proj}"
    )
    if st.form_submit_button("💾 儲存審查與候選變更", use_container_width=True):
        e_t1.to_csv(path_review, index=False, encoding='utf-8-sig')
        st.success("✨ 勘驗前後審查項目已儲存！")
        st.rerun()

st.write("")

# 表格二：使照前後
st.subheader("🏅 取得標章：使照前後")
h2 = (len(df_r2) * 35.5) + 48
with st.form("form_t2"):
    e_t2 = st.data_editor(
        df_r2, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        height=int(h2), 
        column_config=column_config,
        key=f"editor_rw2_{curr_proj}"
    )
    if st.form_submit_button("💾 儲存取得標章變更", use_container_width=True):
        e_t2.to_csv(path_cert, index=False, encoding='utf-8-sig')
        st.success("✨ 使照前後標章項目已儲存！")
        st.rerun()

# --- 7. 核心：便利貼 ---
st.divider()
st.subheader("📌 獎勵項目重要備忘")

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("➕ 新增便利貼"):
        st.session_state.notes_reward.append({"title": "新紀錄", "content": ""})
        st.rerun()

cols = st.columns(3)
updated_notes = []

# 使用 list() 包裹以避免刪除時的索引錯誤
for idx, note in enumerate(list(st.session_state.notes_reward)):
    with cols[idx % 3]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1: 
                nt = st.text_input(
                    f"T_{idx}", 
                    value=note["title"], 
                    key=f"t_{idx}_{curr_proj}_rw", 
                    label_visibility="collapsed"
                )
            with c2: 
                if st.button("🗑️", key=f"d_{idx}_{curr_proj}_rw"):
                    st.session_state.notes_reward.pop(idx)
                    st.rerun()
            nc = st.text_area(
                f"C_{idx}", 
                value=note["content"], 
                key=f"c_{idx}_{curr_proj}_rw", 
                height=120, 
                label_visibility="collapsed"
            )
            updated_notes.append({"title": nt, "content": nc})

if st.button("💾 儲存便利貼內容", use_container_width=True):
    try:
        with open(path_notes, "w", encoding="utf-8") as f:
            json.dump(updated_notes, f, ensure_ascii=False, indent=4)
        st.session_state.notes_reward = updated_notes
        st.success("✅ 獎勵備忘錄已儲存！")
        st.rerun()
    except Exception as e:
        st.error(f"儲存失敗: {e}")