import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# --- 1. 路徑修正：確保深層分頁能讀取到根目錄的工具模組 ---
root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

# --- 2. 匯入標準模組與 UI 元件 ---
from state_manager import init_project_state, PROJECTS_DIR
from ui_components import render_sidebar, render_calc_result
from arch_calc import ArchCalc

# --- 3. 核心初始化 ---
# 取得主程式選定的專案
if 'global_project_selector' in st.session_state:
    curr_proj = st.session_state.global_project_selector
else:
    _, curr_proj = init_project_state()

calc = ArchCalc()
project_dir = PROJECTS_DIR / curr_proj
base_info_path = project_dir / "base_info.csv"

# --- 4. 資料載入邏輯 (還原完整欄位與分區偵測) ---
def load_data():
    base_cols = [
        "案件名稱", "基地地號", "更新單元面積", 
        "使用分區(一)", "使用分區面積(一)", "使用分區(二)", "使用分區面積(二)", 
        "使用分區(三)", "使用分區面積(三)", "使用分區(四)", "使用分區面積(四)", 
        "須扣除面積", "扣除理由", "須加入面積", "加入理由", "基地面積(㎡)", 
        "建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "鄰房占用面積(㎡)", 
        "法定容積率_分區一", "法定容積率_分區二", "法定容積率_分區三", "法定容積率_分區四",
        "都更獎勵容積(㎡)", "容積移轉(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)", 
        "開挖率(%)", "開挖面積(㎡)"
    ]
    all_cols = base_cols + [f"{c}_備註" for c in base_cols]
    
    if not project_dir.exists():
        project_dir.mkdir(parents=True, exist_ok=True)

    if not base_info_path.exists():
        # 建立兩列空資料 (Row 0: 法定/基準, Row 1: 實設)
        return pd.DataFrame([[""] * len(all_cols)] * 2, columns=all_cols)
    
    try:
        df = pd.read_csv(base_info_path, dtype=str).fillna("")
        for col in all_cols:
            if col not in df.columns: df[col] = ""
        return df[all_cols]
    except:
        return pd.DataFrame([[""] * len(all_cols)] * 2, columns=all_cols)

# 狀態同步
if 'df' not in st.session_state or st.session_state.get('last_proj_key') != curr_proj:
    st.session_state.df = load_data()
    st.session_state.last_proj_key = curr_proj
    
    # 偵測已有資料的分區數量
    existing_zones = 1
    for i, zh in enumerate(['二', '三', '四'], start=2):
        if st.session_state.df.loc[0, f"使用分區({zh})"] != "":
            existing_zones = i
    st.session_state.num_zones = existing_zones

df = st.session_state.df
locked_config = {
    "項目": st.column_config.TextColumn(disabled=True), 
    "⚖️ 法定規範": st.column_config.TextColumn(disabled=True), 
    "🏗️ 實設數值": st.column_config.TextColumn(disabled=True), 
    "🔍 檢討": st.column_config.TextColumn(disabled=True), 
    "📝 備註": st.column_config.TextColumn(disabled=False)
}

st.title(f"📐 面積表檢討 - {curr_proj}")
st.divider()

