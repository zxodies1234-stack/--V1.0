import streamlit as st
import pandas as pd
import os
from utils import init_sidebar

# 0. 配置與初始化
st.set_page_config(layout="wide")
curr_proj = init_sidebar()
project_dir = f"projects/{curr_proj}"
data_path = os.path.join(project_dir, "area_data.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir)

st.title(f"🏢 各層面積計算")
st.caption(f"當前專案：{curr_proj}")

# --- 1. 核心邏輯：資料載入 (具備自動修復欄位功能) ---
def load_area_data():
    # 定義標準欄位
    required_cols = ["樓層", "用途", "屬性", "專有面積(㎡)", "共用面積(㎡)", "小計(㎡)", "坪數", "備註"]
    
    if not os.path.exists(data_path):
        df = pd.DataFrame(columns=required_cols)
        df.to_csv(data_path, index=False)
        return df
    
    try:
        df = pd.read_csv(data_path)
        
        # 【核心修正】：檢查並補齊缺失欄位，避免 KeyError
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0.0 if "面積" in col or "坪數" in col or "小計" in col else ""
        
        # 強制轉型文字欄位
        for tc in ["樓層", "用途", "屬性", "備註"]:
            df[tc] = df[tc].astype(str).replace("nan", "")
            
        # 確保「屬性」有預設值
        df["屬性"] = df["屬性"].replace("", "計入容積")
        
        return df[required_cols]
    except Exception as e:
        st.error(f"資料讀取失敗，已重置表格。錯誤內容: {e}")
        return pd.DataFrame(columns=required_cols)

# 使用緩存確保狀態穩定
if 'area_df_v3' not in st.session_state or st.session_state.get('area_last_proj_3') != curr_proj:
    st.session_state.area_df_v3 = load_area_data()
    st.session_state.area_last_proj_3 = curr_proj

# --- 2. 編輯表格 ---
st.subheader("📋 樓層面積詳細明細")
display_df = st.session_state.area_df_v3.copy()
display_df["🗑️"] = False # 增加刪除用勾選框

edited_df = st.data_editor(
    display_df, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "屬性": st.column_config.SelectboxColumn("屬性", options=["計入容積", "免計項目", "不計入建築面積"], width="small"),
        "專有面積(㎡)": st.column_config.NumberColumn("專有(㎡)", format="%.2f", width="small"),
        "共用面積(㎡)": st.column_config.NumberColumn("共用(㎡)", format="%.2f", width="small"),
        "小計(㎡)": st.column_config.NumberColumn("小計(㎡)", format="%.2f", disabled=True, width="small"),
        "坪數": st.column_config.NumberColumn("坪數", format="%.2f", disabled=True, width="small"),
        "備註": st.column_config.TextColumn("備註", width="medium"),
        "🗑️": st.column_config.CheckboxColumn("刪除", width="small")
    }, 
    key="area_editor_v3_core"
)

# --- 3. 儲存邏輯 ---
if st.button("💾 儲存變更", key="save_area_v3", use_container_width=True):
    # 移除勾選刪除的列
    final_df = edited_df[edited_df["🗑️"] == False].copy().drop(columns=["🗑️"])
    
    # 數值計算
    for col in ["專有面積(㎡)", "共用面積(㎡)"]:
        final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0)
    
    final_df["小計(㎡)"] = final_df["專有面積(㎡)"] + final_df["共用面積(㎡)"]
    final_df["坪數"] = final_df["小計(㎡)"] * 0.3025
    
    # 寫入檔案與更新 Session
    final_df.to_csv(data_path, index=False)
    st.session_state.area_df_v3 = final_df
    st.success("✅ 各層面積已成功儲存並重新計算！")
    st.rerun()

# --- 4. 即時統計統計 ---
st.divider()
if not st.session_state.area_df_v3.empty:
    total_floor_area = st.session_state.area_df_v3[st.session_state.area_df_v3["屬性"] == "計入容積"]["小計(㎡)"].sum()
    st.info(f"💡 目前「計入容積」總面積為：**{total_floor_area:.2f} ㎡**")