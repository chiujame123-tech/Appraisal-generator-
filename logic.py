# logic.py
import pandas as pd
import streamlit as st

@st.cache_data(ttl=60)
def load_gsheet():
    sheet_id = "1-wHN-fHSIrziB-KfM1Pck9S8qh8nWqDF-kMERfInoWg"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(csv_url)
        return df
    except Exception:
        return None

def get_title(name, rank):
    """根據姓名與職級，產出合適的尊稱，如 '王隊目' 或 '王隊員'"""
    surname = name[0] if name else ""
    if "隊目" in rank:
        return f"{surname}隊目"
    else:
        return f"{surname}隊員"

def categorize_sentence(sentence):
    """分析句子屬性，用於決定轉折詞"""
    if any(k in sentence for k in ["行政", "文書", "公文", "紀錄", "倉庫", "局內事宜", "管理"]):
        return "admin"
    if any(k in sentence for k in ["操練", "訓練", "講堂"]):
        return "drill"
    if any(k in sentence for k in ["滅火", "拯救", "火警", "事故", "現場", "救援"]):
        return "ops"
    if any(k in sentence for k in ["建議", "思考", "分析", "判斷", "策略", "組織"]):
        return "mind"
    if any(k in sentence for k in ["溝通", "講座", "參觀", "協調", "人際", "融洽", "教授"]):
        return "social"
    return "general"

def build_smart_paragraph(sentences, subject_title):
    """
    智能語義組裝引擎：
    1. 不再使用「該員」，全數採用「他」或「X隊目/隊員」。
    2. 根據前後文類別 (admin, drill, ops 等) 智能插入起承轉合字眼。
    """
    if not sentences:
        return ""
    
    result_text = ""
    prev_category = None
    
    # 預備一般連接詞輪流使用 (不含「該員」)
    default_connectors = [
        f"{subject_title}",
        f"此外，他",
        f"同時，他",
        f"另一方面，他",
        f"再者，他",
        f"他亦"
    ]

    for i, sentence in enumerate(sentences):
        clean_sentence = sentence.rstrip("。")
        curr_category = categorize_sentence(clean_sentence)
        
        # 決定轉折詞 (智能 Context-Aware 判斷)
        connector = ""
        if i == 0:
            connector = f"{subject_title}"
        else:
            if prev_category == "admin" and curr_category == "drill":
                connector = f"除了妥善處理各項繁重的行政工作外，在操練方面，他"
            elif prev_category == "ops" and curr_category == "mind":
                connector = f"在具備豐富前線經驗的同時，他"
            elif prev_category == "mind" and curr_category == "ops":
                connector = f"除了出色的分析能力外，在實際救援中，他"
            elif prev_category == "drill" and curr_category == "social":
                connector = f"在帶領局內訓練之餘，他"
            else:
                # 若無特殊語境轉換，則使用輪流的標準連接詞
                connector = default_connectors[i % len(default_connectors)]
        
        result_text += f"{connector}{clean_sentence}。"
        prev_category = curr_category
        
    return result_text