# --- 5. 基地基本資料 (還原雙向綁定與動態分區) ---
with st.expander("📑 1. 基地基本資料", expanded=True):
    with st.form("main_base_info_form"):
        r1_c1, r1_c2 = st.columns(2)
        f_name = r1_c1.text_input("📁 案件名稱", value=df.loc[0, "案件名稱"])
        f_lot = r1_c2.text_input("📍 基地地號", value=df.loc[0, "基地地號"])
        f_u_area = st.text_input("📄 更新單元面積 (㎡)", value=df.loc[0, "更新單元面積"])
        
        st.write("##### 🏙️ 使用分區明細")
        new_zones_input = []
        for i in range(st.session_state.num_zones):
            zh = ['一', '二', '三', '四'][i]
            z_c1, z_c2 = st.columns(2)
            zn = z_c1.text_input(f"🏙️ 使用分區({zh})", value=df.loc[0, f"使用分區({zh})"], key=f"zn_{i}")
            za = z_c2.text_input(f"📐 使用分區面積({zh})", value=df.loc[0, f"使用分區面積({zh})"], key=f"za_{i}")
            new_zones_input.append({"name": zn, "area": za})

        m_c1, m_c2 = st.columns([1, 2])
        f_minus = m_c1.text_input("➖ 須扣除面積", value=df.loc[0, "須扣除面積"])
        f_m_reason = m_c2.text_input("💬 扣除理由", value=df.loc[0, "扣除理由"])
        
        p_c1, p_c2 = st.columns([1, 2])
        f_plus = p_c1.text_input("➕ 須加入面積", value=df.loc[0, "須加入面積"])
        f_p_reason = p_c2.text_input("💬 加入理由", value=df.loc[0, "加入理由"])
        
        # 即時運算基地面積
        u_f, m_f, p_f = calc.to_float(f_u_area), calc.to_float(f_minus), calc.to_float(f_plus)
        s_area = calc.calc_site_area(u_f, m_f, p_f)
        render_calc_result("基地面積", s_area, formula=f"更新單元({u_f:,.2f}) - 扣除({m_f:,.2f}) + 加入({p_f:,.2f})")
        
        if st.form_submit_button("💾 儲存並更新基地資料", use_container_width=True):
            df.loc[0:1, ["案件名稱", "基地地號", "更新單元面積", "須扣除面積", "扣除理由", "須加入面積", "加入理由", "基地面積(㎡)"]] = \
                [f_name, f_lot, f_u_area, f_minus, f_m_reason, f_plus, f_p_reason, f"{s_area:.2f}"]
            
            # 清除舊分區並寫入新分區
            for idx in range(4):
                zh = ['一','二','三','四'][idx]
                df.loc[0:1, f"使用分區({zh})"], df.loc[0:1, f"使用分區面積({zh})"] = "", ""
            for idx, zone in enumerate(new_zones_input):
                zh = ['一','二','三','四'][idx]
                df.loc[0:1, f"使用分區({zh})"], df.loc[0:1, f"使用分區面積({zh})"] = zone["name"], zone["area"]
            
            calc.save_csv(df, base_info_path)
            st.success("✅ 基地資料已儲存"); st.rerun()

    b_col1, b_col2, _ = st.columns([1, 1, 4])
    if b_col1.button("➕ 增加分區列") and st.session_state.num_zones < 4:
        st.session_state.num_zones += 1; st.rerun()
    if b_col2.button("➖ 減少分區列") and st.session_state.num_zones > 1:
        st.session_state.num_zones -= 1; st.rerun()

# --- 6. 建蔽率檢討 (還原舊邏輯) ---
s_area_val = calc.to_float(df.loc[0, "基地面積(㎡)"])

with st.expander("📊 2. 建蔽率檢討", expanded=True):
    with st.form("form_bc"):
        c1, c2 = st.columns(2)
        l_bc_in = c1.text_input("📝 法定建蔽率 (%)", value=df.loc[0, "建蔽率(%)"])
        n_a_in = c2.text_input("📝 鄰房占用面積 (㎡)", value=df.loc[0, "鄰房占用面積(㎡)"])
        a_ba_in = st.text_input("🏗️ 實設建築面積 (㎡)", value=df.loc[1, "建築面積(㎡)"])
        
        l_bc, n_a = calc.to_float(l_bc_in), calc.to_float(n_a_in)
        l_ba = (s_area_val - n_a) * (l_bc / 100) + n_a
        render_calc_result("法定建築面積", l_ba, formula=f"(基地 {s_area_val:,.2f} - 占用 {n_a:,.2f}) × 建蔽率 {l_bc}% + 占用 {n_a:,.2f}")
        
        df.loc[0, "建蔽率(%)"], df.loc[0, "建築面積(㎡)"], df.loc[1, "建築面積(㎡)"] = f"{l_bc:.2f}", f"{l_ba:.2f}", a_ba_in
        ed_bc = st.data_editor(calc.get_review_table(df, ["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)"]), use_container_width=True, hide_index=True, column_config=locked_config, key="ed_bc")
        
        if st.form_submit_button("💾 儲存建蔽率檢討"):
            df.loc[0, "鄰房占用面積(㎡)"] = n_a_in
            for i, col in enumerate(["建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)"]):
                df.loc[0, f"{col}_備註"] = ed_bc["📝 備註"].iloc[i]
            calc.save_csv(df, base_info_path); st.success("✅ 建蔽率已更新"); st.rerun()

