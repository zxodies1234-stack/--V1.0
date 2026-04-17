import streamlit as st
import pandas as pd
import os
import plotly.express as px
from utils import init_sidebar

# 0. 寬螢幕設定
st.set_page_config(layout="wide")

# 1. 初始化環境
curr_proj = init_sidebar()
project_dir = f"projects/{curr_proj}"
data_path = os.path.join(project_dir, "progress.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir)

st.title(f"📊 專案進度管理")

# --- 2. 核心邏輯：資料載入 (含舊欄位自動相容) ---
def load_saved_data():
    required_cols = ["項目", "狀態", "開始日期", "結束日期", "專案人員", "協力廠商", "備註"]
    if not os.path.exists(data_path):
        stages = ["設計初期", "圖面規劃", "圖面檢討", "都審報告書", "執照圖", "施工圖"]
        df = pd.DataFrame(columns=required_cols)
        df["項目"] = stages
        df["狀態"] = "⚪ 未開始"
        df["開始日期"] = pd.Timestamp.now().date()
        df["結束日期"] = (pd.Timestamp.now() + pd.Timedelta(days=30)).date()
        df.to_csv(data_path, index=False)
        return df
    else:
        df = pd.read_csv(data_path)
        rename_map = {"階段": "項目", "預計開始": "開始日期", "預計結束": "結束日期"}
        df = df.rename(columns=rename_map)
        for col in required_cols:
            if col not in df.columns: df[col] = ""
        df["開始日期"] = pd.to_datetime(df["開始日期"], errors='coerce').dt.date
        df["結束日期"] = pd.to_datetime(df["結束日期"], errors='coerce').dt.date
        return df[required_cols]

# 穩定緩衝機制
if 'stable_df' not in st.session_state or st.session_state.get('last_proj') != curr_proj:
    st.session_state.stable_df = load_saved_data()
    st.session_state.last_proj = curr_proj

# --- 3. 上方表格區 (專注編輯) ---
st.subheader("📋 任務清單編輯")

display_df = st.session_state.stable_df.copy()
display_df["🗑️"] = False

edited_data = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "狀態": st.column_config.SelectboxColumn("狀態", options=["⚪ 未開始", "🔵 進行中", "✅ 已完成", "📂 掛件中", "🚨 作業要徑", "❓ 遇到問題"]),
        "開始日期": st.column_config.DateColumn("開始日期"),
        "結束日期": st.column_config.DateColumn("結束日期"),
        "🗑️": st.column_config.CheckboxColumn("🗑️", width="small")
    },
    key="editor_v_final"
)

# 修改處：按鈕文字變更為 "💾 儲存變更"
if st.button("💾 儲存變更", use_container_width=True):
    final_df = edited_data[edited_data["🗑️"] == False].copy()
    final_df = final_df.drop(columns=["🗑️"])
    final_df = final_df[final_df["項目"].fillna("").str.strip() != ""]
    final_df.to_csv(data_path, index=False)
    st.session_state.stable_df = final_df
    st.success("✅ 資料已成功鎖定儲存！")
    st.rerun()

st.divider()

# --- 4. 下方甘特圖區 (修正對齊版) ---
st.subheader("📅 工程進度時間軸")

if st.button("🔄 更新甘特圖"):
    plot_df = st.session_state.stable_df.copy()
    plot_df = plot_df.dropna(subset=["開始日期", "結束日期"])
    plot_df = plot_df[plot_df["項目"].fillna("").str.strip() != ""]

    if not plot_df.empty:
        current_order = plot_df["項目"].tolist()
        plot_df_rev = plot_df.iloc[::-1].reset_index(drop=True)

        fig = px.timeline(
            plot_df_rev, x_start="開始日期", x_end="結束日期", y="項目", color="狀態",
            category_orders={"項目": current_order},
            color_discrete_map={
                "🚨 作業要徑": "#FF4B4B", "🔵 進行中": "#0068C9", "✅ 已完成": "#29B09D",
                "📂 掛件中": "#FFD166", "❓ 遇到問題": "#E01E1E", "⚪ 未開始": "#BFBFBF"
            },
            hover_data=["專案人員", "協力廠商"]
        )
        fig.update_yaxes(showticklabels=False, title="")
        
        anns = []
        for i, row in plot_df_rev.iterrows():
            try:
                s, e = row['開始日期'], row['結束日期']
                s_str = s.strftime('%m/%d').lstrip('0').replace('/0', '/')
                e_str = e.strftime('%m/%d').lstrip('0').replace('/0', '/')
                anns.append(dict(x=s, y=row['項目'], text=s_str, showarrow=False, xanchor='right', xshift=-8, font=dict(size=10)))
                anns.append(dict(x=e, y=row['項目'], text=e_str, showarrow=False, xanchor='left', xshift=8, font=dict(size=10)))
                anns.append(dict(x=s, y=row['項目'], text=f"<b>{row['項目']}</b>", showarrow=False, xanchor='left', xshift=5, font=dict(color="white")))
            except: continue

        fig.update_layout(
            annotations=anns, 
            height=450, 
            xaxis=dict(
                side="top", 
                title="",
                tickformat="%Y-%m",      # 顯示 年-月
                dtick="M1",              # 每月一個刻度
                ticklabelmode="instant", # 標籤對齊刻度線
                gridcolor="rgba(200, 200, 200, 0.3)" # 輔助線
            ),
            margin=dict(l=50, r=80, t=100, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("請先填寫數據並儲存。")