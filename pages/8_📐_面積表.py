import streamlit as st
import pandas as pd
import os
import re
from utils import init_sidebar

# 0. 配置與初始化
st.set_page_config(page_title="面積表", layout="wide")
curr_proj = init_sidebar()

# --- 💉 核心視覺區隔 CSS 注入 ---
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem !important; }
        
        /* 1. 基礎設定：讓表格內的單元格看起來更有層次 */
        [data-testid="stDataEditor"] div {
            font-family: 'Inter', sans-serif;
        }

        /* 2. 關鍵修正：針對「可編輯」單元格的表現法 */
        /* 我們針對未被標記為 disabled 的單元格增加輸入框視覺 */
        [data-testid="stTable"] [aria-disabled="false"], 
        div[data-testid="stDataEditor"] div[role="gridcell"][aria-selected="false"] {
            /* 預設顯示淡色背景與實線邊框，模擬 input field */
            border: 1px solid #e2e8f0 !important;
            background-color: #ffffff !important;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.05) !important;
            border-radius: 4px !important;
        }

        /* 3. 當滑鼠懸停 (Hover) 在可編輯區時，加強邊框色 */
        div[data-testid="stDataEditor"] div[role="gridcell"]:hover {
            border-color: #3b82f6 !important;
            background-color: #f0f7ff !important;
        }

        /* 4. 針對「禁用」單元格：維持灰色扁平感，與可編輯區區隔 */
        div[data-testid="stDataEditor"] div[role="gridcell"][aria-readonly="true"],
        [data-testid="stTable"] [aria-disabled="true"] {
            background-color: #f1f5f9 !important;
            color: #64748b !important;
            border: 1px solid #f1f5f9 !important;
            box-shadow: none !important;
        }

        /* 5. 小優化：編輯中的單元格高亮 */
        div[data-testid="stDataEditor"] div[role="gridcell"][data-active="true"] {
            border: 2px solid #3b82f6 !important;
            background-color: #ffffff !important;
        }

        /* 6. 下拉選單提示 (針對特定欄位或選單感) */
        div[data-testid="stDataEditor"] .role-selectbox::after {
            content: "▼";
            position: absolute;
            bottom: 2px;
            right: 4px;
            font-size: 8px;
            color: #94a3b8;
        }
    </style>
