import streamlit as st
import os
import shutil

def init_sidebar():
    # 1. 紀錄當前活動頁面 (初始化)
    if 'active_nav' not in st.session_state:
        st.session_state['active_nav'] = "nav_memo"

    # 2. 導覽跳轉函式
    def navigate_to(page_path, nav_key, group_key):
        st.session_state['active_nav'] = nav_key
        if 'expanded_states' in st.session_state:
            for key in st.session_state['expanded_states']:
                st.session_state['expanded_states'][key] = (key == group_key)
        st.switch_page(page_path)

    # 3. 💉 CSS 注入：科技感雙排浮水印與按鈕樣式
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none !important; }
            
            /* --- 科技感雙排浮水印 --- */
            .stApp::after {
                content: "洪睿宇建築師事務所 \\A JYH Architects ";
                position: fixed;
                bottom: 40px;
                right: 40px;
                opacity: 0.4;                  
                font-size: 24px;                
                color: #1E293B;                
                pointer-events: none; 
                z-index: 999999;
                font-weight: 500;              
                text-align: right;             
                line-height: 1.3;
                white-space: pre;                
                font-family: "Inter", "Segoe UI", "Roboto", sans-serif;
                letter-spacing: 4px;           
                font-style: normal;            
                margin-right: -10px; 
            }
            
            /* 基礎按鈕樣式 */
            [data-testid="stSidebar"] .stButton button {
                background-color: #f8f9fb !important;
                border: 1px solid #ebedf0 !important;
                color: #31333F !important;
                font-weight: 400 !important; 
                font-size: 14px !important;
                text-align: left !important;
                justify-content: flex-start !important;
                display: flex !important;
                width: 100% !important; 
                min-height: 40px !important;
                border-radius: 6px !important;
                margin-bottom: 2px !important;
            }

            /* 滑鼠經過效果 */
            [data-testid="stSidebar"] .stButton button:hover {
                border-color: #ff4b4b !important;
                color: #ff4b4b !important;
                background-color: #ffffff !important;
            }

            /* 修正 Expander 標題字體 */
            [data-testid="stSidebar"] [data-testid="stExpander"] p {
                font-weight: 400 !important;
                font-size: 14px !important;
                color: #555 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("🏢 專案管理")
    
    # --- 專案資料夾邏輯 ---
    if not os.path.exists("projects"): os.makedirs("projects")
    
    # --- 解決網頁版跳回預設專案的關鍵處 ---
    projects = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
    if not projects: projects = ["預設專案"]

    # 初始化 Session State 中的選定專案
    if 'selected_project' not in st.session_state:
        st.session_state['selected_project'] = projects[0]

    # 新增/刪除專案展開區
    with st.sidebar.expander("➕ 新增/刪除專案", expanded=False):
        new_col1, new_col2 = st.columns([2,1])
        new_proj = new_col1.text_input("新專案", key="add_input", label_visibility="collapsed", placeholder="名稱")
        if new_col2.button("建立", key="create_btn"):
            if new_proj:
                os.makedirs(f"projects/{new_proj}", exist_ok=True)
                st.session_state['selected_project'] = new_proj # 建立後自動切換到該專案
                st.rerun()
        
        del_proj = st.selectbox("刪除專案", ["請選擇"] + projects, key="del_select")
        if st.button("❌ 確認永久刪除", key="delete_btn", use_container_width=True):
            if del_proj != "請選擇" and del_proj != "預設專案":
                shutil.rmtree(f"projects/{del_proj}")
                # 刪除後回到清單第一個專案
                new_list = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
                st.session_state['selected_project'] = new_list[0] if new_list else "預設專案"
                st.rerun()

    # --- 專案選擇器 ---
    # 透過 index 強制將 UI 對準 Session State 存儲的值
    try:
        current_index = projects.index(st.session_state['selected_project'])
    except ValueError:
        current_index = 0

    curr_proj = st.sidebar.selectbox(
        "當前執行專案", 
        projects, 
        index=current_index,
        key="sidebar_proj_select_widget"
    )
    
    # 當選單手動改變時，同步回 Session State
    st.session_state['selected_project'] = curr_proj

    st.sidebar.divider()

    # --- 功能導覽區塊 ---
    st.sidebar.title("🚀 功能導航")
    
    if 'expanded_states' not in st.session_state:
        st.session_state['expanded_states'] = {"g1": True, "g2": False, "g3": False, "g4": False, "g5": False}

    def get_label(label, key):
        if st.session_state['active_nav'] == key:
            return f"➤ {label}" 
        return f"　 {label}" 

    # 📌 置頂功能
    if st.sidebar.button(get_label("📌 專案便利貼", "nav_memo"), key="nav_memo_btn"):
        navigate_to("pages/1_📌_專案便利貼 - 每日check.py", "nav_memo", None)

    # 1. 專案進度控管
    exp1 = st.sidebar.expander("📅 專案進度控管", expanded=st.session_state['expanded_states']["g1"])
    if exp1.button(get_label("📊 專案進度", "nav_prog"), key="nav_prog_btn"):
        navigate_to("pages/2_📊_專案進度.py", "nav_prog", "g1")

    # 2. 各階段審查項目
    exp5 = st.sidebar.expander("📝 各階段審查項目", expanded=st.session_state['expanded_states']["g5"])
    if exp5.button(get_label("📝 執照前", "n3"), key="n3_btn"): navigate_to("pages/3_📝_執照前.py", "n3", "g5")
    if exp5.button(get_label("📝 執照中", "n4"), key="n4_btn"): navigate_to("pages/4_📝_執照中.py", "n4", "g5")
    if exp5.button(get_label("📝 執照後", "n5"), key="n5_btn"): navigate_to("pages/5_📝_執照後.py", "n5", "g5")
    if exp5.button(get_label("📝 抽查與報備", "n6"), key="n6_btn"): navigate_to("pages/6_📝_抽查與報備.py", "n6", "g5")
    if exp5.button(get_label("📝 申請獎勵-候選 / 標章", "n7"), key="n7_btn"): 
        navigate_to("pages/7_📝_申請獎勵-候選 標章.py", "n7", "g5")

    # 3. 面積法規檢討
    exp2 = st.sidebar.expander("📏 面積法規檢討", expanded=st.session_state['expanded_states']["g2"])
    if exp2.button(get_label("📐 面積表", "n8"), key="n8_btn"): navigate_to("pages/8_📐_面積表.py", "n8", "g2")
    if exp2.button(get_label("🏢 各層面積計算", "n9"), key="n9_btn"): navigate_to("pages/9_🏢_各層面積計算.py", "n9", "g2")
    if exp2.button(get_label("⚖️ 相關法規", "n10"), key="n10_btn"): navigate_to("pages/10_⚖️_相關法規.py", "n10", "g2")

    # 4. 現場影像紀錄
    exp3 = st.sidebar.expander("🖼️ 現場影像紀錄", expanded=st.session_state['expanded_states']["g3"])
    if exp3.button(get_label("🖼️ 基地照片", "n11"), key="n11_btn"): navigate_to("pages/11_🖼️_基地照片.py", "n11", "g3")
    if exp3.button(get_label("📸 施工影像紀錄", "n12"), key="n12_btn"): navigate_to("pages/12_📸_施工影像紀錄.py", "n12", "g3")

    # 5. 資源管理
    exp4 = st.sidebar.expander("📂 資源管理", expanded=st.session_state['expanded_states']["g4"])
    if exp4.button(get_label("📞 聯絡人清單", "n13"), key="n13_btn"): navigate_to("pages/13_📞_聯絡人清單.py", "n13", "g4")

    # 最後返回 Session State 存儲的專案名稱，確保全域統一
    return st.session_state['selected_project']