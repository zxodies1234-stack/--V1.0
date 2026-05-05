import streamlit as st
import pandas as pd
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

# 2. 定義資料路徑 (使用新架構的 PROJECTS_DIR)
# 確保路徑與當前選定的專案同步更新
project_dir = PROJECTS_DIR / curr_proj
contacts_path = project_dir / "contacts.csv"

# 確保專案目錄存在
if not project_dir.exists():
    project_dir.mkdir(parents=True, exist_ok=True)

# --- 3. 資料載入函數 ---
def load_contacts():
    # 標準欄位定義
    cols = ["類別", "公司名稱", "姓名", "連絡電話", "聯絡地址", "Email", "備註"]
    
    if contacts_path.exists():
        try:
            # 讀取並處理空值
            df = pd.read_csv(contacts_path, encoding='utf-8-sig').astype(str).replace("nan", "")
            
            # 自動處理舊資料欄位名稱相容性
            if "電話號碼" in df.columns:
                df = df.rename(columns={"電話號碼": "連絡電話"})
            
            # 檢查並補齊缺失欄位
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
            
            return df[cols]
        except Exception as e:
            st.error(f"讀取聯絡人失敗: {e}")
            return pd.DataFrame(columns=cols)
    else:
        # 若檔案不存在，回傳空表格
        return pd.DataFrame(columns=cols)

# 載入資料
contacts_df = load_contacts()

# --- 4. UI 介面渲染 ---
st.title(f"📞 聯絡人清單")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# 編輯表單
with st.form("contact_form_v3"):
    # 定義類別選單
    contact_categories = [
        "業主", "承辦", "建築師", "結構", "機電", 
        "營造", "綠建築", "顧問", "廠商", "測量", 
        "鑽探", "水保", "代書", "其他"
    ]
    
    # 核心編輯器
    edited_df = st.data_editor(
        contacts_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=f"contacts_editor_{curr_proj}", # 綁定專案名稱確保唯一性，防止不同專案間切換錯誤
        column_config={
            "類別": st.column_config.SelectboxColumn("類別", options=contact_categories, required=True),
            "公司名稱": st.column_config.TextColumn("公司名稱", width="medium"),
            "姓名": st.column_config.TextColumn("姓名", width="small"),
            "連絡電話": st.column_config.TextColumn("連絡電話", width="medium"),
            "聯絡地址": st.column_config.TextColumn("聯絡地址", width="large"),
            "Email": st.column_config.TextColumn("Email", width="medium"),
            "備註": st.column_config.TextColumn("備註", width="medium"),
        }
    )
    
    submit_button = st.form_submit_button("💾 儲存所有聯絡變更", use_container_width=True)

# --- 5. 儲存處理邏輯 ---
if submit_button:
    try:
        # 資料清理
        final_df = edited_df.copy()
        for col in final_df.columns:
            final_df[col] = final_df[col].astype(str).str.strip().replace("nan", "")
        
        # 寫入實體 CSV (包含 BOM 以確保 Excel 相容性)
        final_df.to_csv(contacts_path, index=False, encoding='utf-8-sig')
        st.success(f"✅ {curr_proj} 的聯絡資料已成功更新！")
        st.rerun()
    except Exception as e:
        st.error(f"儲存失敗: {e}")

# --- 6. 輔助資訊 ---
if not contacts_df.empty:
    st.info(f"💡 目前共有 {len(contacts_df)} 位聯絡人。您可以直接在表格中點擊「新增行」或「刪除」。")