# --- 7. 容積率檢討 (還原舊邏輯) ---
with st.expander("📊 3. 容積率檢討", expanded=True):
    with st.form("form_far"):
        far_inputs = []; formula_parts = []
        for i in range(st.session_state.num_zones):
            zh = ['一', '二', '三', '四'][i]
            z_n = df.loc[0, f"使用分區({zh})"] or f"分區({zh})"
            z_a_val = calc.to_float(df.loc[0, f"使用分區面積({zh})"])
            val = calc.to_float(st.text_input(f"📝 法定容積({z_n}) (%)", value=df.loc[0, f"法定容積率_分區{zh}"], key=f"far_in_{i}"))
            far_inputs.append(val); formula_parts.append(f"{z_a_val:,.2f}×{val}%")

        base_fa = sum([calc.to_float(df.loc[0, f"使用分區面積({['一','二','三','四'][idx]})"]) * (far_inputs[idx] / 100) for idx in range(st.session_state.num_zones)])
        render_calc_result("基準容積面積", base_fa, formula=f"Σ({ ' + '.join(formula_parts) })")
        
        bonus = st.text_input("📝 容積獎勵面積 (㎡)", value=df.loc[0, "都更獎勵容積(㎡)"])
        trans = st.text_input("📝 容積移轉面積 (㎡)", value=df.loc[0, "容積移轉(㎡)"])
        a_fa_in = st.text_input("🏗️ 實設容積樓地板 (㎡)", value=df.loc[1, "容積樓地板面積(㎡)"])
        
        t_fa = base_fa + calc.to_float(bonus) + calc.to_float(trans)
        t_pct = (t_fa / s_area_val * 100) if s_area_val > 0 else 0.0
        render_calc_result("允建總容積", t_fa, formula=f"基準 {base_fa:,.2f} + 獎勵 {calc.to_float(bonus):,.2f} + 移轉 {calc.to_float(trans):,.2f}")
        
        df.loc[0, "允建容積率(%)"], df.loc[0, "容積樓地板面積(㎡)"], df.loc[1, "容積樓地板面積(㎡)"] = f"{t_pct:.2f}", f"{t_fa:.2f}", a_fa_in
        ed_far = st.data_editor(calc.get_review_table(df, ["允建容積率(%)", "容積樓地板面積(㎡)"]), use_container_width=True, hide_index=True, column_config=locked_config, key="ed_far")
        
        if st.form_submit_button("💾 儲存容積率檢討"):
            for idx in range(st.session_state.num_zones):
                df.loc[0, f"法定容積率_分區{['一','二','三','四'][idx]}"] = str(far_inputs[idx])
            df.loc[0, ["都更獎勵容積(㎡)", "容積移轉(㎡)"]] = [bonus, trans]
            for i, col in enumerate(["允建容積率(%)", "容積樓地板面積(㎡)"]):
                df.loc[0, f"{col}_備註"] = ed_far["📝 備註"].iloc[i]
            calc.save_csv(df, base_info_path); st.success("✅ 容積率已更新"); st.rerun()

# --- 8. 開挖率檢討 ---
with st.expander("📊 4. 開挖率檢討", expanded=True):
    with st.form("exc_form"):
        e1, e2 = st.columns(2)
        l_exc = e1.text_input("📝 法定開挖率 (%)", value=df.loc[0, "開挖率(%)"])
        a_exc = e2.text_input("🏗️ 實設開挖面積 (㎡)", value=df.loc[1, "開挖面積(㎡)"])
        
        l_exc_f = calc.to_float(l_exc)
        l_exc_a = s_area_val * (l_exc_f / 100)
        render_calc_result("法定開挖面積", l_exc_a, formula=f"基地 {s_area_val:,.2f} × {l_exc_f}%")
        
        df.loc[0, "開挖率(%)"], df.loc[0, "開挖面積(㎡)"], df.loc[1, "開挖面積(㎡)"] = f"{l_exc_f:.2f}", f"{l_exc_a:.2f}", a_exc
        ed_exc = st.data_editor(calc.get_review_table(df, ["開挖率(%)", "開挖面積(㎡)"]), use_container_width=True, hide_index=True, column_config=locked_config, key="ed_exc")
        
        if st.form_submit_button("💾 儲存開挖率檢討"):
            for i, col in enumerate(["開挖率(%)", "開挖面積(㎡)"]):
                df.loc[0, f"{col}_備註"] = ed_exc["📝 備註"].iloc[i]
            calc.save_csv(df, base_info_path); st.success("✅ 開挖率已更新"); st.rerun()

# --- 9. PDF 報告 (還原功能) ---
st.divider()
if st.button("📄 產生完整檢討 PDF 報告", use_container_width=True):
    report_cols = ["基地面積(㎡)", "建蔽率(%)", "建築面積(㎡)", "空地面積(㎡)", "允建容積率(%)", "容積樓地板面積(㎡)", "開挖率(%)", "開挖面積(㎡)"]
    pdf_data = calc.export_pdf(curr_proj, calc.get_review_table(df, report_cols))
    st.download_button("📥 下載 PDF 報告", data=pdf_data, file_name=f"{curr_proj}_建築檢討.pdf", use_container_width=True)