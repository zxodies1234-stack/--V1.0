import streamlit as st
import shutil
from pathlib import Path

def render_sidebar(projects, current):
    """
    標準化側邊欄：支援二級目錄優化、專案切換、新增與刪除專案
    """
    # 1. 視覺優化 CSS
    st.markdown("""
        <style>
            section[data-testid="stSidebarNav"] > ul > li > div > span {
                font-weight: bold !important;
                color: #1E1E1E !important;
                font-size: 1.05rem !important;
            }
            .stButton > button {
                margin-top: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🏗️ 建築專案控制台")
        st.divider()
        
        # 2. 專案切換器
        selected = st.selectbox(
            "切換目前執行專案：",
            projects,
            index=projects.index(current) if current in projects else 0,
            key="global_project_selector"
        )
        
        st.info(f"📍 目前選定：{selected}")
        st.divider()

        # 3. 專案管理功能
        
        @st.dialog("建立新建築專案")
        def create_project_dialog():
            new_name = st.text_input("請輸入專案名稱 (例如：玉成200)", placeholder="請輸入專案名稱")
            st.write("系統將自動建立法規與照片資料夾結構。")
            
            if st.button("確認建立", use_container_width=True):
                if new_name:
                    from state_manager import create_project_folder
                    success, msg = create_project_folder(new_name)
                    if success:
                        st.session_state.selected_project = new_name
                        st.session_state.global_project_selector = new_name
                        st.success(f"專案「{new_name}」已建立！")
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("名稱不能為空")

        @st.dialog("永久刪除專案")
        def delete_project_dialog(target):
            st.warning(f"確定要永久刪除「{target}」嗎？")
            st.error("此操作將刪除該專案所有 CSV 數據、面積表與照片，且無法復原。")
            
            # --- 核心修正：將 color="red" 改為 type="primary" ---
            # type="primary" 在大多數 Streamlit 版本中都會顯示為鮮艷的紅色/橘色
            if st.button("確認永久刪除", type="primary", use_container_width=True):
                from state_manager import PROJECTS_DIR
                target_path = PROJECTS_DIR / target
                if target_path.exists():
                    shutil.rmtree(target_path)
                    if "selected_project" in st.session_state:
                        del st.session_state.selected_project
                    st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ 新增專案", use_container_width=True):
                create_project_dialog()
        with col2:
            if st.button("🗑️ 刪除專案", use_container_width=True):
                delete_project_dialog(selected)

        st.divider()

    return selected

def render_calc_result(title, value, unit="㎡", formula=None):
    """標準化計算結果組件"""
    formula_html = f'<div style="color: #666; font-size: 0.85rem; margin-top: 4px;">算式：{formula}</div>' if formula else ""
    st.markdown(f'''
        <style>
            .calc-result-container {{
                padding: 16px;
                border-left: 6px solid #ff4b4b;
                background-color: #fcfcfc;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                margin: 10px 0 20px 0;
            }}
            .calc-result-title {{ font-weight: bold; font-size: 1.1rem; }}
            .calc-result-value {{ color: #ff4b4b; font-size: 1.3rem; margin-left: 8px; }}
        </style>
        <div class="calc-result-container">
            <div class="calc-result-title">🎯 {title}：<span class="calc-result-value">{value:,.2f} {unit}</span></div>
            {formula_html}
        </div>
    ''', unsafe_allow_html=True)

def section_header(title, icon="📊"):
    st.subheader(f"{icon} {title}")
    st.markdown("---")