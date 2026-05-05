import streamlit as st
from state_manager import init_project_state
from ui_components import render_sidebar

# 1. 頁面基礎配置 (必須是 Streamlit 指令的第一行)
st.set_page_config(page_title="建築專案管理系統", layout="wide")

# 2. 渲染側邊欄並獲取最新的專案清單
# 我們將渲染與狀態初始化結合，確保 render_sidebar 內部觸發 rerun 後，
# 下一次執行能抓到實體資料夾中最新的專案
all_projects, curr_proj = init_project_state()

# 呼叫側邊欄 (包含切換、新增、刪除邏輯)
# 確保此處回傳的選中項會更新進 session_state
selected_proj = render_sidebar(all_projects, curr_proj)

# 3. 狀態同步：若側邊欄切換了專案，更新全域狀態
if selected_proj != st.session_state.get("global_project_selector"):
    st.session_state.global_project_selector = selected_proj
    st.rerun()

# 4. 定義頁面物件 (嚴格對齊實體資料夾路徑)
# 01_專案進度控管
pg_1 = st.Page("pages/01_專案進度控管/1_專案便利貼-每日check.py", title="專案便利貼", icon="📌")
pg_2 = st.Page("pages/01_專案進度控管/2_專案進度.py", title="專案進度", icon="📊")

# 02_階段審查項目
pg_3 = st.Page("pages/02_階段審查項目/3_執照前.py", title="執照前", icon="📝")
pg_4 = st.Page("pages/02_階段審查項目/4_執照中.py", title="執照中", icon="📝")
pg_5 = st.Page("pages/02_階段審查項目/5_執照後.py", title="執照後", icon="📝")
pg_6 = st.Page("pages/02_階段審查項目/6_抽查與報備.py", title="抽查與報備", icon="📋")
pg_7 = st.Page("pages/02_階段審查項目/7_申請獎勵-候選標章.py", title="申請獎勵-候選標章", icon="📜")

# 03_面積法規檢討
pg_8 = st.Page("pages/03_面積法規檢討/8_面積表.py", title="面積表", icon="📐")
pg_9 = st.Page("pages/03_面積法規檢討/9_各層面積計算.py", title="各層面積計算", icon="🏢")
pg_10 = st.Page("pages/03_面積法規檢討/10_相關法規.py", title="相關法規", icon="⚖️")

# 04_現場影像紀錄
pg_11 = st.Page("pages/04_現場影像紀錄/11_基地照片.py", title="基地照片", icon="🖼️")
pg_12 = st.Page("pages/04_現場影像紀錄/12_施工影像紀錄.py", title="施工影像紀錄", icon="🎥")

# 05_資源管理
pg_13 = st.Page("pages/05_資源管理/13_聯絡人清單.py", title="聯絡人清單", icon="📞")

# 5. 建立二級分組導覽結構
pg = st.navigation({
    "專案進度控管": [pg_1, pg_2],
    "階段審查項目": [pg_3, pg_4, pg_5, pg_6, pg_7],
    "面積法規檢討": [pg_8, pg_9, pg_10],
    "現場影像紀錄": [pg_11, pg_12],
    "資源管理": [pg_13]
})

# 6. 執行導航渲染
pg.run()