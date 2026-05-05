import streamlit as st
import pandas as pd
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：子頁面不再重複執行配置與側邊欄渲染，避免 DuplicateKey 錯誤
from state_manager import init_project_state, PROJECTS_DIR

# --- 核心修正：取得主程式選定的專案 ---
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    # 備援方案：若 session 中尚未定義則重新初始化一次
    _, curr_proj = init_project_state()

# 2. 定義資料路徑 (使用 Path 物件)
project_dir = PROJECTS_DIR / curr_proj
data_path = project_dir / "area_data.csv"

# 確保目錄存在
if not project_dir.exists():
    project_dir.mkdir(parents=True, exist_ok=True)

# --- 3. 核心邏輯：資料載入 (具備自動修復欄位功能) ---
def load_area_data():
    # 定義標準欄位
    required_cols = ["樓層", "用途", "屬性", "專有面積(㎡)", "共用面積(㎡)", "小計(㎡)", "坪數", "備註"]
    
    if not data_path.exists():
        df = pd.DataFrame(columns=required_cols)
        # 初始化一行空資料供用戶填寫
        df.loc[0] = ["1F", "住宅", "計入容積", 0.0, 0.0, 0.0, 0.0, ""]
        df.to_csv(data_path, index=False, encoding='utf-8-sig')
        return df
    
    try:
        df = pd.read_csv(data_path, encoding='utf-8-sig')
        
        # 檢查並補齊缺失欄位
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0.0 if any(k in col for k in ["面積", "坪數", "小計"]) else ""
        
        # 強制轉型文字欄位，處理 NaN
        for tc in ["樓層", "用途", "屬性", "備註"]:
            df[tc] = df[tc].astype(str).replace("nan", "")
            
        # 確保「屬性」有預設值
        df["屬性"] = df["屬性"].replace("", "計入容積")
        
        return df[required_cols]
    except Exception as e:
        st.error(f"資料讀取失敗，已建立空表格。錯誤內容: {e}")
        return pd.DataFrame(columns=required_cols)

# 4. 狀態管理：確保切換專案時強制刷新數據
if 'area_df_v3' not in st.session_state or st.session_state.get('area_last_proj_v3') != curr_proj:
    st.session_state.area_df_v3 = load_area_data()
    st.session_state.area_last_proj_v3 = curr_proj

# --- 5. UI 介面：編輯表格 ---
st.title(f"🏢 各層面積計算")
st.caption(f"當前專案：{curr_proj}")
st.subheader("📋 樓層面積詳細明細")

# 準備顯示用的 DataFrame (增加刪除勾選框)
display_df = st.session_state.area_df_v3.copy()
display_df["🗑️"] = False 

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
    key=f"area_editor_{curr_proj}"
)

# --- 6. 儲存與計算邏輯 ---
if st.button("💾 儲存變更並重新計算", key="save_area_v3", use_container_width=True):
    # 1. 移除勾選刪除的列
    final_df = edited_df[edited_df["🗑️"] == False].copy().drop(columns=["🗑️"])
    
    # 2. 數值強制轉換與計算
    for col in ["專有面積(㎡)", "共用面積(㎡)"]:
        final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0)
    
    final_df["小計(㎡)"] = final_df["專有面積(㎡)"] + final_df["共用面積(㎡)"]
    final_df["坪數"] = final_df["小計(㎡)"] * 0.3025
    
    # 3. 寫入檔案與更新 Session
    final_df.to_csv(data_path, index=False, encoding='utf-8-sig')
    st.session_state.area_df_v3 = final_df
    st.success("✅ 各層面積已成功儲存！所有面積與坪數已更新完成。")
    st.rerun()

# --- 7. 即時統計統計區 ---
st.divider()
if not st.session_state.area_df_v3.empty:
    # 統計「計入容積」總面積
    total_floor_area = st.session_state.area_df_v3[
        st.session_state.area_df_v3["屬性"] == "計入容積"
    ]["小計(㎡)"].sum()
    
    # 統計「總坪數」
    total_pings = st.session_state.area_df_v3["坪數"].sum()
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"💡 目前「計入容積」總面積為：**{total_floor_area:.2f} ㎡**")
    with c2:
        st.info(f"💡 本案總坪數合計約：**{total_pings:.2f} 坪**")