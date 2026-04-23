import streamlit as st
import pandas as pd
import os
import json
from utils import init_sidebar

# 0. 基礎配置
st.set_page_config(page_title="申請獎勵項目-候選 / 標章", layout="wide")
curr_proj = init_sidebar()

# --- 💉 視覺修正：緊湊佈局與隱藏滾動軸 ---
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem !important; }
        hr { margin-top: 0.8rem !important; margin-bottom: 1.5rem !important; }
        [data-testid="stForm"] { padding: 0.5rem 0rem !important; border: none !important; }
        [data-testid="stTable"] { overflow: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 路徑定位
project_dir = f"projects/{curr_proj}"
path_review = os.path.join(project_dir, "review_items_process.csv")
path_cert = os.path.join(project_dir, "review_items_final.csv")
path_notes = os.path.join(project_dir, "notes_reward.json") 

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

st.title("📝 申請獎勵項目-候選 / 標章")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 2. 資料載入函數 ---
def load_reward_data(path, is_table_2=False):
    cols = ["評估項目", "是否辦理", "進度狀態", "列管時間", "審查單位", "協力單位", "備註"]
    
    if os.path.exists(path):
        df = pd.read_csv(path, dtype=str).fillna("")
        for c in cols:
            if c not in df.columns:
                if c == "是否辦理": df[c] = "⚪ 待確認"
                elif c == "進度狀態": df[c] = "⚪ 未開始"
                else: df[c] = ""
        return df[cols]
    else:
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

df_r1 = load_reward_data(path_review, False)
df_r2 = load_reward_data(path_cert, True)

# 選單內容
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

# --- 3. 表格渲染 ---
st.subheader("🏆 審查與候選：勘驗前後")
h1 = (len(df_r1) * 35.5) + 48
with st.form("form_t1"):
    e_t1 = st.data_editor(df_r1, num_rows="dynamic", use_container_width=True, hide_index=True, height=int(h1), column_config=column_config)
    if st.form_submit_button("💾 儲存審查與候選變更", use_container_width=True):
        e_t1.to_csv(path_review, index=False, encoding='utf-8-sig'); st.rerun()

st.write("")

st.subheader("🏅 取得標章：使照前後")
h2 = (len(df_r2) * 35.5) + 48
with st.form("form_t2"):
    e_t2 = st.data_editor(df_r2, num_rows="dynamic", use_container_width=True, hide_index=True, height=int(h2), column_config=column_config)
    if st.form_submit_button("💾 儲存取得標章變更", use_container_width=True):
        e_t2.to_csv(path_cert, index=False, encoding='utf-8-sig'); st.rerun()

# --- 4. 獎勵項目專屬便利貼 ---
st.divider()
st.subheader("📌 獎勵項目重要備忘")

if 'notes_reward' not in st.session_state:
    if os.path.exists(path_notes):
        with open(path_notes, "r", encoding="utf-8") as f:
            st.session_state.notes_reward = json.load(f)
    else:
        st.session_state.notes_reward = [{"title": "新紀錄", "content": ""}]

if st.button("➕ 新增便利貼"):
    st.session_state.notes_reward.append({"title": "新紀錄", "content": ""}); st.rerun()

cols = st.columns(3)
updated_notes = []
for idx, note in enumerate(st.session_state.notes_reward):
    with cols[idx % 3]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1: nt = st.text_input(f"T_{idx}", value=note["title"], key=f"t_{idx}_rw", label_visibility="collapsed")
            with c2: 
                if st.button("🗑️", key=f"d_{idx}_rw"):
                    st.session_state.notes_reward.pop(idx); st.rerun()
            nc = st.text_area(f"C_{idx}", value=note["content"], key=f"c_{idx}_rw", height=120, label_visibility="collapsed")
            updated_notes.append({"title": nt, "content": nc})

if st.button("💾 儲存便利貼內容", use_container_width=True):
    with open(path_notes, "w", encoding="utf-8") as f:
        json.dump(updated_notes, f, ensure_ascii=False, indent=4)
    st.session_state.notes_reward = updated_notes
    st.success("✅ 獎勵備忘錄已儲存！")