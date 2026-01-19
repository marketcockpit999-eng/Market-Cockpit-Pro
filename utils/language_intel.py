# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Fed Language Intelligence
FRB/Treasury発言の言葉を定量化・可視化

機能:
- 🦅 Tone Index: Hawkish/Dovish スコア (-100〜+100)
- ⚠️ Alert Words: Crisis, Pivot等の頻度
- 👻 消えた言葉: 急減したキーワードを検知
- 🌡️ 温度差: Fed vs Treasury の言葉の乖離
"""

import re
import csv
import os
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Tuple, Optional
import pandas as pd
import feedparser

# =============================================================================
# KEYWORD DICTIONARIES (キーワード辞書)
# =============================================================================

HAWKISH_WORDS = [
    # Core hawkish
    "inflation", "inflationary", "tightening", "restrictive",
    "higher for longer", "price stability", "above target",
    "overheating", "overheated", "hot", "strong labor",
    "rate hike", "raise rates", "further increases",
    "vigilant", "vigilance", "committed",
    # Quantitative
    "2% target", "inflation expectations", "wage pressure",
    "services inflation", "core inflation", "sticky",
]

DOVISH_WORDS = [
    # Core dovish  
    "cut", "cuts", "easing", "ease", "easier",
    "soft landing", "disinflation", "disinflationary",
    "slowdown", "slowing", "weakness", "weakening",
    "downside risk", "below target", "patient", "patience",
    "data dependent", "wait and see", "gradual",
    "pause", "pausing", "hold", "holding",
    "pivot", "turning point", "inflection",
    # Labor market
    "cooling", "rebalancing", "normalization",
]

CRISIS_WORDS = [
    # Financial stress
    "stress", "stresses", "instability", "unstable",
    "contagion", "spillover", "systemic",
    "bank run", "deposit flight", "liquidity crisis",
    "disorderly", "dysfunction", "breakdown",
    "fire sale", "forced selling",
    # Emergency
    "emergency", "facilities", "backstop",
    "intervention", "support", "stabilize",
]

PIVOT_WORDS = [
    # Transition signals
    "pause", "pausing", "skip",
    "data dependent", "meeting by meeting",
    "patient", "wait", "watching",
    "balanced", "two-sided", "both directions",
    "optionality", "flexibility", "nimble",
    "recalibrate", "recalibrating", "adjust",
]

# カテゴリ別辞書をまとめる
KEYWORD_CATEGORIES = {
    'hawkish': HAWKISH_WORDS,
    'dovish': DOVISH_WORDS,
    'crisis': CRISIS_WORDS,
    'pivot': PIVOT_WORDS,
}

# =============================================================================
# TEXT ANALYSIS FUNCTIONS
# =============================================================================

def count_keywords(text: str, keywords: List[str]) -> Dict[str, int]:
    """
    テキスト内のキーワード出現回数をカウント
    
    Args:
        text: 分析対象テキスト
        keywords: 検索キーワードリスト
    
    Returns:
        キーワードごとの出現回数 {keyword: count}
    """
    text_lower = text.lower()
    counts = {}
    for kw in keywords:
        # 単語境界を考慮してカウント（部分一致を防ぐ）
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            counts[kw] = len(matches)
    return counts


def calculate_tone_index(text: str) -> Tuple[float, Dict]:
    """
    Tone Index (Hawkish/Dovish スコア) を計算
    
    Returns:
        (tone_score, details)
        - tone_score: -100 (極めてDovish) 〜 +100 (極めてHawkish)
        - details: 内訳情報
    """
    hawkish_counts = count_keywords(text, HAWKISH_WORDS)
    dovish_counts = count_keywords(text, DOVISH_WORDS)
    
    hawkish_total = sum(hawkish_counts.values())
    dovish_total = sum(dovish_counts.values())
    total = hawkish_total + dovish_total
    
    if total == 0:
        return 0.0, {'hawkish': 0, 'dovish': 0, 'hawkish_words': {}, 'dovish_words': {}}
    
    # -100 to +100 スケール
    tone_score = ((hawkish_total - dovish_total) / total) * 100
    
    return tone_score, {
        'hawkish': hawkish_total,
        'dovish': dovish_total,
        'hawkish_words': hawkish_counts,
        'dovish_words': dovish_counts,
    }


def analyze_text_full(text: str, source: str = "Unknown") -> Dict:
    """
    テキストの完全分析
    
    Returns:
        全カテゴリの分析結果
    """
    tone_score, tone_details = calculate_tone_index(text)
    
    crisis_counts = count_keywords(text, CRISIS_WORDS)
    pivot_counts = count_keywords(text, PIVOT_WORDS)
    
    results = {
        'source': source,
        'timestamp': datetime.now().isoformat(),
        'word_count': len(text.split()),
        'tone_index': round(tone_score, 1),
        'hawkish_count': tone_details['hawkish'],
        'dovish_count': tone_details['dovish'],
        'crisis_count': sum(crisis_counts.values()),
        'pivot_count': sum(pivot_counts.values()),
        'top_hawkish': sorted(tone_details['hawkish_words'].items(), 
                             key=lambda x: x[1], reverse=True)[:5],
        'top_dovish': sorted(tone_details['dovish_words'].items(), 
                            key=lambda x: x[1], reverse=True)[:5],
        'top_crisis': sorted(crisis_counts.items(),
                            key=lambda x: x[1], reverse=True)[:5],
        'top_pivot': sorted(pivot_counts.items(),
                           key=lambda x: x[1], reverse=True)[:5],
    }
    
    return results


def get_tone_emoji(tone_index: float) -> str:
    """Tone Indexに応じた絵文字を返す"""
    if tone_index >= 50:
        return "🦅🦅"  # 極めてタカ派
    elif tone_index >= 20:
        return "🦅"    # タカ派
    elif tone_index <= -50:
        return "🕊️🕊️"  # 極めてハト派
    elif tone_index <= -20:
        return "🕊️"    # ハト派
    else:
        return "⚖️"    # 中立


def get_tone_color(tone_index: float) -> str:
    """Tone Indexに応じた色を返す (Streamlit用)"""
    if tone_index >= 20:
        return "#e74c3c"  # Red (Hawkish)
    elif tone_index <= -20:
        return "#3498db"  # Blue (Dovish)
    else:
        return "#95a5a6"  # Gray (Neutral)


# =============================================================================
# RSS FETCHING
# =============================================================================

FED_RSS_FEEDS = {
    'fed_speeches': {
        'url': 'https://www.federalreserve.gov/feeds/speeches.xml',
        'label': '🏛️ Fed Speeches',
        'org': 'fed',
    },
    'fed_press': {
        'url': 'https://www.federalreserve.gov/feeds/press_all.xml',
        'label': '🏛️ Fed Press',
        'org': 'fed',
    },
    'treasury': {
        'url': 'https://home.treasury.gov/news/press-releases/rss.xml',
        'label': '💵 Treasury',
        'org': 'treasury',
    },
}


def fetch_fed_content(days_back: int = 7) -> List[Dict]:
    """
    Fed/Treasury の最新コンテンツを取得
    
    Args:
        days_back: 何日前まで取得するか
    
    Returns:
        [{'title': ..., 'text': ..., 'source': ..., 'date': ..., 'org': ...}, ...]
    """
    cutoff = datetime.now() - timedelta(days=days_back)
    results = []
    
    for source_key, config in FED_RSS_FEEDS.items():
        try:
            feed = feedparser.parse(config['url'])
            for entry in feed.entries[:20]:  # 最新20件
                # 日付パース
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                
                if pub_date and pub_date < cutoff:
                    continue
                
                # テキスト抽出
                text = entry.get('summary', '') or entry.get('description', '')
                text = re.sub(r'<[^>]+>', '', text)  # HTMLタグ除去
                
                results.append({
                    'title': entry.get('title', 'No Title'),
                    'text': text,
                    'source': config['label'],
                    'source_key': source_key,
                    'org': config['org'],
                    'date': pub_date.isoformat() if pub_date else None,
                    'link': entry.get('link', ''),
                })
        except Exception as e:
            print(f"Error fetching {source_key}: {e}")
    
    return results


def fetch_and_analyze(days_back: int = 7) -> Dict:
    """
    RSS取得 + 全体分析を一括実行
    
    Returns:
        {
            'items': [...],           # 個別記事
            'fed_analysis': {...},    # Fed全体の分析
            'treasury_analysis': {...}, # Treasury全体の分析
            'temperature_diff': {...},  # 温度差
            'summary': {...},         # サマリー統計
        }
    """
    items = fetch_fed_content(days_back)
    
    if not items:
        return {
            'items': [],
            'fed_analysis': None,
            'treasury_analysis': None,
            'temperature_diff': None,
            'summary': {'total': 0},
        }
    
    # 組織別にテキストを分離
    fed_texts = [item['text'] for item in items if item['org'] == 'fed']
    treasury_texts = [item['text'] for item in items if item['org'] == 'treasury']
    
    # 個別分析
    for item in items:
        analysis = analyze_text_full(item['text'], item['source'])
        item['analysis'] = analysis
    
    # 組織別の全体分析
    fed_combined = ' '.join(fed_texts)
    treasury_combined = ' '.join(treasury_texts)
    
    fed_analysis = analyze_text_full(fed_combined, 'Fed (Combined)') if fed_texts else None
    treasury_analysis = analyze_text_full(treasury_combined, 'Treasury (Combined)') if treasury_texts else None
    
    # 温度差計算
    temp_diff = calculate_temperature_diff(fed_texts, treasury_texts) if fed_texts and treasury_texts else None
    
    return {
        'items': items,
        'fed_analysis': fed_analysis,
        'treasury_analysis': treasury_analysis,
        'temperature_diff': temp_diff,
        'summary': {
            'total': len(items),
            'fed_count': len(fed_texts),
            'treasury_count': len(treasury_texts),
            'fetch_date': datetime.now().isoformat(),
        },
    }


# =============================================================================
# HISTORICAL DATA MANAGEMENT (CSV)
# =============================================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
HISTORY_FILE = os.path.join(DATA_DIR, 'fed_language_history.csv')

HISTORY_COLUMNS = [
    'date', 'source', 'tone_index', 'hawkish_count', 'dovish_count',
    'crisis_count', 'pivot_count', 'word_count',
]


def save_analysis_to_history(analysis: Dict) -> bool:
    """分析結果をCSVに追記"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        
        file_exists = os.path.exists(HISTORY_FILE)
        
        with open(HISTORY_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=HISTORY_COLUMNS)
            if not file_exists:
                writer.writeheader()
            
            row = {
                'date': analysis.get('timestamp', datetime.now().isoformat())[:10],
                'source': analysis.get('source', 'unknown'),
                'tone_index': analysis.get('tone_index', 0),
                'hawkish_count': analysis.get('hawkish_count', 0),
                'dovish_count': analysis.get('dovish_count', 0),
                'crisis_count': analysis.get('crisis_count', 0),
                'pivot_count': analysis.get('pivot_count', 0),
                'word_count': analysis.get('word_count', 0),
            }
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error saving to history: {e}")
        return False