""", unsafe_allow_html=True)

project_dir = f"projects/{curr_proj}"
base_info_path = os.path.join(project_dir, "base_info.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

# 1. 資料載入 (邏輯保持不變)
def load_base_info():
    rule_cols_2 = ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)", "開挖率(%)", "開挖面積(㎡)"]
    rule_cols_3 = ["法定容積(㎡)", "都更獎勵容積(㎡)", "容積移轉(㎡)", "允建容積(㎡)"]
    target_rule_cols = rule_cols_2 + rule_cols_3
    base_cols = ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]
    note_cols = [f"{col}_備註" for col in target_rule_cols]
    all_cols = base_cols + target_rule_cols + note_cols

    if not os.path.exists(base_info_path):
        df = pd.DataFrame([[""] * len(all_cols), [""] * len(all_cols)], columns=all_cols)
        df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
        return df
    
    df = pd.read_csv(base_info_path, dtype=str).fillna("")
    for col in all_cols:
        if col not in df.columns: df[col] = ""
    return df[all_cols]

if 'base_info_df' not in st.session_state or st.session_state.get('area_last_proj_3_main') != curr_proj:
    st.session_state.base_info_df = load_base_info()
    st.session_state.area_last_proj_3_main = curr_proj

raw_df = st.session_state.base_info_df.copy()

st.title(f"📐 面積表")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 1. 基地基本資料 ---
with st.expander("📑 1. 基地基本資料", expanded=True):
    v_base = raw_df[["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]].iloc[[0]].T.reset_index()
    v_base.columns = ["項目", "內容值"]

    with st.form("form_base"):
        e_base = st.data_editor(
            v_base, use_container_width=True, hide_index=True, key="v_be_1",
            column_config={
                "項目": st.column_config.TextColumn("項目", disabled=True, width=150),
                "內容值": st.column_config.TextColumn("內容值") # 預設 editable
            }
        )
        if st.form_submit_button("💾 儲存基本資料變更", use_container_width=True):
            raw_df.loc[0, ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]] = e_base["內容值"].tolist()
            raw_df.loc[1, ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]] = e_base["內容值"].tolist()
            raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
            st.session_state.base_info_df = raw_df
            st.success("✅ 基本資料已更新")
            st.rerun()

# --- 2. 法規檢討 ---
with st.expander("📊 2. 建蔽率、容積率、開挖率 (法規檢討)", expanded=False):
    
    if st.button("🔄 同步「各層面積計算」之實設容積總和"):
        try:
            area_data_path = os.path.join(project_dir, "area_data.csv")
            if os.path.exists(area_data_path):
                floor_df = pd.read_csv(area_data_path)
                floor_df["小計(㎡)"] = pd.to_numeric(floor_df["小計(㎡)"], errors='coerce').fillna(0)
                actual_sum = floor_df[floor_df["屬性"] == "計入容積"]["小計(㎡)"].sum()
                raw_df.loc[1, "容積樓地板面積(㎡)"] = f"{actual_sum:.2f}"
                st.session_state.base_info_df = raw_df
                st.toast(f"已同步實設容積總面積：{actual_sum:.2f} ㎡", icon="✅")
                st.rerun()
        except: pass

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
                if diff > 0: return f"剩餘 {diff:.2f} {unit}"
                elif diff == 0: return "符合 (剛好)"
                else: return f"❌ 超過 {abs(diff):.2f} {unit}"
            except: return "-"
        
        res["🔍 檢討"] = res.apply(calc_review, axis=1)
        res["📝 備註"] = [raw_df[f"{col}_備註"].iloc[0] for col in cols]
        return res

    cols_a = ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)"]
    cols_b = ["允建容積率(%)", "容積樓地板面積(㎡)"]
    cols_c = ["開挖率(%)", "開挖面積(㎡)"]

    def render_split_table(cols, key):
        df = get_render_df_with_review(cols)
        return st.data_editor(
            df, use_container_width=True, hide_index=True, key=key,
            column_config={
                "項目": st.column_config.TextColumn("項目", disabled=True),
                "🔍 檢討": st.column_config.TextColumn("🔍 檢討", disabled=True),
                "⚖️ 法定規範": st.column_config.TextColumn("⚖️ 法定規範"),
                "🏗️ 實設數值": st.column_config.TextColumn("🏗️ 實設數值")
            }
        )

    with st.form("form_rules_2_split"):
        st.markdown("**表格一：建蔽率檢討**")
        e_a = render_split_table(cols_a, "v_be_2_a")
        st.markdown("**表格二：容積率檢討**")
        e_b = render_split_table(cols_b, "v_be_2_b")
        st.markdown("**表格三：開挖率檢討**")
        e_c = render_split_table(cols_c, "v_be_2_c")

        if st.form_submit_button("💾 儲存法規檢討變更 (所有表格)", use_container_width=True):
            try: site_area = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(raw_df.loc[0, "基地面積(㎡)"]))[0])
            except: site_area = 0.0

            combined_editors = [e_a, e_b, e_c]
            combined_cols = [cols_a, cols_b, cols_c]
            
            for editor, cols in zip(combined_editors, combined_cols):
                raw_df.loc[0, cols] = editor["⚖️ 法定規範"].tolist()
                raw_df.loc[1, cols] = editor["🏗️ 實設數值"].tolist()
                if "建蔽率(%)" in cols:
                    try:
                        legal_bc_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(raw_df.loc[0, "建蔽率(%)"]))[0])
                        raw_df.loc[0, "建築面積(㎡)"] = f"{(site_area * (legal_bc_val / 100)):.2f}"
                        actual_area_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(raw_df.loc[1, "建築面積(㎡)"]))[0])
                        raw_df.loc[1, "空地面積(㎡)"] = f"{(site_area - actual_area_val):.2f}"
                    except: pass
                
                notes = editor["📝 備註"].tolist()
                for i, col in enumerate(cols):
                    raw_df.loc[0, f"{col}_備註"] = notes[i]
                    raw_df.loc[1, f"{col}_備註"] = notes[i]
            
            raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
            st.session_state.base_info_df = raw_df
            st.success("✅ 儲存成功！連動欄位已自動更新")
            st.rerun()

# --- 3. 獎勵移轉 ---
with st.expander("🚀 3. 容積獎勵、容積移轉", expanded=False):
    target_rule_cols_3 = ["法定容積(㎡)", "都更獎勵容積(㎡)", "容積移轉(㎡)", "允建容積(㎡)"]
    v1 = raw_df[target_rule_cols_3].iloc[[0]].T
    v2 = raw_df[target_rule_cols_3].iloc[[1]].T
    res3 = pd.concat([v1, v2], axis=1).reset_index()
    res3.columns = ["項目", "容積率(%)", "容積面積(㎡)"]
    res3["📝 備註"] = [raw_df[f"{col}_備註"].iloc[0] for col in target_rule_cols_3]

    with st.form("form_rules_3"):
        e_compare_3 = st.data_editor(
            res3, use_container_width=True, hide_index=True, key="v_be_3",
            column_config={"項目": st.column_config.TextColumn("項目", disabled=True)}
        )
        if st.form_submit_button("💾 儲存獎勵與移轉變更", use_container_width=True):
            raw_df.loc[0, target_rule_cols_3] = e_compare_3["容積率(%)"].tolist()
            raw_df.loc[1, target_rule_cols_3] = e_compare_3["容積面積(㎡)"].tolist()
            notes = e_compare_3["📝 備註"].tolist()
            for i, col in enumerate(target_rule_cols_3):
                raw_df.loc[0, f"{col}_備註"] = notes[i]
                raw_df.loc[1, f"{col}_備註"] = notes[i]
            raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
            st.session_state.base_info_df = raw_df
            st.success("✅ 表格 3 已更新")
            st.rerun()