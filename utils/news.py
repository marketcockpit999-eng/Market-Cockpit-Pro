# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - News
ニュース取得、RSS処理、アラート関連関数を管理
"""

import datetime
import re
import requests
import feedparser
import streamlit as st

from .config import MONITORED_AGENCIES


def get_time_diff_str(date_str):
    """Calculate time difference from now and return a human-readable string."""
    try:
        from dateutil import parser
        from datetime import timezone
        
        now = datetime.datetime.now(timezone.utc)
        target_date = parser.parse(date_str)
        
        if target_date.tzinfo is None:
            return f"⚠️ {date_str[:16]}"
            
        diff = now - target_date
        seconds = diff.total_seconds()
        
        if seconds < 0:
            return "⚠️ 時刻不明"
        
        if seconds < 60:
            return "たった今"
        elif seconds < 3600:
            return f"{int(seconds // 60)}分前"
        elif seconds < 86400:
            return f"{int(seconds // 3600)}時間前"
        elif seconds < 604800:
            return f"{int(seconds // 86400)}日前"
        else:
            return target_date.strftime('%Y/%m/%d')
    except:
        return f"⚠️ {date_str[:16] if len(date_str) > 16 else date_str}"


def search_google_news(query: str, num_results: int = 5, gl: str = "US", mode: str = "primary") -> str:
    """
    Search Google News RSS for a topic
    
    Args:
        query: Search query
        num_results: Number of results to return
        gl: Geographic location (US, JP, GB, etc.)
        mode: 'primary' for original sources, 'all' for all results
    
    Returns:
        Formatted string with headlines
    """
    try:
        encoded_query = requests.utils.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-{gl}&gl={gl}&ceid={gl}:en"
        
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return f"「{query}」に関するニュースが見つかりませんでした。"
        
        results = []
        for entry in feed.entries[:num_results]:
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            published = entry.get('published', '')
            source = entry.get('source', {}).get('title', 'Unknown')
            
            time_diff = get_time_diff_str(published) if published else ""
            
            results.append(f"• [{time_diff}] **{title}**\n  _{source}_ | [Link]({link})")
        
        return "\n\n".join(results)
    except Exception as e:
        return f"ニュース検索エラー: {str(e)}"


def check_for_market_alerts(df) -> list:
    """
    Check for important market conditions and return alerts.
    
    Returns:
        List of alert dictionaries with 'type', 'message', 'severity'
    """
    alerts = []
    
    # VIX Alert
    if 'VIX' in df.columns:
        vix = df['VIX'].iloc[-1]
        if vix > 30:
            alerts.append({
                'type': 'VIX',
                'message': f"⚠️ VIXが{vix:.1f}に上昇 - 市場の恐怖が高まっています",
                'severity': 'high'
            })
        elif vix > 20:
            alerts.append({
                'type': 'VIX',
                'message': f"📊 VIXが{vix:.1f}に上昇 - 注意が必要です",
                'severity': 'medium'
            })
    
    # Reserves Alert
    if 'Reserves' in df.columns:
        reserves = df['Reserves'].iloc[-1]
        if reserves < 3000:  # Below $3T is concerning
            alerts.append({
                'type': 'Reserves',
                'message': f"⚠️ 銀行準備金が{reserves:.0f}Bに低下 - 流動性逼迫リスク",
                'severity': 'high'
            })
    
    # ON RRP Alert (depletion)
    if 'ON_RRP' in df.columns:
        on_rrp = df['ON_RRP'].iloc[-1]
        if on_rrp < 100:  # Below $100B is very low
            alerts.append({
                'type': 'ON_RRP',
                'message': f"🔴 ON RRPが{on_rrp:.0f}Bに枯渇 - 余剰流動性が消滅",
                'severity': 'high'
            })
    
    # Credit Spread Alert
    if 'Credit_Spread' in df.columns:
        spread = df['Credit_Spread'].iloc[-1]
        if spread > 5:
            alerts.append({
                'type': 'Credit_Spread',
                'message': f"⚠️ クレジットスプレッドが{spread:.2f}%に拡大 - 信用リスク上昇",
                'severity': 'high'
            })
    
    # Yield Curve Inversion
    if 'T10Y2Y' in df.columns:
        t10y2y = df['T10Y2Y'].iloc[-1]
        if t10y2y < 0:
            alerts.append({
                'type': 'Yield_Curve',
                'message': f"⚠️ イールドカーブ逆転中 ({t10y2y:.2f}%) - リセッション警告",
                'severity': 'medium'
            })
    
    # Primary Credit (Discount Window) Alert
    if 'Primary_Credit' in df.columns:
        primary = df['Primary_Credit'].iloc[-1]
        if primary > 10:  # Above $10B is unusual
            alerts.append({
                'type': 'Primary_Credit',
                'message': f"🔴 ディスカウントウィンドウ利用急増 ({primary:.0f}B) - 銀行流動性危機の兆候",
                'severity': 'high'
            })
    
    # RMP Alert
    if 'RMP_Alert_Active' in df.columns and df['RMP_Alert_Active'].iloc[-1]:
        rmp_text = df['RMP_Status_Text'].iloc[-1] if 'RMP_Status_Text' in df.columns else "RMP実行中"
        alerts.append({
            'type': 'RMP',
            'message': rmp_text,
            'severity': 'info'
        })
    
    return alerts


def fetch_agency_rss(agency_key: str) -> list:
    """
    Fetch RSS feed from a monitored agency.
    
    Args:
        agency_key: Key from MONITORED_AGENCIES dict
    
    Returns:
        List of entry dictionaries
    """
    if agency_key not in MONITORED_AGENCIES:
        return []
    
    agency = MONITORED_AGENCIES[agency_key]
    rss_url = agency.get('rss')
    
    if not rss_url:
        return []
    
    try:
        feed = feedparser.parse(rss_url)
        entries = []
        
        for entry in feed.entries[:10]:
            entries.append({
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': re.sub('<[^<]+?>', '', entry.get('summary', ''))[:300],
                'source': agency.get('label', agency_key)
            })
        
        return entries
    except:
        return []


def format_rss_entry(entry: dict) -> str:
    """Format a single RSS entry for display"""
    time_str = get_time_diff_str(entry.get('published', ''))
    title = entry.get('title', 'No Title')
    summary = entry.get('summary', '')[:200]
    link = entry.get('link', '')
    source = entry.get('source', 'Unknown')
    
    return f"""
**{title}**
⏰ {time_str} | 📰 {source}

{summary}...

[🔗 詳細を見る]({link})
"""
