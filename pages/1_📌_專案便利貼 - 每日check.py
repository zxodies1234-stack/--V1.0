import streamlit as st
import json
import os
from utils import init_sidebar

# 0. 寬螢幕設定
st.set_page_config(layout="wide")
curr_proj = init_sidebar()
project_dir = f"projects/{curr_proj}"
notes_path = os.path.join(project_dir, "notes.json")

if not os.path.exists(project_dir):
    os.makedirs(project_dir)

st.title(f"📌 專案便利貼：{curr_proj}")
st.caption("記錄專案中的疑難雜症、待辦事項或臨時想法")

# --- 1. 核心邏輯：載入與儲存 ---
def load_notes():
    if not os.path.exists(notes_path):
        return [{"title": "新便利貼", "content": ""}]
    with open(notes_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_notes(notes_list):
    with open(notes_path, "w", encoding="utf-8") as f:
        json.dump(notes_list, f, ensure_ascii=False, indent=4)

# 使用 Session State 管理臨時編輯狀態
if 'temp_notes' not in st.session_state or st.session_state.get('notes_last_proj') != curr_proj:
    st.session_state.temp_notes = load_notes()
    st.session_state.notes_last_proj = curr_proj

# --- 2. 便利貼控制面板 ---
col_ctrl1, col_ctrl2 = st.columns([1, 6])
with col_ctrl1:
    if st.button("➕ 新增便利貼"):
        st.session_state.temp_notes.append({"title": "新便利貼", "content": ""})
        st.rerun()

# --- 3. 顯示便利貼矩陣 ---
cols = st.columns(3)
updated_notes = []

for idx, note in enumerate(st.session_state.temp_notes):
    with cols[idx % 3]:
        with st.container(border=True):
            # 標題與刪除按鈕
            c1, c2 = st.columns([4, 1])
            with c1:
                # 為了避免 ID 重複報錯，key 加入了專案名稱與索引
                new_title = st.text_input(f"標題 {idx+1}", value=note["title"], key=f"title_{idx}_{curr_proj}", label_visibility="collapsed")
            with c2:
                if st.button("🗑️", key=f"del_{idx}_{curr_proj}"):
                    st.session_state.temp_notes.pop(idx)
                    st.rerun()
            
            new_content = st.text_area(f"內容 {idx+1}", value=note["content"], key=f"content_{idx}_{curr_proj}", height=150, label_visibility="collapsed", placeholder="請輸入紀錄內容...")
            
            updated_notes.append({"title": new_title, "content": new_content})

st.divider()

# --- 4. 儲存變更 (已移除 type="primary"，變回白色底) ---
if st.button("💾 儲存變更", use_container_width=True):
    save_notes(updated_notes)
    st.session_state.temp_notes = updated_notes
    st.success("✅ 所有便利貼內容已成功儲存！")
    st.rerun()