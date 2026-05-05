import streamlit as st
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：子頁面不再執行 st.set_page_config 與 render_sidebar，避免 DuplicateKey 錯誤
from state_manager import init_project_state

# --- 核心修正：取得主程式選定的專案 ---
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    # 備援方案
    _, curr_proj = init_project_state()

# --- 2. UI 介面渲染 ---
st.title("⚖️ 相關法規與查詢連結")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 3. 推薦功能：外部法規連結資料庫 ---
st.subheader("🌐 常用線上法規查詢")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("**📜 營建法規**")
        st.page_link("https://law.moj.gov.tw/", label="全國法規資料庫", icon="🏛️")
        st.page_link("https://www.cpami.gov.tw/", label="內政部國土管理署", icon="🏢")

with col2:
    with st.container(border=True):
        st.markdown("**📍 縣市法規 (台北/新北)**")
        st.page_link("https://www.laws.taipei.gov.tw/", label="台北市法規查詢系統", icon="🏙️")
        st.page_link("https://web.law.ntpc.gov.tw/", label="新北市電子法規查詢", icon="🌆")

with col3:
    with st.container(border=True):
        st.markdown("**🔍 都市計畫與地籍**")
        st.page_link("https://map.tgos.tw/", label="TGOS 地圖服務", icon="🗺️")
        st.page_link("https://easymap.land.moi.gov.tw/", label="地籍圖資網路便民服務", icon="📐")

st.divider()

# --- 4. 推薦功能：專案法規筆記 ---
st.subheader("📝 專案專屬法規備註")

# 狀態管理：使用 curr_proj 作為 key 的一部分，確保各專案備註獨立
memo_key = f"law_memo_{curr_proj}"
if memo_key not in st.session_state:
    st.session_state[memo_key] = ""

law_memo = st.text_area(
    "針對此專案的法規限制或容獎重點紀錄：",
    value=st.session_state[memo_key],
    height=200,
    placeholder="例如：本案適用危老條例第X條、容積移轉上限為30%...",
    key=f"input_{memo_key}"
)

if st.button("💾 儲存法規備註", use_container_width=True):
    st.session_state[memo_key] = law_memo
    st.success(f"✅ {curr_proj} 的法規備註已暫存！")

st.info("💡 提示：此頁面未來可擴充為 PDF 法規手冊上傳區，方便快速查閱。")