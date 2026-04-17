import streamlit as st
import os
import shutil

def init_sidebar():
    # --- 💉 CSS 樣式注入 ---
    st.markdown("""
        <style>
            [data-testid="stSidebar"] .stButton button {
                font-size: 15px !important;
                font-weight: 500 !important;
                padding: 5px 10px !important;
                min-height: 38px !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] p {
                font-size: 15px !important; 
                font-weight: 600 !important;
                color: #31333F !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] .stButton button {
                font-size: 13px !important;
                font-weight: 400 !important;
                min-height: 30px !important;
                padding: 2px 8px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("🏢 專案管理")
    
    if not os.path.exists("projects"): os.makedirs("projects")

    if 'expanded_states' not in st.session_state:
        st.session_state['expanded_states'] = {
            "group1": True, "group2": False, "group3": False, "group4": False, "group5": False
        }

    def set_only_expanded(target_group):
        for key in st.session_state['expanded_states']:
            st.session_state['expanded_states'][key] = (key == target_group)

    # --- 1. 專案管理區塊 ---
    exp_manage = st.sidebar.expander("➕ 新增/刪除專案", expanded=False)
    new_proj = exp_manage.text_input("新專案名稱", key="add_proj_input")
    if exp_manage.button("建立專案", key="create_btn", use_container_width=True):
        if new_proj:
            os.makedirs(f"projects/{new_proj}", exist_ok=True)
            st.rerun()
    
    projects = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
    curr_proj = st.sidebar.selectbox("選擇目前執行專案", projects if projects else ["預設專案"], key="sidebar_proj_select")
    st.sidebar.divider()

    # --- 2. ⭐ 置頂核心功能 ---
    if st.sidebar.button("📌 專案便利貼 - 每日check", key="nav_memo_main", use_container_width=True):
        set_only_expanded(None) 
        st.switch_page("pages/1_📌_專案便利貼 - 每日check.py")

    # --- 3. 🚀 功能導航 ---
    st.sidebar.title("🚀 功能導航")

    # 第一組：專案進度控管
    exp1 = st.sidebar.expander("📅 專案進度控管", expanded=st.session_state['expanded_states']["group1"])
    if exp1.button("📊 專案進度", key="nav_prog", use_container_width=True):
        set_only_expanded("group1")
        st.switch_page("pages/2_📊_專案進度.py")

    # 第二組：各階段審查項目 (17:32 截圖新序號 3-7)
    exp5 = st.sidebar.expander("📝 各階段審查項目", expanded=st.session_state['expanded_states']["group5"])
    if exp5.button("📝 執照前", key="nav_before", use_container_width=True):
        set_only_expanded("group5")
        st.switch_page("pages/3_📝_執照前.py")
    if exp5.button("📝 執照中", key="nav_during", use_container_width=True):
        set_only_expanded("group5")
        st.switch_page("pages/4_📝_執照中.py")
    if exp5.button("📝 執照後", key="nav_after", use_container_width=True):
        set_only_expanded("group5")
        st.switch_page("pages/5_📝_執照後.py")
    if exp5.button("📝 抽查與報備", key="nav_check_report", use_container_width=True):
        set_only_expanded("group5")
        st.switch_page("pages/6_📝_抽查與報備.py")
    if exp5.button("📝 審查項目", key="nav_review", use_container_width=True):
        set_only_expanded("group5")
        st.switch_page("pages/7_📝_審查項目.py")

    # 第三組：面積法規檢討 (17:32 截圖新序號 8-10)
    exp2 = st.sidebar.expander("📏 面積法規檢討", expanded=st.session_state['expanded_states']["group2"])
    if exp2.button("📐 面積表", key="nav_area", use_container_width=True):
        set_only_expanded("group2")
        st.switch_page("pages/8_📐_面積表.py")
    if exp2.button("🏢 各層面積計算", key="nav_calc", use_container_width=True):
        set_only_expanded("group2")
        st.switch_page("pages/9_🏢_各層面積計算.py") 
    if exp2.button("⚖️ 相關法規", key="nav_law", use_container_width=True):
        set_only_expanded("group2")
        st.switch_page("pages/10_⚖️_相關法規.py")

    # 第四組：現場影像紀錄 (17:32 截圖新序號 11-12)
    exp3 = st.sidebar.expander("🖼️ 現場影像紀錄", expanded=st.session_state['expanded_states']["group3"])
    if exp3.button("🖼️ 基地照片", key="nav_pic", use_container_width=True):
        set_only_expanded("group3")
        st.switch_page("pages/11_🖼️_基地照片.py")
    if exp3.button("📸 施工影像紀錄", key="nav_video", use_container_width=True):
        set_only_expanded("group3")
        st.switch_page("pages/12_📸_施工影像紀錄.py")

    # 第五組：資源管理 (17:32 截圖新序號 13)
    exp4 = st.sidebar.expander("📂 資源管理", expanded=st.session_state['expanded_states']["group4"])
    if exp4.button("📞 聯絡人清單", key="nav_contact", use_container_width=True):
        set_only_expanded("group4")
        st.switch_page("pages/13_📞_聯絡人清單.py")

    return curr_proj