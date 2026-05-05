import pandas as pd
from pathlib import Path
import streamlit as st
import io

class ArchCalc:
    """
    專業建築計算核心大腦
    負責：數值轉換、標準化 CSV 存取、動態分區運算及 PDF 導出。
    """
    def __init__(self):
        pass

    def to_float(self, val):
        """
        強健的轉型工具：確保任何輸入（包含千分位逗號或空字串）都能安全轉換為浮點數。
        """
        try:
            if isinstance(val, (int, float)): return float(val)
            clean_val = str(val).replace(',', '').strip()
            return float(clean_val) if clean_val else 0.0
        except:
            return 0.0

    def calc_site_area(self, unit_area, minus_area, plus_area):
        """
        基地面積計算：基地面積 = 更新單元 - 須扣除 + 須加入
        """
        return self.to_float(unit_area) - self.to_float(minus_area) + self.to_float(plus_area)

    def save_csv(self, df, file_path):
        """
        標準化存檔工具：強制使用 utf-8-sig 編碼。
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            st.error(f"❌ 存檔至 {file_path.name} 失敗: {e}")
            return False

    def get_review_table(self, df, cols):
        """
        自動生成檢討對照表：
        將 CSV 的 Row 0 (法定) 與 Row 1 (實設) 轉換為 UI 顯示用的 DataFrame。
        """
        rows = []
        for col in cols:
            # 處理欄位名稱顯示美化
            display_name = col.replace("(%)", "").replace("(㎡)", "")
            
            legal_val = self.to_float(df.loc[0, col]) if col in df.columns else 0.0
            actual_val = self.to_float(df.loc[1, col]) if col in df.columns else 0.0
            
            # 自動判定合格狀態
            if actual_val == 0:
                status = "⚪ 待輸入"
            elif actual_val <= legal_val:
                status = "✅ 合格"
            else:
                status = "⚠️ 超出規範"

            rows.append({
                "項目": display_name,
                "⚖️ 法定規範": f"{legal_val:,.2f}",
                "🏗️ 實設數值": f"{actual_val:,.2f}",
                "🔍 檢討": status,
                "📝 備註": df.loc[0, f"{col}_備註"] if f"{col}_備註" in df.columns else ""
            })
        return pd.DataFrame(rows)

    def export_pdf(self, project_name, review_df):
        """
        快速導出 PDF 報告 (簡易版實作，使用 DataFrame 轉換)
        註：若需高度自定義樣式，建議於環境中安裝 fpdf 或 reportlab。
        此處提供一個標準的二進位流回傳，供 download_button 使用。
        """
        # 這是一個佔位符實作，實際上在 Streamlit 中通常會將 DF 轉為 HTML 再印出
        # 或是使用字串組合產生報表內容
        buffer = io.BytesIO()
        report_text = f"建築面積檢討報告 - {project_name}\n"
        report_text += "="*40 + "\n\n"
        report_text += review_df.to_string(index=False)
        
        buffer.write(report_text.encode('utf-8-sig'))
        return buffer.getvalue()

    # --- 新增：容積率加權運算邏輯 (針對多分區) ---
    def calc_weighted_far(self, df, num_zones):
        """
        計算多個使用分區的平均基準容積率
        """
        total_base_fa = 0.0
        total_zone_area = 0.0
        
        for i in range(num_zones):
            zh = ['一', '二', '三', '四'][i]
            area = self.to_float(df.loc[0, f"使用分區面積({zh})"])
            far = self.to_float(df.loc[0, f"法定容積率_分區{zh}"])
            
            total_base_fa += area * (far / 100)
            total_zone_area += area
            
        return total_base_fa, total_zone_area