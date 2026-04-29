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
        .calc-result { 
            font-size: 20px; font-weight: bold; color: #d32f2f; 
            padding: 10px; background-color: #f8f9fa; 
            border-radius: 5px; border-left: 5px solid #d32f2f;
            margin-bottom: 10px;
        }
        .hint-text {
            color: gray;
            font-style: italic;
            font-size: 0.9em;
            margin-left: 10px;
        }
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
    base_cols = [
        "案件名稱", "基地地號", "更新單元面積", 
        "使用分區(一)", "使用分區面積(一)", 
        "使用分區(二)", "使用分區面積(二)", 
        "須扣除面積", "扣除理由", 
        "須加入面積", "加入理由", 
        "基地面積(㎡)", "鄰房占用面積(㎡)",
        "法定容積率_分區一", "法定容積率_分區二"
    ]
    target_rule_cols = rule_cols_2 + rule_cols_3
    all_cols = base_cols + target_rule_cols + [f"{col}_備註" for col in target_rule_cols]

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

def parse_float_safe(val):
    try:
        return float(re.findall(r"[-+]?\d*\.\d+|\d+", str(val))[0])
    except:
        return 0.0

st.title(f"📐 面積表")
st.caption(f"當前專案：{curr_proj}")
st.divider()

# --- 1. 基地基本資料 ---
with st.expander("📑 1. 基地基本資料", expanded=True):
    with st.form("form_base"):
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1: in_name = st.text_input("📁 輸入案件名稱", value=raw_df.loc[0, "案件名稱"])
        with r1_c2: in_lot = st.text_input("📍 輸入基地地號", value=raw_df.loc[0, "基地地號"])
        st.divider()
        in_u_area = st.text_input("📄 輸入更新單元面積 (㎡)", value=raw_df.loc[0, "更新單元面積"])
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1: in_z1 = st.text_input("🏙️ 使用分區(一)", value=raw_df.loc[0, "使用分區(一)"])
        with r2_c2: in_z1_a = st.text_input("📐 使用分區面積(一) (㎡)", value=raw_df.loc[0, "使用分區面積(一)"])
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1: in_z2 = st.text_input("🏙️ 使用分區(二)", value=raw_df.loc[0, "使用分區(二)"])
        with r3_c2: in_z2_a = st.text_input("📐 輸入使用分區面積(二) (㎡)", value=raw_df.loc[0, "使用分區面積(二)"])
        st.divider()
        r4_c1, r4_c2 = st.columns(2)
        with r4_c1:
            in_minus = st.text_input("➖ 須扣除面積 (㎡)", value=raw_df.loc[0, "須扣除面積"])
            in_plus = st.text_input("➕ 須加入面積 (㎡)", value=raw_df.loc[0, "須加入面積"])
        with r4_c2:
            in_m_reason = st.text_input("💬 扣除理由", value=raw_df.loc[0, "扣除理由"])
            in_p_reason = st.text_input("💬 加入理由", value=raw_df.loc[0, "加入理由"])
        
        s_area = parse_float_safe(in_u_area) - parse_float_safe(in_minus) + parse_float_safe(in_plus)

        st.divider()
        st.markdown(f'🎯 **基地面積 (計算基準㎡)** <span class="hint-text">(更新單元面積 - 須扣除面積 + 須加入面積)</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc-result">{s_area:,.2f} ㎡</div>', unsafe_allow_html=True)

        if st.form_submit_button("💾 儲存基地資料", use_container_width=True):
            save_cols = ["案件名稱", "基地地號", "更新單元面積", "使用分區(一)", "使用分區面積(一)", "使用分區(二)", "使用分區面積(二)", "須扣除面積", "扣除理由", "須加入面積", "加入理由", "基地面積(㎡)"]
            save_data = [in_name, in_lot, in_u_area, in_z1, in_z1_a, in_z2, in_z2_a, in_minus, in_m_reason, in_plus, in_p_reason, f"{s_area:.2f}"]
            raw_df.loc[0, save_cols] = raw_df.loc[1, save_cols] = save_data
            raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
            st.session_state.base_info_df = raw_df
            st.rerun()

# --- 2. 法規檢討表格生成 ---
def get_render_df(cols):
    res = pd.concat([raw_df[cols].iloc[[0]].T, raw_df[cols].iloc[[1]].T], axis=1).reset_index()
    res.columns = ["項目", "⚖️ 法定規範", "🏗️ 實設數值"]
    def calc_review(row):
        try:
            l, a = parse_float_safe(row["⚖️ 法定規範"]), parse_float_safe(row["🏗️ 實設數值"])
            diff = l - a
            unit = "%" if "%" in row["項目"] else "㎡"
            return "符合" if diff >= -0.001 else f"超過 {abs(diff):.2f} {unit}"
        except: return "-"
    res["🔍 檢討"] = res.apply(calc_review, axis=1)
    res["📝 備註"] = [raw_df[f"{col}_備註"].iloc[0] for col in cols]
    return res

