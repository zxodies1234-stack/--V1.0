import streamlit as st
import pandas as pd
import plotly.express as px
import time
from pathlib import Path

# --- 1. 匯入新架構模組 ---
# 注意：不需要再匯入 render_sidebar，因為 app.py 已經執行過了
from state_manager import init_project_state, PROJECTS_DIR

# --- 核心修正：移除 st.set_page_config 與重複的 render_sidebar ---

# 1. 取得主程式選定的專案
# 從 session_state 獲取由 app.py 中 render_sidebar 設定的專案名稱
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    # 預防性處理：若 session 中尚未定義則重新初始化一次
    _, curr_proj = init_project_state()

# 2. 定義資料路徑 (使用 Path 物件)
project_dir = PROJECTS_DIR / curr_proj
data_path = project_dir / "progress.csv"

# 確保目錄存在
if not project_dir.exists():
    project_dir.mkdir(parents=True, exist_ok=True)

# --- 2. 核心邏輯：資料載入 ---
def load_saved_data():
    required_cols = ["項目", "狀態", "開始日期", "結束日期", "專案人員", "協力廠商", "備註"]
    
    # 若檔案不存在，初始化預設階段
    if not data_path.exists():
        stages = ["設計初期", "圖面規劃", "圖面檢討", "都審報告書", "執照圖", "施工圖"]
        df = pd.DataFrame(columns=required_cols)
        df["項目"] = stages
        df["狀態"] = "⚪ 未開始"
        df["開始日期"] = pd.Timestamp.now().date()
        df["結束日期"] = (pd.Timestamp.now() + pd.Timedelta(days=30)).date()
        df.to_csv(data_path, index=False, encoding='utf-8-sig')
        return df
    else:
        try:
            df = pd.read_csv(data_path, encoding='utf-8-sig')
            # 兼容舊版欄位名轉換
            rename_map = {"階段": "項目", "預計開始": "開始日期", "預計結束": "結束日期"}
            df = df.rename(columns=rename_map)
            
            # 補齊缺失欄位
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""
            
            # 轉換日期格式
            df["開始日期"] = pd.to_datetime(df["開始日期"], errors='coerce').dt.date
            df["結束日期"] = pd.to_datetime(df["結束日期"], errors='coerce').dt.date
            return df[required_cols]
        except Exception as e:
            st.error(f"讀取進度表失敗: {e}")
            return pd.DataFrame(columns=required_cols)

# 3. 狀態管理：切換專案時重載
if 'stable_df' not in st.session_state or st.session_state.get('last_proj_prog') != curr_proj:
    st.session_state.stable_df = load_saved_data()
    st.session_state.last_proj_prog = curr_proj

# --- 3. UI 介面：任務清單編輯 ---
st.title(f"📊 專案進度管理 - {curr_proj}")
st.subheader("📋 任務清單編輯")

edited_df = st.data_editor(
    st.session_state.stable_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "狀態": st.column_config.SelectboxColumn("狀態", options=["⚪ 未開始", "🔵 進行中", "✅ 已完成", "📂 掛件中", "🚨 作業要徑", "❓ 遇到問題"]),
        "開始日期": st.column_config.DateColumn("開始日期"),
        "結束日期": st.column_config.DateColumn("結束日期"),
    },
    key="main_progress_editor"
)

# 儲存變更按鈕
if st.button("💾 儲存變更", use_container_width=True):
    # 移除空項目
    final_df = edited_df[edited_df["項目"].fillna("").str.strip() != ""].copy()
    
    # 確保存檔日期格式正確
    final_df["開始日期"] = pd.to_datetime(final_df["開始日期"]).dt.date
    final_df["結束日期"] = pd.to_datetime(final_df["結束日期"]).dt.date
    
    # 更新 Session 並存檔
    st.session_state.stable_df = final_df
    final_df.to_csv(data_path, index=False, encoding='utf-8-sig')
    st.success("✅ 進度資料已成功儲存")
    time.sleep(0.5)
    st.rerun()

st.divider()

# --- 4. 甘特圖渲染區域 ---
st.subheader("📅 工程進度時間軸")

plot_list = []
# 使用 edited_df 以保持預覽即時性
raw_records = edited_df.to_dict('records')
display_order = []

# 構建 Plotly 繪圖數據
for idx, row in enumerate(raw_records):
    p_name_raw = str(row.get("項目", "")).strip()
    if p_name_raw and row.get("開始日期") and row.get("結束日期"):
        # 防止相同名稱重疊
        unique_id = f"{p_name_raw} " + ("\u200b" * idx) 
        
        s_date = pd.to_datetime(row["開始日期"])
        e_date = pd.to_datetime(row["結束日期"])
        
        if e_date >= s_date:
            plot_list.append({
                "顯示名稱": p_name_raw,
                "繪圖座標": unique_id,
                "狀態": str(row.get("狀態", "⚪ 未開始")),
                "開始日期": s_date,
                "結束日期": e_date
            })
            display_order.append(unique_id)

plot_df = pd.DataFrame(plot_list)

if not plot_df.empty:
    fig = px.timeline(
        plot_df, 
        x_start="開始日期", 
        x_end="結束日期", 
        y="繪圖座標",
        color="狀態",
        category_orders={"繪圖座標": display_order},
        color_discrete_map={
            "🚨 作業要徑": "#FF4B4B", "🔵 進行中": "#0068C9", "✅ 已完成": "#29B09D",
            "📂 掛件中": "#FFD166", "❓ 遇到問題": "#E01E1E", "⚪ 未開始": "#BFBFBF"
        }
    )
    
    fig.update_yaxes(autorange="reversed", showticklabels=False, title="")
    
    anns = []
    for i, row in plot_df.iterrows():
        try:
            target_y = row['繪圖座標']
            disp_name = row['顯示名稱']
            s, e = row['開始日期'], row['結束日期']
            
            anns.append(dict(x=s, y=target_y, text=f"{s.strftime('%m/%d')}", showarrow=False, xanchor='right', xshift=-5, font=dict(size=10, color="#666")))
            anns.append(dict(x=e, y=target_y, text=f"{e.strftime('%m/%d')}", showarrow=False, xanchor='left', xshift=5, font=dict(size=10, color="#666")))
            anns.append(dict(x=s, y=target_y, text=f" <b>{disp_name}</b>", showarrow=False, xanchor='left', xshift=8, font=dict(size=12, color="white")))
        except: continue

    fig.update_layout(
        annotations=anns, 
        height=max(400, len(plot_df) * 60), 
        xaxis=dict(side="top", title="", tickformat="%m/%d"),
        margin=dict(l=10, r=80, t=80, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"gantt_{curr_proj}_{len(plot_df)}")
else:
    st.info("💡 目前尚無有效的任務進度數據，請在上方表格填寫項目與日期。")