import streamlit as st
import pandas as pd
import os
import re
from utils import init_sidebar

# 0. 配置與初始化
st.set_page_config(page_title="面積表", layout="wide")
curr_proj = init_sidebar()

# --- 視覺修正 ---
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem !important; }
        hr { margin-top: 0.8rem !important; margin-bottom: 1.5rem !important; }
        [data-testid="stForm"] { padding: 0.5rem 0rem !important; border: none !important; }
        .stTextInput label { font-weight: bold !important; color: #1e3a8a !important; }
    </style>
""", unsafe_allow_html=True)

project_dir = f"projects/{curr_proj}"
base_info_path = os.path.join(project_dir, "base_info.csv")

if not os.path.exists(project_dir):
    os.makedirs(project_dir, exist_ok=True)

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
    with st.form("form_base_minimal"):
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            in_lot = st.text_input("📍 輸入基地地號", value=raw_df.loc[0, "基地地號"])
            in_t_area = st.text_input("📄 輸入謄本面積 (㎡)", value=raw_df.loc[0, "謄本面積(㎡)"])
        with b_col2:
            in_zone = st.text_input("🏙️ 輸入使用分區", value=raw_df.loc[0, "使用分區"])
            in_s_area = st.text_input("📐 輸入基地面積 (㎡)", value=raw_df.loc[0, "基地面積(㎡)"])

        if st.form_submit_button("💾 儲存變更", use_container_width=True):
            raw_df.loc[0, ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]] = [in_lot, in_zone, in_t_area, in_s_area]
            raw_df.loc[1, ["基地地號", "使用分區", "謄本面積(㎡)", "基地面積(㎡)"]] = [in_lot, in_zone, in_t_area, in_s_area]
            raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
            st.session_state.base_info_df = raw_df
            st.success("✅ 基地基本資料已更新")
            st.rerun()

# --- 2. 建蔽率、容積率、開挖率 ---
with st.expander("📊 2. 建蔽率、容積率、開挖率 (法規檢討)", expanded=True):
    
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
                elif diff == 0: return "符合"
                else: return f"超過 {abs(diff):.2f} {unit}"
            except: return "-"
        res["🔍 檢討"] = res.apply(calc_review, axis=1)
        res["📝 備註"] = [raw_df[f"{col}_備註"].iloc[0] for col in cols]
        return res

    cols_a = ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)"]
    cols_b = ["允建容積率(%)", "容積樓地板面積(㎡)"]
    cols_c = ["開挖率(%)", "開挖面積(㎡)"]

    locked_config = {
        "項目": st.column_config.TextColumn(disabled=True, width=180),
        "⚖️ 法定規範": st.column_config.TextColumn(disabled=True),
        "🏗️ 實設數值": st.column_config.TextColumn(disabled=True),
        "🔍 檢討": st.column_config.TextColumn(disabled=True, width=150),
        "📝 備註": st.column_config.TextColumn(disabled=False)
    }

    with st.form("form_rules_2_split"):
        # --- 表格一：建蔽率檢討 ---
        st.markdown("### 表格一：建蔽率檢討")
        input_col1_a, input_col2_a = st.columns(2)
        with input_col1_a:
            legal_bc = st.text_input("📝 輸入法定建蔽率 (%)", value=raw_df.loc[0, "建蔽率(%)"], key="in_bc_l")
        with input_col2_a:
            actual_ba = st.text_input("🏗️ 輸入實設建築面積 (㎡)", value=raw_df.loc[1, "建築面積(㎡)"], key="in_ba_a")
        e_a = st.data_editor(get_render_df_with_review(cols_a), use_container_width=True, hide_index=True, key="v_be_2_a", column_config=locked_config)
        
        # --- 表格二：容積率檢討 ---
        st.markdown("### 表格二：容積率檢討")
        input_col1_b, input_col2_b = st.columns(2)
        with input_col1_b:
            legal_far = st.text_input("📝 輸入法定容積率 (%)", value=raw_df.loc[0, "法定容積(㎡)"], key="in_far_l")
            bonus_far = st.text_input("📝 輸入容積獎勵 (%)", value=raw_df.loc[0, "都更獎勵容積(㎡)"], key="in_far_b")
        with input_col2_b:
            transfer_far = st.text_input("📝 輸入容積移轉 (%)", value=raw_df.loc[0, "容積移轉(㎡)"], key="in_far_t")
            actual_fa = st.text_input("🏗️ 輸入實設容積樓地板面積 (㎡)", value=raw_df.loc[1, "容積樓地板面積(㎡)"], key="in_fa_a")
        e_b = st.data_editor(get_render_df_with_review(cols_b), use_container_width=True, hide_index=True, key="v_be_2_b", column_config=locked_config)
        
        # --- 表格三：開挖率檢討 ---
        st.markdown("### 表格三：開挖率檢討")
        input_col1_c, input_col2_c = st.columns(2)
        with input_col1_c:
            legal_exc = st.text_input("📝 輸入法定開挖率 (%)", value=raw_df.loc[0, "開挖率(%)"], key="in_exc_l")
        with input_col2_c:
            actual_exa = st.text_input("🏗️ 輸入實設開挖面積 (㎡)", value=raw_df.loc[1, "開挖面積(㎡)"], key="in_exa_a")
        e_c = st.data_editor(get_render_df_with_review(cols_c), use_container_width=True, hide_index=True, key="v_be_2_c", column_config=locked_config)

        if st.form_submit_button("💾 儲存變更", use_container_width=True):
            try:
                site_area = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(raw_df.loc[0, "基地面積(㎡)"]))[0])
            except: site_area = 0.0

            # 1. 建蔽率連動
            try:
                bc_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(legal_bc))[0])
                actual_ba_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(actual_ba))[0])
                raw_df.loc[0, "建蔽率(%)"] = f"{bc_val}"
                l_ba = site_area * (bc_val / 100)
                raw_df.loc[0, "建築面積(㎡)"] = f"{l_ba:.2f}"
                raw_df.loc[0, "空地面積(㎡)"] = f"{(site_area - l_ba):.2f}"
                raw_df.loc[1, "建蔽率(%)"] = f"{(actual_ba_val / site_area * 100 if site_area > 0 else 0):.2f}"
                raw_df.loc[1, "建築面積(㎡)"] = f"{actual_ba_val:.2f}"
                raw_df.loc[1, "空地面積(㎡)"] = f"{(site_area - actual_ba_val):.2f}"
            except: pass

            # 2. 容積率連動 (新增邏輯)
            try:
                l_far = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(legal_far))[0])
                b_far = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(bonus_far or 0))[0])
                t_far = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(transfer_far or 0))[0])
                a_fa_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(actual_fa))[0])

                # 法定連動：允建容積率% = 法定% * (1 + 獎勵% + 移轉%)
                total_far_ratio = l_far * (1 + (b_far / 100) + (t_far / 100))
                raw_df.loc[0, "允建容積率(%)"] = f"{total_far_ratio:.2f}"
                
                # 法定連動：容積樓地板面積㎡ = 允建容積率% * 基地面積
                raw_df.loc[0, "容積樓地板面積(㎡)"] = f"{(site_area * total_far_ratio / 100):.2f}"
                
                # 實設連動
                raw_df.loc[1, "容積樓地板面積(㎡)"] = f"{a_fa_val:.2f}"
                raw_df.loc[1, "允建容積率(%)"] = f"{(a_fa_val / site_area * 100 if site_area > 0 else 0):.2f}"
                
                # 同步儲存原始輸入值供下次讀取
                raw_df.loc[0, "法定容積(㎡)"] = f"{l_far}"
                raw_df.loc[0, "都更獎勵容積(㎡)"] = f"{b_far}"
                raw_df.loc[0, "容積移轉(㎡)"] = f"{t_far}"
            except: pass

            # 3. 開挖率連動
            try:
                exc_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(legal_exc))[0])
                actual_exa_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(actual_exa))[0])
                raw_df.loc[0, "開挖率(%)"] = f"{exc_val}"
                raw_df.loc[0, "開挖面積(㎡)"] = f"{(site_area * exc_val / 100):.2f}"
                raw_df.loc[1, "開挖率(%)"] = f"{(actual_exa_val / site_area * 100 if site_area > 0 else 0):.2f}"
                raw_df.loc[1, "開挖面積(㎡)"] = f"{actual_exa_val:.2f}"
            except: pass

            # 4. 備註儲存
            for editor, cols in zip([e_a, e_b, e_c], [cols_a, cols_b, cols_c]):
                notes = editor["📝 備註"].tolist()
                for i, col in enumerate(cols):
                    raw_df.loc[0, f"{col}_備註"] = notes[i]
                    raw_df.loc[1, f"{col}_備註"] = notes[i]
            
            raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
            st.session_state.base_info_df = raw_df
            st.success("✅ 所有法規連動數據已更新並儲存")
            st.rerun()

# --- 3. 容積獎勵、容積移轉 ---
with st.expander("🚀 3. 容積獎勵、容積移轉", expanded=False):
    def get_render_df_simple(cols):
        v1 = raw_df[cols].iloc[[0]].T
        v2 = raw_df[cols].iloc[[1]].T
        res = pd.concat([v1, v2], axis=1).reset_index()
        res.columns = ["項目", "比率(%)", "面積(㎡)"]
        res["📝 備註"] = [raw_df[f"{col}_備註"].iloc[0] for col in cols]
        return res

    target_rule_cols_3 = ["法定容積(㎡)", "都更獎勵容積(㎡)", "容積移轉(㎡)", "允建容積(㎡)"]
    with st.form("form_rules_3"):
        e_compare_3 = st.data_editor(
            get_render_df_simple(target_rule_cols_3), use_container_width=True, hide_index=True, key="v_be_3",
            column_config={"項目": st.column_config.TextColumn(disabled=True, width=180)}
        )
        if st.form_submit_button("💾 儲存變更", use_container_width=True):
            raw_df.loc[0, target_rule_cols_3] = e_compare_3["比率(%)"].tolist()
            raw_df.loc[1, target_rule_cols_3] = e_compare_3["面積(㎡)"].tolist()
            notes = e_compare_3["📝 備註"].tolist()
            for i, col in enumerate(target_rule_cols_3):
                raw_df.loc[0, f"{col}_備註"] = notes[i]
                raw_df.loc[1, f"{col}_備註"] = notes[i]
            raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
            st.session_state.base_info_df = raw_df
            st.success("✅ 獎勵詳細資料已儲存")
            st.rerun()