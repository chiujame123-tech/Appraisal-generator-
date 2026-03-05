import streamlit as st
import re
from data import fs278_db, highlight_keywords
from logic import load_gsheet, get_title, build_smart_paragraph

# ==========================================
# 介面設置與 CSS 美化
# ==========================================
st.set_page_config(page_title="Appraisal Generator", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: 700; color: #1a365d; margin-bottom: 0px; }
    .sub-title { font-size: 16px; color: #555555; margin-bottom: 20px; }
    div[data-testid="stSelectbox"] > label { color: #333333; font-weight: 600; display: none; }
    .preview-box { font-size: 13px; color: #0056b3; background-color: #f0f7ff; padding: 6px 10px; border-radius: 4px; margin-top: -12px; margin-bottom: 15px; border-left: 3px solid #0056b3; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 初始化 Session State (確保切換 Tab 不會流失資料)
# ==========================================
if "member_name" not in st.session_state:
    st.session_state["member_name"] = ""  # 已移除預設姓名
if "specific_case" not in st.session_state:
    st.session_state["specific_case"] = "例如於二零二四年四月十日在佐敦道華豐大廈發生的三級火警中，當日作為升降台隊目並以搜救隊身份執行任務。臨危不亂，有條理及清晰地指派各隊員執行任務，最終成功救出被困人士。"
if "events_input" not in st.session_state:
    st.session_state["events_input"] = "油尖旺社區應急防火嘉年華2024"
if "future_plan" not in st.session_state:
    st.session_state["future_plan"] = "參加煙火特攻員訓練課程"

# ==========================================
# 頁面標題
# ==========================================
st.markdown('<div class="main-title">Appraisal Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Appraisal System</div>', unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3 = st.tabs(["📄 考績生成系統 (Generator)", "📁 考績檔案庫 (Database)", "🖍️ 評分標記 (Highlighter)"])

# ==========================================
# TAB 1: 考績生成器
# ==========================================
with tab1:
    with st.container(border=True):
        st.markdown("**1. 基本資料 (Basic Information)**")
        col1, col2, col3, col4 = st.columns(4)
        with col1: 
            st.markdown("人員姓名")
            member_name = st.text_input("人員姓名", key="member_name", label_visibility="collapsed")
        with col2: 
            st.markdown("職級")
            member_rank = st.selectbox("職級", ["消防隊目", "消防總隊目", "消防員", "見習消防員"], key="member_rank", label_visibility="collapsed")
        with col3: 
            st.markdown("整體評級")
            overall_rating = st.selectbox("整體評級", ["優 (A)", "良 (B)", "常/當 (C)"], key="overall_rating", label_visibility="collapsed")
        with col4: 
            st.markdown("未來動向 / 建議訓練")
            future_plan = st.text_input("未來動向 / 建議訓練", key="future_plan", label_visibility="collapsed")

    with st.container(border=True):
        st.markdown("**2. 評分細項與寫法款式 (Assessment Criteria)**")
        st.caption("請揀選評級，並於其右方下拉選單選擇不同的文字風格，下方會即時顯示句子預覽。")
        
        with st.expander("點擊展開 / 收起 16 項評分設定", expanded=True):
            selections = {}
            items_list = list(fs278_db.keys())
            
            for i in range(0, len(items_list), 2):
                col_a1, col_a2, col_b1, col_b2 = st.columns([1.2, 2.5, 1.2, 2.5])
                
                # 第一個欄位
                item1 = items_list[i]
                with col_a1:
                    st.markdown(f"**{item1}**")
                    grade1 = st.selectbox(item1, ["優 (A)", "良 (B)", "常/當 (C)"], key=f"g_{i}", label_visibility="collapsed")
                with col_a2:
                    st.markdown("**款式選擇**")
                    variations1 = fs278_db[item1][grade1]
                    selected_idx1 = st.selectbox(
                        f"{item1}款式", 
                        options=range(len(variations1)), 
                        format_func=lambda x: f"{variations1[x]['desc']}",
                        key=f"s_{i}", 
                        label_visibility="collapsed"
                    )
                    selections[item1] = variations1[selected_idx1]
                    preview1 = variations1[selected_idx1].get('通用', variations1[selected_idx1].get('行動', ''))
                    st.markdown(f"<div class='preview-box'>📝 他{preview1}。</div>", unsafe_allow_html=True)
                
                # 第二個欄位
                if i + 1 < len(items_list):
                    item2 = items_list[i+1]
                    with col_b1:
                        st.markdown(f"**{item2}**")
                        grade2 = st.selectbox(item2, ["優 (A)", "良 (B)", "常/當 (C)"], key=f"g_{i+1}", label_visibility="collapsed")
                    with col_b2:
                        st.markdown("**款式選擇**")
                        variations2 = fs278_db[item2][grade2]
                        selected_idx2 = st.selectbox(
                            f"{item2}款式", 
                            options=range(len(variations2)), 
                            format_func=lambda x: f"{variations2[x]['desc']}",
                            key=f"s_{i+1}", 
                            label_visibility="collapsed"
                        )
                        selections[item2] = variations2[selected_idx2]
                        preview2 = variations2[selected_idx2].get('通用', variations2[selected_idx2].get('行動', ''))
                        st.markdown(f"<div class='preview-box'>📝 他{preview2}。</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**3. 具體案例與補充資料 (Supplementary Information)**")
        st.markdown("具體行動案例 (將插入至「行動表現」末段)：")
        specific_case = st.text_area("具體行動案例", key="specific_case", label_visibility="collapsed")
        st.markdown("近期參與的部門活動 (將插入至「總結」段落)：")
        events_input = st.text_input("近期參與的部門活動", key="events_input", label_visibility="collapsed")

    st.write("") 

    if st.button("生成正式考績報告 (Generate Report)", type="primary", use_container_width=True):
        para1_traits = []
        para2_ops = []
        para3_sta = []
        para4_misc = []

        for item_name, content_dict in selections.items():
            if "行動" in content_dict: para2_ops.append(content_dict["行動"])
            if "局內" in content_dict: para3_sta.append(content_dict["局內"])
            if "通用" in content_dict:
                if item_name in ["4. 可靠程度", "6. 服從紀律", "7. 幹勁與決心", "10. 分析能力", "14. 儀容和舉止", "15. 與人相處的技巧"]:
                    para1_traits.append(content_dict["通用"])
                elif item_name == "16. 支持/參加部門活動":
                    para4_misc.append(content_dict["通用"])

        # 獲取正確的主稱 (例如 "王隊目" 或 "李隊員")
        subject_title = get_title(st.session_state.member_name, st.session_state.member_rank)
        
        # 使用全新的 Context-Aware 語義連貫性引擎
        t1_text = build_smart_paragraph(para1_traits, subject_title)
        t2_text = build_smart_paragraph(para2_ops, subject_title)
        t3_text = build_smart_paragraph(para3_sta, subject_title)
        t4_text = build_smart_paragraph(para4_misc, subject_title)

        p1_text = f"【個人特質與紀律】\n{st.session_state.member_rank}{st.session_state.member_name}對工作盡忠職守。{t1_text}"
        p2_text = f"【行動工作表現】\n在行動工作方面，{subject_title}表現卓越。{t2_text}這點在他處理實際事故時表露無遺。{st.session_state.specific_case}"
        p3_text = f"【局內工作表現】\n在局內工作方面，{subject_title}極之能幹可靠。{t3_text}"
        
        misc_str = f"{t4_text}例如參與{st.session_state.events_input}。" if st.session_state.events_input else t4_text
        # 徹底移除「該員」，改為「他」
        p4_text = f"【總結與未來動向】\n{misc_str}整體來說，他在評核期內各方面工作表現令人滿意，故此我把他的表現評為「{st.session_state.overall_rating.split(' ')[0]}」級。在訓練方面，我建議他{st.session_state.future_plan}。"

        final_text = f"{p1_text}\n\n{p2_text}\n\n{p3_text}\n\n{p4_text}"
        
        st.divider()
        st.success("系統提示：報告已成功生成。請核對下方內容並複製。")
        st.text_area("📋 考績報告預覽 (Report Preview)：", final_text, height=450)

# ==========================================
# TAB 2: 舊料資料庫 (雲端 Google Sheet 同步版)
# ==========================================
with tab2:
    st.markdown("### 考績檔案庫 (Cloud Database)")
    st.caption("透過 Google Sheet 即時同步的歷年優秀考績撰寫範例。")
    
    df = load_gsheet()
    
    if df is None:
        st.error("⚠️ 系統無法連接至 Google Sheet 資料庫，請檢查分享權限設定。")
    else:
        expected_cols = ["總區", "年份", "職級", "標題", "考績文章"]
        if not all(col in df.columns for col in expected_cols):
            st.warning("📊 資料庫格式有誤：請確保 A 至 E 欄位名稱為「總區」、「年份」、「職級」、「標題」、「考績文章」。")
        else:
            with st.container(border=True):
                st.markdown("**檔案篩選**")
                region_ui = st.radio("篩選總區：", ["九龍總區", "香港總區", "新界南總區", "新界北總區"], horizontal=True, key="db_region")
                region_key = region_ui.replace("總區", "") 
                
                col_y, col_r = st.columns(2)
                with col_y:
                    st.markdown("年份")
                    years_in_sheet = df["年份"].dropna().astype(str).unique().tolist()
                    years = sorted(years_in_sheet, reverse=True) if years_in_sheet else ["2025", "2024", "2023"]
                    year_selected = st.selectbox("篩選年份：", years, label_visibility="collapsed", key="db_year")
                
                with col_r:
                    st.markdown("職級")
                    ranks = ["見習消防員", "消防員", "消防隊目", "消防總隊目"]
                    rank_selected = st.selectbox("篩選職級：", ranks, index=2, label_visibility="collapsed", key="db_rank")
                
            st.write("")
            
            filtered_df = df[
                (df["總區"].astype(str).str.contains(region_key, na=False)) & 
                (df["年份"].astype(str) == str(year_selected)) & 
                (df["職級"].astype(str) == str(rank_selected))
            ]
            
            if filtered_df.empty:
                st.info(f"💡 查無記錄：系統目前沒有 {year_selected} 年度 {region_key}總區【{rank_selected}】的檔案。")
            else:
                for idx, row in filtered_df.iterrows():
                    with st.expander(f"📄 檔案標題：{row['標題']} ({row['年份']})", expanded=False):
                        st.write(row['考績文章'])

# ==========================================
# TAB 3: Highlighter
# ==========================================
with tab3:
    st.markdown("### 評分標記系統 (Highlighter)")
    st.caption("將文本貼上，系統會自動辨識並標註對應的指標編號 (1-16)。")
    
    st.markdown("請於下方輸入考績報告文本：")
    if "text_to_highlight" not in st.session_state:
        st.session_state["text_to_highlight"] = "消防隊目陳大文對工作盡忠職守，極為嚴守紀律..."
        
    text_to_highlight = st.text_area("考績報告文本", key="text_to_highlight", height=200, label_visibility="collapsed")
    
    if st.button("開始標記分析 (Analyze Text)", type="primary"):
        if text_to_highlight:
            parts = re.split(r'([。，！？\n；])', text_to_highlight)
            highlighted_output = ""
            for i in range(0, len(parts)-1, 2):
                clause = parts[i]
                punct = parts[i+1]
                matched_item = None
                for item_num, pattern in highlight_keywords.items():
                    if re.search(pattern, clause):
                        matched_item = item_num
                        break
                if matched_item:
                    highlighted_output += f'<ruby><u style="text-decoration-color: #ff4b4b; text-decoration-thickness: 2px; text-underline-offset: 4px;">{clause}</u><rt style="color:#ff4b4b; font-weight:bold; font-size:0.9em; margin-bottom:2px;">{matched_item}</rt></ruby>{punct}'
                else:
                    highlighted_output += clause + punct
            
            if len(parts) % 2 != 0:
                highlighted_output += parts[-1]
                
            with st.container(border=True):
                st.markdown("**📝 分析結果 (Analysis Result)：**")
                st.markdown(f"<div style='line-height: 2.5; font-size: 16px; padding: 15px; border-radius: 5px; background-color: #f7fafc;'>{highlighted_output}</div>", unsafe_allow_html=True)
                st.caption("提示：紅線及數字代表對應的指標。")
        else:
            st.warning("請先輸入文本方可進行分析。")