locked_config = {"項目": st.column_config.TextColumn(disabled=True, width=180), "⚖️ 法定規範": st.column_config.TextColumn(disabled=True), "🏗️ 實設數值": st.column_config.TextColumn(disabled=True), "🔍 檢討": st.column_config.TextColumn(disabled=True, width=150), "📝 備註": st.column_config.TextColumn(disabled=False)}

with st.form("form_rules_combined"):
    # 2. 建蔽率檢討
    with st.expander("📊 2. 建蔽率檢討", expanded=True):
        i_c1_a, i_c2_a = st.columns(2)
        with i_c1_a: legal_bc_in = st.text_input("📝 輸入法定建蔽率 (%)", value=raw_df.loc[0, "建蔽率(%)"], key="bc_l_in")
        with i_c2_a: neighbor_area = st.text_input("📝 輸入鄰房占用面積 (㎡)", value=raw_df.loc[0, "鄰房占用面積(㎡)"], key="neighbor_in")
        
        # --- 新增法定建蔽總結面板 ---
        bc_pct_curr = parse_float_safe(legal_bc_in)
        n_area_curr = parse_float_safe(neighbor_area)
        # 公式: (基地面積 - 鄰房占用) * 法定建蔽率 + 鄰房占用
        legal_ba_curr = (s_area - n_area_curr) * (bc_pct_curr / 100) + n_area_curr

        st.divider()
        bc_res_col1, bc_res_col2 = st.columns(2)
        with bc_res_col1:
            st.write("🎯 **法定建蔽率 (%)**")
            st.markdown(f'<div class="calc-result">{bc_pct_curr:.2f} %</div>', unsafe_allow_html=True)
        with bc_res_col2:
            st.write("🎯 **法定建築面積 (㎡)**")
            st.markdown(f'<div class="calc-result">{legal_ba_curr:,.2f} ㎡</div>', unsafe_allow_html=True)

        st.divider()
        actual_ba_in = st.text_input("🏗️ 輸入實設建築面積 (㎡)", value=raw_df.loc[1, "建築面積(㎡)"], key="ba_a_in")
        e_a = st.data_editor(get_render_df(["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)"]), use_container_width=True, hide_index=True, key="ebc", column_config=locked_config)

    # 3. 容積率檢討
    with st.expander("📊 3. 容積率檢討", expanded=True):
        st.write("🏙️ **分區基準容積率設定**")
        i_c1_z, i_c2_z = st.columns(2)
        with i_c1_z: l_far_z1 = st.text_input(f"📝 法定容積率({raw_df.loc[0, '使用分區(一)'] or '分區一'}) (%)", value=raw_df.loc[0, "法定容積率_分區一"], key="far_z1")
        with i_c2_z: l_far_z2 = st.text_input(f"📝 法定容積率({raw_df.loc[0, '使用分區(二)'] or '分區二'}) (%)", value=raw_df.loc[0, "法定容積率_分區二"], key="far_z2")
        
        z1_a = parse_float_safe(raw_df.loc[0, "使用分區面積(一)"])
        z2_a = parse_float_safe(raw_df.loc[0, "使用分區面積(二)"])
        base_fa_area = (z1_a * parse_float_safe(l_far_z1) / 100) + (z2_a * parse_float_safe(l_far_z2) / 100)
        base_far_pct = (base_fa_area / s_area * 100) if s_area > 0 else 0.0

        st.divider()
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.write("🎯 **基準容積率 (%)**")
            st.markdown(f'<div class="calc-result">{base_far_pct:.2f} %</div>', unsafe_allow_html=True)
        with res_col2:
            st.write("🎯 **基準容積面積 (㎡)**")
            st.markdown(f'<div class="calc-result">{base_fa_area:,.2f} ㎡</div>', unsafe_allow_html=True)
        
        st.divider()
        i_c1_b, i_c2_b = st.columns(2)
        with i_c1_b: bonus_area_in = st.text_input("📝 輸入容積獎勵面積 (㎡)", value=raw_df.loc[0, "都更獎勵容積(㎡)"], key="far_b_area")
        with i_c2_b: transfer_area_in = st.text_input("📝 輸入容積移轉面積 (㎡)", value=raw_df.loc[0, "容積移轉(㎡)"], key="far_t_area")
        
        b_area_curr = parse_float_safe(bonus_area_in)
        t_area_curr = parse_float_safe(transfer_area_in)
        total_fa_area_curr = base_fa_area + b_area_curr + t_area_curr
        total_far_pct_curr = (total_fa_area_curr / s_area * 100) if s_area > 0 else 0.0

        st.divider()
        total_res_c1, total_res_c2 = st.columns(2)
        with total_res_c1:
            st.write("🎯 **允建容積率 (%)**")
            st.markdown(f'<div class="calc-result">{total_far_pct_curr:.2f} %</div>', unsafe_allow_html=True)
        with total_res_c2:
            st.write("🎯 **允建容積樓地板面積 (㎡)**")
            st.markdown(f'<div class="calc-result">{total_fa_area_curr:,.2f} ㎡</div>', unsafe_allow_html=True)

        st.divider()
        actual_fa_in = st.text_input("🏗️ 輸入實設容積樓地板面積 (㎡)", value=raw_df.loc[1, "容積樓地板面積(㎡)"], key="fa_actual_in")
        e_b = st.data_editor(get_render_df(["允建容積率(%)", "容積樓地板面積(㎡)"]), use_container_width=True, hide_index=True, key="efar", column_config=locked_config)

    # 4. 開挖率檢討
    with st.expander("📊 4. 開挖率檢討", expanded=True):
        i_c1_c, i_c2_c = st.columns(2)
        with i_c1_c: l_exc = st.text_input("📝 輸入法定開挖率 (%)", value=raw_df.loc[0, "開挖率(%)"], key="exc_l")
        with i_c2_c: a_exa = st.text_input("🏗️ 輸入實設開挖面積 (㎡)", value=raw_df.loc[1, "開挖面積(㎡)"], key="exa_a")
        e_c = st.data_editor(get_render_df(["開挖率(%)", "開挖面積(㎡)"]), use_container_width=True, hide_index=True, key="eexc", column_config=locked_config)

    if st.form_submit_button("💾 儲存法規變更", use_container_width=True):
        # --- 建蔽率連動 ---
        try:
            bc_p, n_a, ba_a = parse_float_safe(legal_bc_in), parse_float_safe(neighbor_area), parse_float_safe(actual_ba_in)
            l_ba = (s_area - n_a) * (bc_p / 100) + n_a
            l_os = s_area * (1 - (bc_p / 100))
            raw_df.loc[0, ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "鄰房占用面積(㎡)"]] = [f"{bc_p}", f"{l_ba:.2f}", f"{l_os:.2f}", f"{n_a}"]
            raw_df.loc[1, "建蔽率(%)"] = f"{((ba_a - n_a) / (s_area - n_a) * 100 if (s_area - n_a) > 0 else 0):.2f}"
            raw_df.loc[1, ["建築面積(㎡)", "空地面積(㎡)"]] = [f"{ba_a:.2f}", f"{(s_area - ba_a):.2f}"]
        except: pass

        # --- 容積率連動 ---
        try:
            raw_df.loc[0, "法定容積率_分區一"], raw_df.loc[0, "法定容積率_分區二"] = f"{parse_float_safe(l_far_z1)}", f"{parse_float_safe(l_far_z2)}"
            act_fa = parse_float_safe(actual_fa_in)
            raw_df.loc[0, ["都更獎勵容積(㎡)", "容積移轉(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)"]] = [f"{b_area_curr}", f"{t_area_curr}", f"{total_far_pct_curr:.2f}", f"{total_fa_area_curr:.2f}"]
            raw_df.loc[1, ["允建容積率(%)", "容積樓地板面積(㎡)"]] = [f"{(act_fa / s_area * 100 if s_area > 0 else 0.0):.2f}", f"{act_fa:.2f}"]
        except: pass

        # --- 開挖率連動 ---
        try:
            le_v, ae_v = parse_float_safe(l_exc), parse_float_safe(a_exa)
            raw_df.loc[0, ["開挖率(%)", "開挖面積(㎡)"]] = [f"{le_v}", f"{(s_area * le_v / 100):.2f}"]
            raw_df.loc[1, ["開挖率(%)", "開挖面積(㎡)"]] = [f"{(ae_v / s_area * 100 if s_area > 0 else 0):.2f}", f"{ae_v:.2f}"]
        except: pass

        for ed, cols in zip([e_a, e_b, e_c], [["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)"], ["允建容積率(%)", "容積樓地板面積(㎡)"], ["開挖率(%)", "開挖面積(㎡)"]]):
            for i, col in enumerate(cols):
                raw_df.loc[0, f"{col}_備註"] = raw_df.loc[1, f"{col}_備註"] = ed["📝 備註"].tolist()[i]
        
        raw_df.to_csv(base_info_path, index=False, encoding='utf-8-sig')
        st.session_state.base_info_df = raw_df
        st.rerun()