import streamlit as st
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：子頁面不再執行 st.set_page_config 與 render_sidebar，避免 DuplicateKey 錯誤
from state_manager import init_project_state, PROJECTS_DIR

# --- 核心修正：取得主程式選定的專案 ---
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    # 備援方案：若直接跑此頁面則預設初始化 (開發除錯用)
    _, curr_proj = init_project_state()

# 2. 定義資料路徑 (使用 Path 物件)
# 確保路徑與當前選定的專案同步更新
project_dir = PROJECTS_DIR / curr_proj
photo_dir = project_dir / "photos"

# 確保照片目錄存在
if not photo_dir.exists():
    photo_dir.mkdir(parents=True, exist_ok=True)

# --- 3. UI 介面渲染 ---
st.title("🖼️ 基地照片管理")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 4. 照片上傳功能 ---
st.subheader("📤 上傳新照片")
with st.expander("點擊展開上傳區域", expanded=True):
    up_files = st.file_uploader(
        "選擇照片檔案 (支援 PNG, JPG, JPEG)", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        key=f"uploader_{curr_proj}" # 使用專案名作為 key 避免緩存衝突
    )
    
    if st.button("🚀 開始上傳檔案", use_container_width=True) and up_files:
        success_count = 0
        for f in up_files:
            try:
                # 使用 Path 物件合成路徑並寫入實體檔案
                save_path = photo_dir / f.name
                with open(save_path, "wb") as file:
                    file.write(f.getbuffer())
                success_count += 1
            except Exception as e:
                st.error(f"檔案 {f.name} 上傳失敗: {e}")
        
        if success_count > 0:
            st.success(f"✅ 成功上傳 {success_count} 張照片！")
            st.rerun()

st.divider()

# --- 5. 照片展示與管理區域 ---
st.subheader("📷 基地現況照片庫")

# 取得目錄下所有符合格式的圖片檔案
photos = [f for f in photo_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]

if not photos:
    st.info("💡 目前尚無基地照片，請先從上方上傳。")
else:
    # 使用 3 欄式佈局動態展示
    cols = st.columns(3)
    
    for i, p_path in enumerate(photos):
        with cols[i % 3]:
            with st.container(border=True):
                # 顯示圖片，使用檔案名稱作為標註
                st.image(str(p_path), use_container_width=True, caption=p_path.name)
                
                # 刪除功能：確保 Key 包含檔案名與索引以維持唯一性
                if st.button(f"🗑️ 刪除照片", key=f"del_{p_path.stem}_{i}_{curr_proj}", use_container_width=True):
                    try:
                        p_path.unlink() # 刪除實體檔案
                        st.success(f"已刪除：{p_path.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")

# --- 6. 輔助資訊 ---
# 在側邊欄顯示當前專案的照片儲存路徑，便於管理員核對
st.sidebar.divider()
st.sidebar.write(f"📁 儲存路徑：")
st.sidebar.code(str(photo_dir))