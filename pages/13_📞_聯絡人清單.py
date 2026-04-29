import streamlit as st
import pandas as pd
import os
from utils import init_sidebar

# 0. 基礎配置與路徑鎖定
st.set_page_config(layout="wide")
curr_proj = init_sidebar()

# 絕對路徑定位
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
project_dir = os.path.join(root_dir, "projects", curr_proj)
contacts_path = os.path.join(project_dir, "contacts.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

st.title(f"📞 聯絡人清單")

# --- 1. 資料載入函數 (對應新欄位) ---
def load_contacts():
    # 依照您的要求調整後的欄位清單
    cols = ["類別", "公司名稱", "姓名", "連絡電話", "聯絡地址", "Email", "備註"]
    if os.path.exists(contacts_path):
        try:
            df = pd.read_csv(contacts_path, encoding='utf-8-sig').astype(str).replace("nan", "")
            # 自動處理舊資料欄位轉換
            if "電話號碼" in df.columns:
                df = df.rename(columns={"電話號碼": "連絡電話"})
            
            # 確保目前的欄位都存在
            for col in cols:
                if col not in df.columns: df[col] = ""
            return df[cols]
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

contacts_df = load_contacts()

# --- 2. 編輯表單 ---
with st.form("contact_form_final_v2"):
    contact_categories = [
        "業主", "承辦", "建築師", "結構", "機電", 
        "營造", "綠建築", "顧問", "廠商", "測量", 
        "鑽探", "水保", "代書", "其他"
    ]
    
    edited_df = st.data_editor(
        contacts_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_clean_final",
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
    
    submit_button = st.form_submit_button("💾 儲存所有變更", use_container_width=True)

# --- 3. 儲存處理邏輯 ---
if submit_button:
    try:
        final_df = edited_df.copy()
        for col in final_df.columns:
            final_df[col] = final_df[col].astype(str).str.strip().replace("nan", "")
        
        # 寫入實體 CSV
        final_df.to_csv(contacts_path, index=False, encoding='utf-8-sig')
        st.success(f"✅ 聯絡資料已成功更新")
        st.rerun()
    except Exception as e:
        st.error(f"儲存失敗: {e}")