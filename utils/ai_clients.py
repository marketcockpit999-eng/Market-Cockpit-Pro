# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - AI Clients
Gemini/Claude AI関連関数を管理
"""

import os
import datetime
import streamlit as st
from dotenv import load_dotenv

from .config import GEMINI_MODEL, CLAUDE_MODEL
from .indicators import INDICATORS, get_indicators_by_category

# Load environment variables
load_dotenv()


# =============================================================================
# SPECIALIZED REPORT CATEGORIES
# =============================================================================
REPORT_CATEGORIES = {
    'fed_policy': {
        'name_ja': '🏦 Fed政策・金融政策',
        'name_en': '🏦 Fed Policy & Monetary Policy',
        'indicator_categories': ['fed_liquidity', 'fed_plumbing', 'rates'],
        'search_keywords': 'Federal Reserve policy 2026 FOMC balance sheet quantitative tightening',
        'prompt_focus_ja': 'Fed政策の現状、金利決定の背景、バランスシート縮小の進捗',
        'prompt_focus_en': 'Current Fed policy stance, rate decision context, balance sheet normalization progress',
    },
    'liquidity': {
        'name_ja': '💧 流動性・配管',
        'name_en': '💧 Liquidity & Plumbing',
        'indicator_categories': ['fed_liquidity', 'fed_plumbing', 'liquidity'],
        'search_keywords': 'market liquidity 2026 repo market ON RRP reverse repo TGA treasury',
        'prompt_focus_ja': '流動性環境の変化、ON RRP枯渇の影響、配管リスク',
        'prompt_focus_en': 'Liquidity conditions, ON RRP depletion impact, plumbing risks',
    },
    'inflation_rates': {
        'name_ja': '📈 インフレ・金利',
        'name_en': '📈 Inflation & Rates',
        'indicator_categories': ['inflation', 'rates', 'inflation_expectations'],
        'search_keywords': 'US inflation 2026 CPI PCE Treasury yields inflation expectations',
        'prompt_focus_ja': 'インフレ動向、金利見通し、実質金利の水準',
        'prompt_focus_en': 'Inflation trends, rate outlook, real interest rate levels',
    },
    'employment': {
        'name_ja': '👷 雇用・景気',
        'name_en': '👷 Employment & Economy',
        'indicator_categories': ['employment', 'consumption', 'gdp', 'sentiment'],
        'search_keywords': 'US jobs report 2026 unemployment NFP payroll GDP consumer spending',
        'prompt_focus_ja': '雇用市場の健全性、消費動向、景気見通し',
        'prompt_focus_en': 'Labor market health, consumer trends, economic outlook',
    },
    'banking': {
        'name_ja': '🏛️ 銀行・信用',
        'name_en': '🏛️ Banking & Credit',
        'indicator_categories': ['banking_sloos', 'banking_h8', 'banking_loans', 'financial_stress', 'credit'],
        'search_keywords': 'US banking 2026 bank lending standards credit conditions CRE commercial real estate',
        'prompt_focus_ja': '銀行セクターの健全性、融資基準、CREリスク',
        'prompt_focus_en': 'Banking sector health, lending standards, CRE risk exposure',
    },
    'crypto': {
        'name_ja': '₿ 暗号資産',
        'name_en': '₿ Crypto',
        'indicator_categories': ['crypto'],
        'search_keywords': 'Bitcoin 2026 crypto market BTC ETF flows stablecoin institutional adoption',
        'prompt_focus_ja': '暗号資産市場の動向、流動性との相関、機関投資家動向',
        'prompt_focus_en': 'Crypto market dynamics, liquidity correlation, institutional flows',
    },
}


def init_ai_clients():
    """Initialize AI clients (Gemini & Claude) from environment variables"""
    
    gemini_client = None
    claude_client = None
    
    # Configure Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        try:
            from google import genai
            gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            print(f"Gemini init error: {e}")

    # Configure Claude API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if ANTHROPIC_API_KEY:
        try:
            import anthropic
            claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"Claude init error: {e}")
            
    return gemini_client, claude_client


def get_market_summary(df):
    """Generate a comprehensive summary of ALL monitored market conditions for AI analysis"""
    summary_parts = []
    
    def add_metric(name, col_name, unit="", with_change=False, change_days=7, show_date=False, is_level=False):
        """Helper to add a metric to summary"""
        if col_name in df.columns:
            data = df[col_name].dropna()
            if len(data) > 0:
                current = data.iloc[-1]
                last_date = data.index[-1].strftime('%Y/%m/%d') if hasattr(data.index[-1], 'strftime') else str(data.index[-1])[:10]
                
                type_tag = "[Level]" if is_level else "[Change]"
                
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
    
    # Date
    summary_parts.append(f"=== 市場データサマリー ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
    
    # Liquidity
    summary_parts.append("【流動性 (Plumbing)】")
    add_metric("Net Liquidity", "Net_Liquidity", "B", with_change=True, is_level=True)
    add_metric("Fed Assets", "Fed_Assets", "B", with_change=True, is_level=True)
    add_metric("TGA", "TGA", "B", with_change=True, is_level=True)
    add_metric("ON RRP", "ON_RRP", "B", with_change=True, is_level=True)
    add_metric("Reserves", "Reserves", "B", with_change=True, is_level=True)
    add_metric("SOMA Total", "SOMA_Total", "B", with_change=True, is_level=True)
    add_metric("SOMA Bills", "SOMA_Bills", "B", with_change=True, is_level=True)
    add_metric("SOMA Bills Ratio", "SomaBillsRatio", "%", with_change=True)
    add_metric("Global Liquidity Proxy", "Global_Liquidity_Proxy", "B", with_change=True, is_level=True)
    add_metric("M2 Velocity", "M2_Velocity", "", with_change=True, is_level=True)
    add_metric("Financial Stress", "Financial_Stress", "", with_change=True)
    
    # Rates
    summary_parts.append("\n【金利】")
    add_metric("EFFR", "EFFR", "%")
    add_metric("SOFR", "SOFR", "%")
    add_metric("IORB", "IORB", "%")
    add_metric("FF Upper", "FedFundsUpper", "%")
    add_metric("US 10Y", "US_TNX", "%")
    add_metric("2Y-10Y Spread", "T10Y2Y", "%")
    add_metric("Credit Spread", "Credit_Spread", "%")
    
    # Emergency
    summary_parts.append("\n【緊急融資】")
    add_metric("SRF", "SRF", "B", is_level=True)
    add_metric("FIMA", "FIMA", "B", is_level=True)
    add_metric("Primary Credit", "Primary_Credit", "B", is_level=True)
    add_metric("Total Loans", "Total_Loans", "B", is_level=True)
    
    # Banking
    summary_parts.append("\n【銀行セクター】")
    add_metric("Bank Cash", "Bank_Cash", "B", is_level=True)
    add_metric("Lending Standards", "Lending_Standards", "pts")
    add_metric("C&I Loans", "CI_Loans", "B", is_level=True)
    add_metric("CRE Loans", "CRE_Loans", "B", is_level=True)
    
    # Money Supply
    summary_parts.append("\n【マネーサプライ】")
    add_metric("M2 (Nominal)", "M2SL", "T", is_level=True)
    add_metric("M2 (Real)", "M2REAL", "T", is_level=True)
    add_metric("US Real M2 Index", "US_Real_M2_Index", "", is_level=True)
    
    # Global M2
    summary_parts.append("\n【グローバルM2】")
    add_metric("Global M2 (True Total)", "Global_M2", "T USD", with_change=True, is_level=True)
    add_metric("JP M2", "JP_M2", "T JPY", is_level=True)
    add_metric("CN M2", "CN_M2", "T CNY", is_level=True)
    add_metric("EU M2", "EU_M2", "T EUR", is_level=True)
    add_metric("CN Credit Impulse", "CN_Credit_Impulse", "%")
    
    # Markets
    summary_parts.append("\n【市場】")
    add_metric("S&P 500", "SP500", "", with_change=True, is_level=True)
    add_metric("VIX", "VIX", "")
    add_metric("HYG", "HYG", "", is_level=True)
    
    # FX
    summary_parts.append("\n【為替】")
    add_metric("DXY", "DXY", "")
    add_metric("USD/JPY", "USDJPY", "")
    add_metric("EUR/USD", "EURUSD", "")
    add_metric("USD/CNY", "USDCNY", "")
    
    # Commodities
    summary_parts.append("\n【コモディティ】")
    add_metric("Gold", "Gold", "$", is_level=True)
    add_metric("Silver", "Silver", "$", is_level=True)
    add_metric("Oil (WTI)", "Oil", "$", is_level=True)
    add_metric("Copper", "Copper", "$", is_level=True)
    
    # Crypto
    summary_parts.append("\n【仮想通貨】")
    add_metric("Bitcoin", "BTC", "$", with_change=True, is_level=True)
    add_metric("Ethereum", "ETH", "$", with_change=True, is_level=True)
    
    # Crypto Leverage (DEX Data)
    summary_parts.append("\n【仮想通貨レバレッジ (DEX)】")
    try:
        from .data_fetcher import get_crypto_leverage_data
        leverage_data = get_crypto_leverage_data()
        if leverage_data:
            # BTC Open Interest
            if leverage_data.get('btc_open_interest'):
                oi_val = leverage_data['btc_open_interest'] / 1e9  # Convert to Billions
                summary_parts.append(f"BTC Open Interest: {oi_val:.2f}B USD")
            # ETH Open Interest
            if leverage_data.get('eth_open_interest'):
                oi_val = leverage_data['eth_open_interest'] / 1e9
                summary_parts.append(f"ETH Open Interest: {oi_val:.2f}B USD")
            # BTC Funding Rate
            if leverage_data.get('btc_funding_rate') is not None:
                fr = leverage_data['btc_funding_rate'] * 100  # Convert to percentage
                fr_label = "LONG優勢" if fr > 0.01 else ("SHORT優勢" if fr < -0.01 else "中立")
                summary_parts.append(f"BTC Funding Rate: {fr:.4f}% ({fr_label})")
            # ETH Funding Rate
            if leverage_data.get('eth_funding_rate') is not None:
                fr = leverage_data['eth_funding_rate'] * 100
                fr_label = "LONG優勢" if fr > 0.01 else ("SHORT優勢" if fr < -0.01 else "中立")
                summary_parts.append(f"ETH Funding Rate: {fr:.4f}% ({fr_label})")
            # Long/Short Ratio
            if leverage_data.get('btc_long_short_ratio'):
                ls = leverage_data['btc_long_short_ratio']
                ls_label = "ロング偏重" if ls > 1.2 else ("ショート偏重" if ls < 0.8 else "均衡")
                summary_parts.append(f"BTC Long/Short Ratio: {ls:.2f} ({ls_label})")
            # Data Source
            if leverage_data.get('data_source'):
                summary_parts.append(f"データソース: {leverage_data['data_source']}")
    except Exception as e:
        summary_parts.append(f"レバレッジデータ取得エラー: {str(e)}")
    
    # Economic
    summary_parts.append("\n【経済指標】")
    add_metric("NFP", "NFP", "K", is_level=True)
    add_metric("Unemployment", "UNRATE", "%")
    add_metric("Core PCE", "CorePCE", "%")
    add_metric("CPI", "CPI", "", is_level=True)
    add_metric("PPI", "PPI", "", is_level=True)
    add_metric("Real GDP", "RealGDP", "B", is_level=True)
    add_metric("Consumer Sentiment", "ConsumerSent", "")
    
    # RMP Status (i18n support - uses RMP_Status_Type and RMP_Weekly_Change)
    rmp_status_type = df['RMP_Status_Type'].iloc[-1] if 'RMP_Status_Type' in df.columns and len(df['RMP_Status_Type'].dropna()) > 0 else 'monitoring'
    rmp_weekly_change = df['RMP_Weekly_Change'].iloc[-1] if 'RMP_Weekly_Change' in df.columns and len(df['RMP_Weekly_Change'].dropna()) > 0 else None
    
    # Build RMP status text (English for AI context)
    if rmp_status_type == 'monitoring' or rmp_weekly_change is None:
        rmp_status = "RMP Monitoring (Started Dec 12, 2025)"
    elif rmp_status_type == 'active':
        rmp_status = f"RMP Active: +${rmp_weekly_change:.1f}B/week (target pace)"
    elif rmp_status_type == 'accelerating':
        rmp_status = f"RMP Accelerating: +${rmp_weekly_change:.1f}B/week (exceeds normal!)"
    elif rmp_status_type == 'slowing':
        rmp_status = f"RMP Slowing: +${rmp_weekly_change:.1f}B/week (pace deceleration)"
    elif rmp_status_type == 'selling':
        rmp_status = f"Bills Selling: ${rmp_weekly_change:.1f}B/week (RMP stopped?)"
    else:
        rmp_status = "RMP Monitoring"
    summary_parts.append(f"\n【RMP状況】\n{rmp_status}")
    
    return "\n".join(summary_parts)


def run_gemini_analysis(gemini_client, model, prompt, use_search=False):
    """Run Gemini analysis with optional web search
    
    Gemini 3 (gemini-3-pro-preview) requires explicit Thought Signatures 
    configuration when using tools like Google Search.
    
    See: https://ai.google.dev/gemini-api/docs/thinking
    """
    if gemini_client is None:
        return "Gemini APIが設定されていません"
    
    try:
        if use_search:
            from google.genai import types
            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    # Gemini 3 requires explicit thinking_config for tool calls
                    thinking_config=types.ThinkingConfig(
                        mode="AUTO"  # Automatically include thought process when needed
                    )
                )
            )
        else:
            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt
            )
        
        # Handle response - Thought Signatures may be included in response
        # For Gemini 3, response structure might include 'thinking' attribute
        # but we primarily need the text content for our use case
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'parts') and len(response.parts) > 0:
            # Extract text from parts if text attribute is not available
            text_parts = [part.text for part in response.parts if hasattr(part, 'text')]
            return '\n'.join(text_parts) if text_parts else "No text content in response"
        else:
            return "Unexpected response format from Gemini API"
            
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error messages for common Gemini 3 issues
        if 'thought' in error_msg.lower() or 'signature' in error_msg.lower():
            return f"Gemini Error (Thought Signatures): {error_msg}\nHint: Ensure thinking_config is properly configured for Gemini 3"
        return f"Gemini Error: {error_msg}"


def generate_category_report(gemini_client, model, category_key, df, lang='en'):
    """
    Generate a specialized report for a specific category using Gemini with web search.
    
    Args:
        gemini_client: Initialized Gemini client
        model: Model name (e.g., 'gemini-2.5-pro')
        category_key: Key from REPORT_CATEGORIES (e.g., 'fed_policy')
        df: DataFrame with market data
        lang: Language code ('en' or 'ja')
    
    Returns:
        Generated report text
    """
    if gemini_client is None:
        return "Gemini APIが設定されていません" if lang == 'ja' else "Gemini API not configured"
    
    if category_key not in REPORT_CATEGORIES:
        return f"Unknown category: {category_key}"
    
    cat_info = REPORT_CATEGORIES[category_key]
    cat_name = cat_info['name_ja'] if lang == 'ja' else cat_info['name_en']
    search_keywords = cat_info['search_keywords']
    prompt_focus = cat_info['prompt_focus_ja'] if lang == 'ja' else cat_info['prompt_focus_en']
    
    # Build category-specific data summary
    cat_data_parts = []
    for cat in cat_info['indicator_categories']:
        indicators = get_indicators_by_category(cat)
        for ind_key, ind_info in indicators.items():
            col_name = ind_info.get('column')
            if col_name and col_name in df.columns:
                data = df[col_name].dropna()
                if len(data) > 0:
                    current = data.iloc[-1]
                    last_date = data.index[-1].strftime('%Y/%m/%d') if hasattr(data.index[-1], 'strftime') else str(data.index[-1])[:10]
                    cat_data_parts.append(f"{ind_info.get('name', col_name)}: {current:.4g} (as of {last_date})")
    
    category_data = "\n".join(cat_data_parts) if cat_data_parts else "No data available for this category"
    
    # Language-specific instructions
    if lang == 'ja':
        language_instruction = """重要: 必ず日本語で回答してください。"""
        role_prompt = """あなたは伝説的なグローバル・マクロ・ストラテジストです。
単なるニュースの要約ではなく、データの背後にある「配管（Plumbing）」、つまり流動性の動きと市場参加者のインセンティブを分析します。"""
    else:
        language_instruction = """IMPORTANT: Respond entirely in English."""
        role_prompt = """You are a legendary global macro strategist.
Rather than simply summarizing news, you analyze the "plumbing" behind the data - the flow of liquidity and market participant incentives."""
    
    prompt = f"""{role_prompt}

{language_instruction}

## Task
Generate a specialized {cat_name} report.

## Focus Areas
{prompt_focus}

## Current Market Data ({cat_name})
{category_data}

## Instructions
1. Use web search to find the latest news and developments related to: {search_keywords}
2. Analyze how recent events impact the data shown above
3. Provide actionable insights and potential scenarios
4. Structure your report with clear sections

Please provide a comprehensive analysis."""
    
    # Use Gemini with web search (Grounding)
    return run_gemini_analysis(gemini_client, model, prompt, use_search=True)


def run_claude_analysis(claude_client, model, prompt):
    """Run Claude analysis"""
    if claude_client is None:
        return "Claude APIが設定されていません"
    
    try:
        response = claude_client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Claude Error: {str(e)}"
