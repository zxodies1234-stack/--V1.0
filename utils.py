import streamlit as st
import os
import shutil

def init_sidebar():
    # --- 💉 核心 CSS 改寫：增加「微按鈕」實體感 ---
    st.markdown("""
        <style>
            /* 1. 徹底隱藏重複的原生導航 */
            [data-testid="stSidebarNav"] { display: none !important; }

            /* 2. 為導航按鈕增加「微實體感」 */
            [data-testid="stSidebar"] .stButton button {
                background-color: #f8f9fb !important; /* 極淺灰底，營造塊狀感 */
                border: 1px solid #ebedf0 !important; /* 極淡邊框，界定邊界 */
                box-shadow: 0px 1px 1px rgba(0,0,0,0.02) !important; /* 微乎其微的陰影 */
                color: #31333F !important;
                font-weight: 400 !important;
                font-size: 14px !important;
                text-align: left !important;
                justify-content: flex-start !important;
                display: flex !important;
                width: 100% !important;
                padding: 6px 12px !important;
                min-height: 35px !important;
                border-radius: 6px !important; /* 稍微圓潤一點更有現代感 */
                margin-bottom: 2px !important;
                transition: all 0.2s ease !important;
            }

            /* 3. 懸停效果：強化「被按下」的感覺 */
            [data-testid="stSidebar"] .stButton button:hover {
                background-color: #ffffff !important; /* 懸停時變亮 */
                border-color: #ff4b4b !important; /* 邊框變色 */
                box-shadow: 0px 2px 4px rgba(0,0,0,0.05) !important;
                transform: translateY(-1px) !important; /* 微幅上浮 */
            }

            /* 4. 下拉選單 Expander 的微調 */
            [data-testid="stSidebar"] [data-testid="stExpander"] {
                border: 1px solid #f0f2f6 !important;
                border-radius: 8px !important;
                background-color: #ffffff !important;
                margin-bottom: 5px !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] p {
                font-weight: 500 !important; /* 標題稍微厚一點點以利區分 */
                font-size: 14px !important;
            }
            
            /* 縮減內部垂直間距 */
            [data-testid="stSidebar"] .st-emotion-cache-16idsys {
                gap: 0.3rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 🏢 專案管理區塊 ---
    st.sidebar.title("🏢 專案管理")
    if not os.path.exists("projects"): os.makedirs("projects")

    with st.sidebar.expander("➕ 新增/刪除專案", expanded=False):
        new_proj = st.text_input("新專案名稱", key="add_proj_input")
        if st.button("建立專案", key="create_btn", use_container_width=True):
            if new_proj:
                os.makedirs(f"projects/{new_proj}", exist_ok=True); st.rerun()
        st.divider()
        projects = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
        del_proj = st.selectbox("選擇刪除專案", ["請選擇"] + projects, key="del_select")
        if st.button("❌ 永久刪除", key="delete_btn", use_container_width=True):
            if del_proj != "請選擇":
                shutil.rmtree(f"projects/{del_proj}"); st.rerun()

    projects = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
    curr_proj = st.sidebar.selectbox("選擇目前執行專案", projects if projects else ["預設專案"], key="sidebar_proj_select")
    st.sidebar.divider()

    # --- 🚀 功能導航區塊 ---
    st.sidebar.title("🚀 功能導航")

    if 'expanded_states' not in st.session_state:
        st.session_state['expanded_states'] = {"g1": True, "g2": False, "g3": False, "g4": False, "g5": False}

    def set_only(target):
        for key in st.session_state['expanded_states']:
            st.session_state['expanded_states'][key] = (key == target)

    # 📌 置頂功能
    if st.sidebar.button("📌 專案便利貼 - 每日check", key="nav_memo"):
        set_only(None); st.switch_page("pages/1_📌_專案便利貼 - 每日check.py")

    # 1. 專案進度控管
    exp1 = st.sidebar.expander("📅 專案進度控管", expanded=st.session_state['expanded_states']["g1"])
    if exp1.button("📊 專案進度", key="nav_prog"):
        set_only("g1"); st.switch_page("pages/2_📊_專案進度.py")

    # 2. 各階段審查項目
    exp5 = st.sidebar.expander("📝 各階段審查項目", expanded=st.session_state['expanded_states']["g5"])
    if exp5.button("📝 執照前", key="n3"): set_only("g5"); st.switch_page("pages/3_📝_執照前.py")
    if exp5.button("📝 執照中", key="n4"): set_only("g5"); st.switch_page("pages/4_📝_執照中.py")
    if exp5.button("📝 執照後", key="n5"): set_only("g5"); st.switch_page("pages/5_📝_執照後.py")
    if exp5.button("📝 抽查與報備", key="n6"): set_only("g5"); st.switch_page("pages/6_📝_抽查與報備.py")
    if exp5.button("📝 審查項目", key="n7"): set_only("g5"); st.switch_page("pages/7_📝_審查項目.py")

    # 3. 面積法規檢討
    exp2 = st.sidebar.expander("📏 面積法規檢討", expanded=st.session_state['expanded_states']["g2"])
    if exp2.button("📐 面積表", key="n8"): set_only("g2"); st.switch_page("pages/8_📐_面積表.py")
    if exp2.button("🏢 各層面積計算", key="n9"): set_only("g2"); st.switch_page("pages/9_🏢_各層面積計算.py")
    if exp2.button("⚖️ 相關法規", key="n10"): set_only("g2"); st.switch_page("pages/10_⚖️_相關法規.py")

    # 4. 現場影像紀錄
    exp3 = st.sidebar.expander("🖼️ 現場影像紀錄", expanded=st.session_state['expanded_states']["g3"])
    if exp3.button("🖼️ 基地照片", key="n11"): set_only("g3"); st.switch_page("pages/11_🖼️_基地照片.py")
    if exp3.button("📸 施工影像紀錄", key="n12"): set_only("g3"); st.switch_page("pages/12_📸_施工影像紀錄.py")

    # 5. 資源管理
    exp4 = st.sidebar.expander("📂 資源管理", expanded=st.session_state['expanded_states']["g4"])
    if exp4.button("📞 聯絡人清單", key="n13"): set_only("g4"); st.switch_page("pages/13_📞_聯絡人清單.py")

    return curr_proj