def load_history(days: int = 90) -> pd.DataFrame:
    """履歴データを読み込み"""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=HISTORY_COLUMNS)
    
    try:
        df = pd.read_csv(HISTORY_FILE)
        df['date'] = pd.to_datetime(df['date'])
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df['date'] >= cutoff]
        return df.sort_values('date')
    except Exception as e:
        print(f"Error loading history: {e}")
        return pd.DataFrame(columns=HISTORY_COLUMNS)


def get_history_summary(days: int = 30) -> Dict:
    """履歴の統計サマリーを取得"""
    df = load_history(days)
    
    if df.empty:
        return {
            'has_data': False,
            'days': days,
        }
    
    return {
        'has_data': True,
        'days': days,
        'record_count': len(df),
        'avg_tone': round(df['tone_index'].mean(), 1),
        'max_tone': round(df['tone_index'].max(), 1),
        'min_tone': round(df['tone_index'].min(), 1),
        'total_crisis_words': int(df['crisis_count'].sum()),
        'total_pivot_words': int(df['pivot_count'].sum()),
        'date_range': f"{df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}",
    }


# =============================================================================
# DISAPPEARED WORDS DETECTION (消えた言葉)
# =============================================================================

def detect_disappeared_words(
    recent_texts: List[str], 
    older_texts: List[str],
    min_old_count: int = 3,
    threshold_ratio: float = 0.3
) -> List[Tuple[str, int, int, float]]:
    """
    消えた言葉を検知
    
    Args:
        recent_texts: 直近のテキストリスト
        older_texts: 過去のテキストリスト
        min_old_count: 過去に最低何回出現していたか
        threshold_ratio: 現在/過去 がこの比率以下なら「消えた」
    
    Returns:
        [(word, old_count, new_count, ratio), ...]
    """
    all_keywords = []
    for category in KEYWORD_CATEGORIES.values():
        all_keywords.extend(category)
    all_keywords = list(set(all_keywords))  # 重複除去
    
    # 過去のカウント
    old_text_combined = ' '.join(older_texts)
    old_counts = count_keywords(old_text_combined, all_keywords)
    
    # 直近のカウント
    recent_text_combined = ' '.join(recent_texts)
    recent_counts = count_keywords(recent_text_combined, all_keywords)
    
    disappeared = []
    for word, old_count in old_counts.items():
        if old_count < min_old_count:
            continue
        new_count = recent_counts.get(word, 0)
        ratio = new_count / old_count
        if ratio <= threshold_ratio:
            disappeared.append((word, old_count, new_count, ratio))
    
    # 減少率でソート (ratio昇順 = 減少が大きい順)
    disappeared.sort(key=lambda x: x[3])
    
    return disappeared[:10]


