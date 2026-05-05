import streamlit as st
import json
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：在多頁面模式下，子頁面通常可以直接存取 app.py 初始化過的 session_state
from state_manager import PROJECTS_DIR

# --- 核心修正：移除 st.set_page_config 與 render_sidebar ---
# 這些功能現在由 app.py 統一接管

# 取得目前在 app.py 中選定的專案
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    # 備援方案：若直接跑此頁面則預設第一個 (開發除錯用)
    curr_proj = "未選定專案"

# 2. 定義資料路徑
project_dir = PROJECTS_DIR / curr_proj
notes_path = project_dir / "notes.json"

# 如果專案資料夾不存在則建立
if not project_dir.exists():
    project_dir.mkdir(parents=True, exist_ok=True)

# --- 2. 核心邏輯：載入與儲存 ---
def load_notes():
    if not notes_path.exists():
        return [{"title": "新便利貼", "content": ""}]
    try:
        with open(notes_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if data else [{"title": "新便利貼", "content": ""}]
    except Exception as e:
        st.error(f"讀取便利貼失敗: {e}")
        return [{"title": "新便利貼", "content": ""}]

def save_notes(notes_list):
    try:
        with open(notes_path, "w", encoding="utf-8") as f:
            json.dump(notes_list, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f"儲存失敗: {e}")
        return False

# 3. 狀態管理：確保切換專案時強制刷新數據
if 'temp_notes' not in st.session_state or st.session_state.get('notes_last_proj') != curr_proj:
    st.session_state.temp_notes = load_notes()
    st.session_state.notes_last_proj = curr_proj

# --- 4. UI 介面渲染 ---
st.title(f"📌 專案便利貼：{curr_proj}")
st.caption("記錄專案中的疑難雜症、待辦事項或臨時想法")

# 控制面板
col_ctrl1, col_ctrl2 = st.columns([1, 6])
with col_ctrl1:
    if st.button("➕ 新增便利貼"):
        st.session_state.temp_notes.append({"title": "新便利貼", "content": ""})
        st.rerun()

# 顯示便利貼矩陣 (3欄佈局)
cols = st.columns(3)
updated_notes = []

# 遍歷 Session 中的便利貼
# 使用 list() 包裹以避免在迴圈中 pop 導致的 index 錯誤
for idx, note in enumerate(list(st.session_state.temp_notes)):
    with cols[idx % 3]:
        with st.container(border=True):
            # 標題列
            c1, c2 = st.columns([4, 1])
            with c1:
                new_title = st.text_input(
                    f"標題 {idx+1}", 
                    value=note["title"], 
                    key=f"title_{idx}_{curr_proj}", 
                    label_visibility="collapsed"
                )
            with c2:
                # 刪除功能
                if st.button("🗑️", key=f"del_{idx}_{curr_proj}"):
                    st.session_state.temp_notes.pop(idx)
                    st.rerun()
            
            # 內容區域
            new_content = st.text_area(
                f"內容 {idx+1}", 
                value=note["content"], 
                key=f"content_{idx}_{curr_proj}", 
                height=150, 
                label_visibility="collapsed", 
                placeholder="請輸入紀錄內容..."
            )
            
            updated_notes.append({"title": new_title, "content": new_content})

st.divider()

# --- 5. 儲存變更 ---
# 改用簡化後的按鈕名稱
if st.button("💾 儲存變更", use_container_width=True):
    if save_notes(updated_notes):
        st.session_state.temp_notes = updated_notes
        st.success("✅ 所有便利貼內容已成功儲存！")
        st.rerun()