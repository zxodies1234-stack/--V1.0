import streamlit as st
import pandas as pd
import os
import re
from utils import init_sidebar

# 0. 寬螢幕設定
st.set_page_config(layout="wide")

# 1. 初始化環境
curr_proj = init_sidebar()
project_dir = f"projects/{curr_proj}"
base_info_path = os.path.join(project_dir, "base_info.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir)

st.title(f"📐 建築面積計算表")
st.caption(f"當前專案：{curr_proj}")

# --- 2. 核心邏輯：資料載入 (升級為全行備註儲存模式) ---
def load_base_info():
    # 規範項目清單
    target_rule_cols = ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)", "開挖率(%)", "開挖面積(㎡)"]
    # 基礎欄位
    base_cols = ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]
    # 動態生成備註欄位名稱，例如：建蔽率(%)_備註
    note_cols = [f"{col}_備註" for col in target_rule_cols]
    
    all_cols = base_cols + target_rule_cols + note_cols

    if not os.path.exists(base_info_path):
        # 初始化兩行 (Index 0: 法定, Index 1: 實設)
        df = pd.DataFrame([[""] * len(all_cols), [""] * len(all_cols)], columns=all_cols)
        df.to_csv(base_info_path, index=False)
        return df
    else:
        df = pd.read_csv(base_info_path)
        # 自動補齊新增加的備註欄位
        for col in all_cols:
            if col not in df.columns:
                df[col] = ""
            else:
                df[col] = df[col].astype(str).replace("nan", "")
        return df[all_cols]

if 'base_info_df' not in st.session_state or st.session_state.get('area_last_proj_2') != curr_proj:
    st.session_state.base_info_df = load_base_info()
    st.session_state.area_last_proj_2 = curr_proj

raw_df = st.session_state.base_info_df.copy()

# 轉置輔助函數
def get_vertical_df(df, columns, row_idx=0):
    v_df = df[columns].iloc[[row_idx]].T.reset_index()
    v_df.columns = ["參數項目", "內容值"]
    v_df["內容值"] = v_df["內容值"].astype(str).replace("nan", "")
    return v_df

# --- 3. 表格 1：基地基本資料 ---
st.subheader("📑 1. 基地基本資料")
v_base = get_vertical_df(raw_df, ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"], 0)

e_base = st.data_editor(
    v_base, use_container_width=True, hide_index=True, key="v_be_1",
    column_config={
        "參數項目": st.column_config.TextColumn("📋 項目", disabled=True, width=150),
        "內容值": st.column_config.TextColumn("✏️ 填寫內容", width=600)
    }
)

if st.button("💾 儲存變更", key="save_base", use_container_width=True):
    current_df = st.session_state.base_info_df.copy()
    new_vals = e_base["內容值"].tolist()
    target_cols = ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]
    current_df.loc[0, target_cols] = new_vals
    current_df.loc[1, target_cols] = new_vals
    
    current_df.to_csv(base_info_path, index=False)
    st.session_state.base_info_df = current_df
    st.success("✅ 基本資料已更新！")
    st.rerun()

st.divider()

# --- 4. 表格 2：建蔽率、容積率、開挖率 (全功能備註版) ---
st.subheader("📊 2. 建蔽率、容積率、開挖率")

def get_full_compare_df(df, columns):
    v1 = df[columns].iloc[[0]].T
    v2 = df[columns].iloc[[1]].T
    
    # 提取每一行對應的備註 (從法定行 Index 0 提取備註)
    notes = [df[f"{col}_備註"].iloc[0] for col in columns]
    
    res = pd.concat([v1, v2], axis=1).reset_index()
    res.columns = ["項目", "⚖️ 法定規範", "🏗️ 實設數值"]
    
    def calc_review(row):
        try:
            f_legal = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(row["⚖️ 法定規範"]))[0])
            f_actual = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(row["🏗️ 實設數值"]))[0])
            diff = f_legal - f_actual
            unit = "%" if "%" in row["項目"] else "㎡"
            if diff > 0: return f"剩餘 {diff:.2f} {unit}"
            elif diff == 0: return "剛好滿額"
            else: return "❌ 超過法定數值"
        except:
            return ""

    res["🔍 檢討"] = res.apply(calc_review, axis=1)
    res["📝 備註"] = notes # 帶入每一行獨立的備註
    return res[["項目", "⚖️ 法定規範", "🏗️ 實設數值", "🔍 檢討", "📝 備註"]]

target_rule_cols = ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)", "開挖率(%)", "開挖面積(㎡)"]
v_compare = get_full_compare_df(raw_df, target_rule_cols)

e_compare = st.data_editor(
    v_compare, use_container_width=True, hide_index=True, key="v_be_2",
    column_config={
        "項目": st.column_config.TextColumn("項目", disabled=True, width=180),
        "⚖️ 法定規範": st.column_config.TextColumn("⚖️ 法定規範", width=120),
        "🏗️ 實設數值": st.column_config.TextColumn("🏗️ 實設數值", width=120),
        "🔍 檢討": st.column_config.TextColumn("🔍 檢討", disabled=True, width=150),
        "📝 備註": st.column_config.TextColumn("📝 備註", width=300) # 改名並開啟全行編輯
    }
)

if st.button("💾 儲存變更", key="save_rules", use_container_width=True):
    current_df = st.session_state.base_info_df.copy()
    
    # 更新數值
    current_df.loc[0, target_rule_cols] = e_compare["⚖️ 法定規範"].tolist()
    current_df.loc[1, target_rule_cols] = e_compare["🏗️ 實設數值"].tolist()
    
    # 更新每一行獨立的備註
    new_notes = e_compare["📝 備註"].tolist()
    for i, col in enumerate(target_rule_cols):
        current_df.loc[0, f"{col}_備註"] = new_notes[i]
        current_df.loc[1, f"{col}_備註"] = new_notes[i] # 法定與實設行同步備註
    
    current_df.to_csv(base_info_path, index=False)
    st.session_state.base_info_df = current_df
    st.success("✅ 數據與各行備註已更新！")
    st.rerun()