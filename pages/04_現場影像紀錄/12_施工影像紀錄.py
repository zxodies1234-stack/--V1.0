import streamlit as st
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：子頁面不再執行 st.set_page_config 與 render_sidebar，避免 DuplicateKey 錯誤
from state_manager import init_project_state, PROJECTS_DIR

# --- 核心修正：取得主程式選定的專案 ---
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    # 備援方案：若直接跑此頁面則預設初始化
    _, curr_proj = init_project_state()

# 2. 定義資料路徑 (使用 Path 物件)
# 建議將施工紀錄與基地照片分開存放在 construction_photos 子目錄下
project_dir = PROJECTS_DIR / curr_proj
img_dir = project_dir / "construction_photos"

# 確保目錄存在
if not img_dir.exists():
    img_dir.mkdir(parents=True, exist_ok=True)

# --- 3. UI 介面渲染 ---
st.title("📸 施工影像紀錄")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 4. 上傳功能 ---
with st.container(border=True):
    st.subheader("📤 上傳工地現場影像")
    uploaded_files = st.file_uploader(
        "選擇工地照片 (支援 JPG, PNG, JPEG)", 
        type=["jpg", "png", "jpeg"], 
        accept_multiple_files=True,
        key=f"const_uploader_{curr_proj}" # 使用專案名稱作為 key 避免衝突
    )
    
    if st.button("🚀 開始上傳檔案", use_container_width=True) and uploaded_files:
        success_count = 0
        for f in uploaded_files:
            try:
                save_path = img_dir / f.name
                with open(save_path, "wb") as file:
                    file.write(f.getbuffer())
                success_count += 1
            except Exception as e:
                st.error(f"檔案 {f.name} 上傳失敗: {e}")
        
        if success_count > 0:
            st.success(f"✅ 已成功儲存 {success_count} 張施工紀錄照片。")
            st.rerun()

# --- 5. 展示相簿 ---
st.divider()
st.subheader("📅 影像紀錄庫")

# 取得所有圖片檔案並按修改時間排序 (最新的在前面)
files = sorted(
    [f for f in img_dir.iterdir() if f.suffix.lower() in [".jpg", ".png", ".jpeg"]],
    key=lambda x: x.stat().st_mtime,
    reverse=True
)

if files:
    # 採用 4 欄式佈局增加檢視效率
    cols = st.columns(4)
    for idx, f_path in enumerate(files):
        with cols[idx % 4]:
            with st.container(border=True):
                st.image(str(f_path), caption=f_path.name, use_container_width=True)
                
                # 刪除功能：加入專案名稱與索引確保 Key 唯一
                if st.button("🗑️ 刪除", key=f"del_const_{f_path.stem}_{idx}_{curr_proj}", use_container_width=True):
                    try:
                        f_path.unlink()
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")
else:
    st.info("💡 目前尚無施工照片，請由上方區域上傳檔案。")

# --- 6. 輔助工具 ---
# 在側邊欄顯示當前專案的影像總數
st.sidebar.divider()
st.sidebar.write(f"📊 目前影像總數：{len(files)}")