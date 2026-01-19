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

# Load environment variables
load_dotenv()


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
    """Run Gemini analysis with optional web search"""
    if gemini_client is None:
        return "Gemini APIが設定されていません"
    
    try:
        if use_search:
            from google.genai import types
            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
        else:
            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt
            )
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"


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
