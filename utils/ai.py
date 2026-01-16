import os
import datetime
import streamlit as st
from dotenv import load_dotenv
from google import genai
import anthropic

# Load environment variables
load_dotenv()

# Model names for latest reasoning AI
GEMINI_MODEL = "gemini-3-flash-preview"  # Latest Gemini 3 Flash
CLAUDE_MODEL = "claude-opus-4-5-20251101"  # Latest Claude Opus 4.5

def init_ai_clients():
    """Initialize AI clients (Gemini & Claude) from environment variables"""
    
    # Configure Gemini API (new google.genai library)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    gemini_client = None
    if GEMINI_API_KEY:
        try:
            gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            print(f"Gemini init error: {e}")

    # Configure Claude API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    claude_client = None
    if ANTHROPIC_API_KEY:
        try:
            claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"Claude init error: {e}")
            
    return gemini_client, claude_client

def get_market_summary(df):
    """Generate a comprehensive summary of ALL monitored market conditions for AI analysis"""
    summary_parts = []
    
    def add_metric(name, col_name, unit="", with_change=False, change_days=7, show_date=False, is_level=False):
        """Helper to add a metric to summary with strict labeling (Level vs Change)"""
        if col_name in df.columns:
            data = df[col_name].dropna()
            if len(data) > 0:
                current = data.iloc[-1]
                last_date = data.index[-1].strftime('%Y/%m/%d') if hasattr(data.index[-1], 'strftime') else str(data.index[-1])[:10]
                
                type_tag = "[Level/総数]" if is_level else "[Change/変化量・指数]"
                
                if with_change and len(data) >= change_days:
                    change = current - data.iloc[-change_days]
                    label = f"{name} {type_tag}: {current:.2f}{unit}"
                    change_label = f"({change_days}日変化: {change:+.2f}{unit})"
                    date_label = f" [更新: {last_date}]" if show_date else ""
                    summary_parts.append(f"{label} {change_label}{date_label}")
                else:
                    label = f"{name} {type_tag}: {current:.2f}{unit}"
                    date_label = f" [更新: {last_date}]" if show_date else ""
                    summary_parts.append(f"{label}{date_label}")
    
    # Add data freshness header
    summary_parts.append("【データ鮮度情報】")
    today = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
    summary_parts.append(f"分析実行日時: {today}")
    summary_parts.append("")
    
    # Focus areas (from session state)
    focus_selection = st.session_state.get('ai_focus_categories', [])
    if focus_selection:
        summary_parts.insert(0, "")
        for i, category in enumerate(reversed(focus_selection)):
            summary_parts.insert(0, f"  → {category}")
        summary_parts.insert(0, "【★★★ ユーザー注目領域（AIはこれらを特に重視して分析してください）★★★】")

    # Fed Liquidity
    summary_parts.append("【FRB流動性】")
    add_metric("Net Liquidity", "Net_Liquidity", "B", True, show_date=True, is_level=True)
    add_metric("ON RRP", "ON_RRP", "B", show_date=True, is_level=True)
    add_metric("Bank Reserves", "Reserves", "B", show_date=True, is_level=True)
    add_metric("TGA", "TGA", "B", show_date=True, is_level=True)
    add_metric("Fed Assets (WALCL)", "Fed_Assets", "B", show_date=True, is_level=True)
    add_metric("SOMA Total", "SOMA_Total", "B", is_level=True)
    add_metric("SOMA Bills", "SOMA_Bills", "B", True, is_level=True)
    
    # RMP Status
    if 'RMP_Status_Text' in df.columns:
        rmp_text = df['RMP_Status_Text'].dropna().iloc[-1]
        summary_parts.append(f"RMP状況: {rmp_text}")
    
    # Economic Indicators
    summary_parts.append("\n【米経済指標】")
    summary_parts.append("[金融政策]")
    add_metric("FF Rate Upper", "FedFundsUpper", "%", is_level=True)
    add_metric("EFFR", "EFFR", "%", is_level=True)
    add_metric("IORB", "IORB", "%", is_level=True)
    add_metric("SOFR", "SOFR", "%", is_level=True)
    
    summary_parts.append("[雇用関連]")
    add_metric("Unemployment Rate", "UNRATE", "%", is_level=True)
    add_metric("NFP Total (Level)", "NFP", "K", is_level=True)
    add_metric("Avg Hourly Earnings", "AvgHourlyEarnings", "$", is_level=True)
    add_metric("JOLTS Job Openings (Level)", "JOLTS", "K", is_level=True)
    add_metric("Initial Claims (Change)", "ICSA", "K")
    
    summary_parts.append("[物価・インフレ]")
    add_metric("CPI Index (Level)", "CPI", "", is_level=True)
    add_metric("CPI Core Index (Level)", "CPICore", "", is_level=True)
    add_metric("Core PCE YoY%", "CorePCE", "%")
    add_metric("PPI Index (Level)", "PPI", "", is_level=True)
    
    summary_parts.append("[景気・製造業]")
    add_metric("Retail Sales", "RetailSales", "M", is_level=True)
    add_metric("Consumer Sentiment", "ConsumerSent", "pt", is_level=True)
    add_metric("Real GDP (Level)", "RealGDP", "B", is_level=True)
    add_metric("2Y-10Y Spread", "T10Y2Y", "%", is_level=True)
    
    summary_parts.append("\n【マネーサプライ】")
    add_metric("US M2 (Nominal)", "M2SL", "B", is_level=True)
    add_metric("US M2 (Real)", "M2REAL", "B", is_level=True)
    add_metric("US Real M2 Index", "US_Real_M2_Index", "", is_level=True)
    add_metric("China M2", "CN_M2", "T CNY", is_level=True)
    add_metric("China Credit Impulse", "CN_Credit_Impulse", "%")
    add_metric("Japan M2", "JP_M2", "T JPY", is_level=True)
    add_metric("EU M2", "EU_M2", "T EUR", is_level=True)

    summary_parts.append("\n【銀行セクター】")
    add_metric("Bank Cash", "Bank_Cash", "B", is_level=True)
    add_metric("C&I Lending Std (Large)", "Lending_Standards", " pts", is_level=True)
    add_metric("C&I Lending Std (Small)", "CI_Std_Small", " pts", is_level=True)
    add_metric("C&I Demand", "CI_Demand", " pts", is_level=True)
    add_metric("C&I Loans", "CI_Loans", "B", is_level=True)
    add_metric("CRE Std (Construction)", "CRE_Std_Construction", " pts", is_level=True)
    add_metric("CRE Std (General)", "CRE_Std_Office", " pts", is_level=True)
    add_metric("CRE Loans", "CRE_Loans", "B", True, is_level=True)
    # H.8 Additional (2026-01-15)
    add_metric("Credit Card Loans", "Credit_Card_Loans", "B", True, is_level=True)
    add_metric("Consumer Loans", "Consumer_Loans", "B", is_level=True)
    add_metric("Bank Securities", "Bank_Securities", "B", is_level=True)
    add_metric("Bank Deposits", "Bank_Deposits", "B", True, is_level=True)
    # Gemini推奨 (2026-01-16)
    add_metric("Small Bank Deposits", "Small_Bank_Deposits", "B", True, is_level=True)
    add_metric("Total Loans & Leases", "Total_Loans", "B", True, is_level=True)
    add_metric("CC Delinquency Rate", "CC_Delinquency", "%", is_level=True)
    
    summary_parts.append("\n【金融ストレス指標 (Gemini推奨)】")
    add_metric("MOVE Index", "MOVE", "", is_level=True)  # 債券恐怖指数
    add_metric("Chicago Fed NFCI", "NFCI", "", is_level=True)  # 金融環境
    add_metric("10Y Breakeven Inflation", "Breakeven_10Y", "%", is_level=True)
    add_metric("CP Spread", "CP_Spread", "%", is_level=True)  # 企業資金ストレス
    # Copper/Gold Ratio (computed)
    if 'Copper' in df.columns and 'Gold' in df.columns:
        copper = df['Copper'].dropna()
        gold = df['Gold'].dropna()
        if len(copper) > 0 and len(gold) > 0:
            ratio = copper.iloc[-1] / gold.iloc[-1]
            summary_parts.append(f"Copper/Gold Ratio [Change]: {ratio:.4f} (景気先行指標)")
    
    summary_parts.append("\n【リスク・債券】")
    add_metric("VIX", "VIX", "", show_date=True, is_level=True)
    add_metric("Credit Spread (HY)", "Credit_Spread", "%", show_date=True, is_level=True)
    add_metric("US 10Y Yield", "US_TNX", "%", show_date=True, is_level=True)
    
    summary_parts.append("\n【株式・為替・商品】")
    if 'SP500' in df.columns:
        sp = df['SP500'].dropna()
        if len(sp) > 5:
            change_pct = ((sp.iloc[-1] / sp.iloc[-5]) - 1) * 100
            summary_parts.append(f"S&P 500 Index [Level]: {sp.iloc[-1]:,.0f} (週間: {change_pct:+.1f}%)")
    add_metric("BTC", "BTC", "", is_level=True)
    add_metric("ETH", "ETH", "", is_level=True)
    add_metric("DXY", "DXY", "", is_level=True)
    add_metric("USD/JPY", "USDJPY", "", is_level=True)
    add_metric("Gold", "Gold", "", is_level=True)
    add_metric("Oil (WTI)", "Oil", "", is_level=True)
    
    # Crypto Liquidity
    if 'crypto_summary_cache' in st.session_state:
        summary_parts.append("\n【クリプト流動性】")
        for line in st.session_state['crypto_summary_cache']:
            summary_parts.append(line)
    
    # Sentiment
    summary_parts.append("\n【センチメント】")
    if 'sentiment_fg_cache' in st.session_state:
        summary_parts.append(st.session_state['sentiment_fg_cache'])
    if 'sentiment_aaii_cache' in st.session_state:
        summary_parts.append(st.session_state['sentiment_aaii_cache'])
    
    return "\n".join(summary_parts)

def run_gemini_analysis(gemini_client, model, prompt, use_search=True):
    """Run Gemini analysis with optional Google Search grounding"""
    from google.genai import types
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    ) if use_search else None
    
    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )
    return response.text

def run_claude_analysis(claude_client, model, prompt):
    """Run Claude analysis"""
    message = claude_client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
