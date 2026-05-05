import streamlit as st
from pathlib import Path

# 1. 定義路徑邏輯
BASE_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(exist_ok=True)

def list_projects():
    """
    動態讀取專案資料夾清單 (移除快取，確保即時更新)
    """
    # 掃描資料夾
    projects = sorted([d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()])
    
    # 如果完全沒專案，自動建立一個「預設專案」避免系統崩潰
    if not projects:
        default_proj = "預設專案"
        (PROJECTS_DIR / default_proj).mkdir(parents=True, exist_ok=True)
        return [default_proj]
    
    return projects

def init_project_state():
    """
    初始化專案數據狀態與 Session State
    """
    # 獲取最新專案清單
    all_p = list_projects()
    
    # 處理 URL 參數 (讓頁面重整後能維持在同一個專案)
    url_proj = st.query_params.get("p")
    
    # 初始化 Session 中的選定專案
    if 'selected_project' not in st.session_state:
        if url_proj in all_p:
            st.session_state.selected_project = url_proj
        else:
            st.session_state.selected_project = all_p[0]
    
    # 確保選定的專案如果被刪除了，會自動跳回第一個專案
    if st.session_state.selected_project not in all_p:
        st.session_state.selected_project = all_p[0]
            
    return all_p, st.session_state.selected_project

def create_project_folder(new_name):
    """
    建立新專案資料夾結構 (由 ui_components 調用)
    """
    if not new_name:
        return False, "專案名稱不能為空"
    
    new_path = PROJECTS_DIR / new_name
    if new_path.exists():
        return False, "專案名稱已存在"
    
    try:
        new_path.mkdir(parents=True)
        # 初始化子目錄結構
        (new_path / "photos").mkdir(exist_ok=True)
        (new_path / "construction_photos").mkdir(exist_ok=True)
        return True, "建立成功"
    except Exception as e:
        return False, f"建立失敗: {str(e)}"