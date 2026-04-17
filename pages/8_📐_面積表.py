import streamlit as st
import pandas as pd
import os
import re
from utils import init_sidebar

# 0. 配置與初始化
st.set_page_config(layout="wide")
curr_proj = init_sidebar()
project_dir = f"projects/{curr_proj}"
base_info_path = os.path.join(project_dir, "base_info.csv")

# 1. 核心邏輯：資料載入
def load_base_info():
    rule_cols_2 = ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)", "開挖率(%)", "開挖面積(㎡)"]
    rule_cols_3 = ["法定容積(㎡)", "都更獎勵容積(㎡)", "容積移轉(㎡)", "允建容積(㎡)"]
    
    target_rule_cols = rule_cols_2 + rule_cols_3
    base_cols = ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]
    note_cols = [f"{col}_備註" for col in target_rule_cols]
    all_cols = base_cols + target_rule_cols + note_cols

    if not os.path.exists(base_info_path):
        df = pd.DataFrame([[""] * len(all_cols), [""] * len(all_cols)], columns=all_cols)
        df.to_csv(base_info_path, index=False)
        return df
    
    df = pd.read_csv(base_info_path)
    for col in all_cols:
        if col not in df.columns: df[col] = ""
        else: df[col] = df[col].astype(str).replace("nan", "")
    return df[all_cols]

if 'base_info_df' not in st.session_state or st.session_state.get('area_last_proj_3_main') != curr_proj:
    st.session_state.base_info_df = load_base_info()
    st.session_state.area_last_proj_3_main = curr_proj

raw_df = st.session_state.base_info_df.copy()

st.title(f"📐 面積表")
st.caption(f"專案：{curr_proj}")

# --- 表格 1：基地基本資料 ---
st.subheader("📑 1. 基地基本資料")
v_base = raw_df[["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]].iloc[[0]].T.reset_index()
v_base.columns = ["項目", "內容值"]

e_base = st.data_editor(v_base, use_container_width=True, hide_index=True, key="v_be_1",
                        column_config={"項目": st.column_config.TextColumn("項目", disabled=True, width=150)})

if st.button("💾 儲存變更", key="save_base"):
    raw_df.loc[0, ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]] = e_base["內容值"].tolist()
    raw_df.loc[1, ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]] = e_base["內容值"].tolist()
    raw_df.to_csv(base_info_path, index=False)
    st.session_state.base_info_df = raw_df
    st.success("✅ 基本資料已更新")
    st.rerun()

st.divider()

# --- 表格 2：建蔽率、容積率、開挖率 (維持自動檢討功能) ---
st.subheader("📊 2. 建蔽率、容積率、開挖率")

if st.button("🔄 同步「各層面積計算」之實設容積總和"):
    try:
        floor_df = pd.read_csv(os.path.join(project_dir, "area_data.csv"))
        actual_sum = floor_df[floor_df["屬性"] == "計入容積"]["小計(㎡)"].sum()
        raw_df.loc[1, "容積樓地板面積(㎡)"] = f"{actual_sum:.2f}"
        st.session_state.base_info_df = raw_df
        st.toast(f"已同步容積總面積：{actual_sum:.2f} ㎡", icon="✅")
    except:
        st.error("同步失敗，請確認第4頁是否有資料。")

# 表格 2 的渲染邏輯 (含檢討)
def get_render_df_with_review(cols):
    v1 = raw_df[cols].iloc[[0]].T
    v2 = raw_df[cols].iloc[[1]].T
    res = pd.concat([v1, v2], axis=1).reset_index()
    res.columns = ["項目", "⚖️ 法定規範", "🏗️ 實設數值"]
    
    def calc_review(row):
        try:
            legal = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(row["⚖️ 法定規範"]))[0])
            actual = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(row["🏗️ 實設數值"]))[0])
            diff = legal - actual
            unit = "%" if "%" in row["項目"] else "㎡"
            return f"剩餘 {diff:.2f} {unit}" if diff > 0 else ("剛好" if diff==0 else "❌ 超過")
        except: return ""
    
    res["🔍 檢討"] = res.apply(calc_review, axis=1)
    res["📝 備註"] = [raw_df[f"{col}_備註"].iloc[0] for col in cols]
    return res

target_rule_cols_2 = ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)", "開挖率(%)", "開挖面積(㎡)"]
e_compare_2 = st.data_editor(get_render_df_with_review(target_rule_cols_2), use_container_width=True, hide_index=True, key="v_be_2",
                           column_config={"項目": st.column_config.TextColumn(disabled=True, width=180),
                                          "🔍 檢討": st.column_config.TextColumn(disabled=True, width=150)})

if st.button("💾 儲存變更", key="save_rules_2"):
    raw_df.loc[0, target_rule_cols_2] = e_compare_2["⚖️ 法定規範"].tolist()
    raw_df.loc[1, target_rule_cols_2] = e_compare_2["🏗️ 實設數值"].tolist()
    notes = e_compare_2["📝 備註"].tolist()
    for i, col in enumerate(target_rule_cols_2):
        raw_df.loc[0, f"{col}_備註"] = notes[i]
        raw_df.loc[1, f"{col}_備註"] = notes[i]
    raw_df.to_csv(base_info_path, index=False)
    st.session_state.base_info_df = raw_df
    st.success("✅ 表格 2 已更新")
    st.rerun()

st.divider()

# --- 表格 3：容積獎勵、容積移轉 (修正版：無檢討、更名軸位) ---
st.subheader("🚀 3. 容積獎勵、容積移轉")

# 表格 3 的渲染邏輯 (純記錄)
def get_render_df_simple(cols):
    v1 = raw_df[cols].iloc[[0]].T # 存儲於法定行
    v2 = raw_df[cols].iloc[[1]].T # 存儲於實設行
    res = pd.concat([v1, v2], axis=1).reset_index()
    res.columns = ["項目", "容積率(%)", "容積面積(㎡)"] # 欄位名稱更新
    res["📝 備註"] = [raw_df[f"{col}_備註"].iloc[0] for col in cols]
    return res

target_rule_cols_3 = ["法定容積(㎡)", "都更獎勵容積(㎡)", "容積移轉(㎡)", "允建容積(㎡)"]
e_compare_3 = st.data_editor(get_render_df_simple(target_rule_cols_3), use_container_width=True, hide_index=True, key="v_be_3",
                           column_config={"項目": st.column_config.TextColumn(disabled=True, width=180)})

if st.button("💾 儲存變更", key="save_rules_3"):
    # 對應回原始 CSV 的 row 0 與 row 1
    raw_df.loc[0, target_rule_cols_3] = e_compare_3["容積率(%)"].tolist()
    raw_df.loc[1, target_rule_cols_3] = e_compare_3["容積面積(㎡)"].tolist()
    notes = e_compare_3["📝 備註"].tolist()
    for i, col in enumerate(target_rule_cols_3):
        raw_df.loc[0, f"{col}_備註"] = notes[i]
        raw_df.loc[1, f"{col}_備註"] = notes[i]
    
    raw_df.to_csv(base_info_path, index=False)
    st.session_state.base_info_df = raw_df
    st.success("✅ 表格 3 已更新")
    st.rerun()