def detect_emerging_words(
    recent_texts: List[str], 
    older_texts: List[str],
    min_new_count: int = 3,
    threshold_ratio: float = 3.0
) -> List[Tuple[str, int, int, float]]:
    """
    急増した言葉を検知
    
    Args:
        recent_texts: 直近のテキストリスト
        older_texts: 過去のテキストリスト
        min_new_count: 直近に最低何回出現しているか
        threshold_ratio: 現在/過去 がこの比率以上なら「急増」
    
    Returns:
        [(word, old_count, new_count, ratio), ...]
    """
    all_keywords = []
    for category in KEYWORD_CATEGORIES.values():
        all_keywords.extend(category)
    all_keywords = list(set(all_keywords))
    
    old_text_combined = ' '.join(older_texts)
    old_counts = count_keywords(old_text_combined, all_keywords)
    
    recent_text_combined = ' '.join(recent_texts)
    recent_counts = count_keywords(recent_text_combined, all_keywords)
    
    emerging = []
    for word, new_count in recent_counts.items():
        if new_count < min_new_count:
            continue
        old_count = old_counts.get(word, 0)
        if old_count == 0:
            ratio = float('inf')  # 新出
        else:
            ratio = new_count / old_count
        
        if ratio >= threshold_ratio:
            emerging.append((word, old_count, new_count, ratio))
    
    # 増加率でソート (ratio降順 = 増加が大きい順)
    emerging.sort(key=lambda x: x[3], reverse=True)
    
    return emerging[:10]


