import streamlit as st

# 1. 建立 FS-278 評分指標的資料庫 (字典映射)
fs278_database = {
    "工作認識": {
        "優 (A)": "極之熟悉分區內的各特別風險及其緊急應變計劃，對所有滅火拯救工具的運用都瞭如指掌，並非常熟悉各項行政及工作程序。",
        "良 (B)": "十分熟知分局內的各特別風險及其緊急應變計劃，對局內各種滅火拯救工具十分熟悉，並對個別的行政及工作程序有一定的認識。",
        "常/當 (C)": "認識分局內的各特別風險及其緊急應變計劃，對局內各種滅火拯救工具有一定的認識。"
    },
    "行動效率及專業能力": {
        "優 (A)": "在無需監督下，能非常迅速、有效地完成工作，作多方面的思考並常常能給予上級多個可行建議，能充分顧及自己、其他隊員及公眾的安全。",
        "良 (B)": "在無需監督下，能迅速有效地完成工作，經常能給予上級確切可行的建議，並能充分顧及自己及其他隊員的安全。",
        "常/當 (C)": "在有限的監督下，能迅速有效地完成工作，偶而能給予上級可行的建議。"
    },
    "領導才能": {
        "優 (A)": "能夠協助現場總指揮恰當地分配工作，調派及帶領各分隊有效地執行任務，並能全面照顧到事故現場各隊員的安全。在局內工作上，能夠帶領局內各類型的操練，即時糾正同事的錯誤。",
        "良 (B)": "能帶領分隊有效地執行上級委派的工作，照顧到事故現場各隊員的安全。在局內能協助主管處理各項事務，分析隊員長劣並調派得妥，令工作更有效率。",
        "常/當 (C)": "能帶領分隊執行上級委派的工作，照顧自己分隊各隊員的安全，並能帶領局內各類型的基本操練。"
    },
    "溝通能力": {
        "優 (A)": "使用無線電時能非常清晰簡潔地傳達信息。在防火講座中講解極之清晰、表現自信及耐性。在局內會議中能清楚表達意見，常給予建設性提議。",
        "良 (B)": "使用無線電時能十分清晰簡潔地傳達信息。面對到訪參觀人士時講解清晰、生動有趣及信心十足，並能清楚用文字記錄日常運作過程。",
        "常/當 (C)": "使用無線電時能清晰地傳達信息。面對到訪參觀人士時能簡單介紹局內運作。"
    }
}

st.set_page_config(page_title="FS-278 自動考績生成器", layout="wide")
st.title("📝 消防自動考績生成器 (基於 FS-278 指標)")

st.info("只需選擇各項目的評級，系統會自動抽取 FS-278 的官方評語並組合成完整文章。")

# 人員基本資料
col1, col2, col3 = st.columns(3)
with col1:
    member_name = st.text_input("人員姓名", "王國良")
with col2:
    member_rank = st.selectbox("職級", ["消防隊目", "消防總隊目", "消防員"])
with col3:
    overall_rating = st.selectbox("整體評級", ["優 (A)", "良 (B)", "常/當 (C)"])

st.markdown("---")
st.subheader("1. 評分項目 (根據 FS-278)")

# 評分選擇區
col_a, col_b = st.columns(2)
with col_a:
    grade_knowledge = st.selectbox("工作認識", ["優 (A)", "良 (B)", "常/當 (C)"])
    grade_efficiency = st.selectbox("行動效率及專業能力", ["優 (A)", "良 (B)", "常/當 (C)"])
with col_b:
    grade_leadership = st.selectbox("領導才能", ["優 (A)", "良 (B)", "常/當 (C)"])
    grade_communication = st.selectbox("溝通能力", ["優 (A)", "良 (B)", "常/當 (C)"])

st.markdown("---")
st.subheader("2. 具體事故案例補充 (這部分需手動輸入以加強說服力)")
specific_case = st.text_area(
    "請簡述一個具體行動案例（例如華豐大廈三級火）", 
    "例如於二零二四年四月十日在佐敦道華豐大廈發生的三級火警中，當日作為升降台隊目並以搜救隊身份執行任務。臨危不亂，有條理及清晰地指派各隊員執行所委派的任務，最終成功救出被困人士。"
)
events_input = st.text_input("近期參與的部門活動", "油尖旺社區應急防火嘉年華2024")

st.markdown("---")

# 生成邏輯
if st.button("🚀 一鍵生成 K Command 考績報告", type="primary"):
    
    # 抽取對應的評語
    text_knowledge = fs278_database["工作認識"][grade_knowledge]
    text_efficiency = fs278_database["行動效率及專業能力"][grade_efficiency]
    text_leadership = fs278_database["領導才能"][grade_leadership]
    text_communication = fs278_database["溝通能力"][grade_communication]
    
    # 組合文章結構 (模仿 K Command 風格)
    para1_traits = f"{member_rank}{member_name}對工作盡忠職守。在工作認識方面，他{text_knowledge}"
    
    para2_ops = f"在行動工作方面，{member_name[0]}隊目表現卓越。他{text_efficiency}這點在他處理實際事故時表露無遺。{specific_case}"
    
    para3_station = f"在局內工作及領導方面，他{text_leadership}同時，他具備極佳的溝通能力，{text_communication}"
    
    para4_misc = f"{member_name[0]}隊目亦非常支持部門活動，例如協助舉辦{events_input}。整體來說，他在評核期內各方面工作表現令人滿意，故此我把他的表現評為「{overall_rating.split(' ')[0]}」級。"
    
    # 顯示結果
    st.success("✅ 報告生成成功！請檢查下方文字：")
    final_text = f"{para1_traits}\n\n{para2_ops}\n\n{para3_station}\n\n{para4_misc}"
    st.text_area("複製您的考績報告：", final_text, height=350)

