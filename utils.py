import streamlit as st
import os
import shutil

def init_sidebar():
    # 隱藏原生導航
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🏢 專案管理中心")
        
        # --- 區塊 1：專案切換與新增 ---
        if not os.path.exists("projects"):
            os.makedirs("projects")
            
        projects = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
        if not projects:
            # 如果完全沒專案，建立一個預設的
            if not os.path.exists("projects/預設專案"):
                os.makedirs("projects/預設專案")
            projects = ["預設專案"]

        # 專案選擇器
        if 'current_project' not in st.session_state:
            st.session_state['current_project'] = projects[0]

        selected_proj = st.selectbox(
            "切換目前執行專案",
            projects,
            index=projects.index(st.session_state['current_project'])
        )
        st.session_state['current_project'] = selected_proj

        # 新增專案功能
        new_proj = st.text_input("➕ 新增專案名稱", placeholder="輸入案名後按 Enter")
        if new_proj:
            new_path = f"projects/{new_proj}"
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                st.success(f"專案 {new_proj} 已建立")
                st.rerun()

        # --- 區塊 2：危險區 (刪除專案) ---
        st.markdown("---")
        with st.expander("⚠️ 危險區域"):
            st.warning(f"正在刪除：{st.session_state['current_project']}")
            if st.button("🔥 確定刪除此專案", use_container_width=True):
                target_dir = f"projects/{st.session_state['current_project']}"
                try:
                    # 刪除整個專案資料夾及其內所有檔案
                    shutil.rmtree(target_dir)
                    st.toast(f"已成功刪除專案：{st.session_state['current_project']}")
                    
                    # 重置 session_state 並刷新
                    del st.session_state['current_project']
                    st.rerun()
                except Exception as e:
                    st.error(f"刪除失敗: {e}")

        # --- 區塊 3：左側-主要功能列表 ---
        st.markdown("---")
        st.subheader("🚀 主要功能")
        
        # 自動掃描 pages 資料夾
        if os.path.exists("pages"):
            page_files = sorted([f for f in os.listdir("pages") if f.endswith(".py")])
            for pf in page_files:
                # 取得顯示名稱（去過編號與後綴）
                display_name = pf.replace(".py", "").split("_")[-1]
                if st.button(display_name, use_container_width=True):
                    st.switch_page(f"pages/{pf}")

    return st.session_state['current_project']