# =============================================================================
# TEMPERATURE DIFFERENCE (温度差: Fed vs Treasury)
# =============================================================================

def calculate_temperature_diff(
    fed_texts: List[str], 
    treasury_texts: List[str]
) -> Dict:
    """
    Fed vs Treasury の言葉の温度差を計算
    
    Returns:
        {
            'fed_tone': float,
            'treasury_tone': float,
            'diff': float,  # Fed - Treasury
            'interpretation': str,
            'emoji': str,
        }
    """
    fed_combined = ' '.join(fed_texts) if fed_texts else ''
    treasury_combined = ' '.join(treasury_texts) if treasury_texts else ''
    
    fed_tone, _ = calculate_tone_index(fed_combined)
    treasury_tone, _ = calculate_tone_index(treasury_combined)
    
    diff = fed_tone - treasury_tone
    
    # 解釈
    if diff > 30:
        interp = "Fedが財務省より大幅にタカ派"
        emoji = "🦅⬆️"
    elif diff > 10:
        interp = "Fedがやや タカ派寄り"
        emoji = "🦅"
    elif diff < -30:
        interp = "財務省がFedより大幅にタカ派"
        emoji = "💵⬆️"
    elif diff < -10:
        interp = "財務省がやや タカ派寄り"
        emoji = "💵"
    else:
        interp = "Fed/財務省は概ね同調"
        emoji = "⚖️"
    
    return {
        'fed_tone': round(fed_tone, 1),
        'treasury_tone': round(treasury_tone, 1),
        'diff': round(diff, 1),
        'interpretation': interp,
        'emoji': emoji,
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_keyword_list(items: List[Tuple[str, int]], max_items: int = 5) -> str:
    """キーワードリストを表示用にフォーマット"""
    if not items:
        return "（なし）"
    return ", ".join([f"{word}({count})" for word, count in items[:max_items]])


def get_category_for_word(word: str) -> Optional[str]:
    """キーワードがどのカテゴリに属するか返す"""
    for category, words in KEYWORD_CATEGORIES.items():
        if word.lower() in [w.lower() for w in words]:
            return category
    return None
