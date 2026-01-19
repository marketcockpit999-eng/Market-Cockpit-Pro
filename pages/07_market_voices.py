# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 7: Market Voices
一次情報リンク集 - 判断はユーザーに委ねる
"""

import streamlit as st
import datetime
import re
import feedparser
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    t,
    RSS_FEEDS,
    get_time_diff_str,
)

# ========== PAGE CONTENT ==========
st.subheader(t('market_voices_title'))
st.caption(t('mv_subtitle'))

# =============================================================================
# 主要機関ダイレクトリンク
# =============================================================================
st.markdown(f"### {t('mv_direct_links')}")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **{t('mv_us')}**
    - [Federal Reserve](https://www.federalreserve.gov/)
    - [Fed - Speeches](https://www.federalreserve.gov/newsevents/speeches.htm)
    - [Fed - Press Releases](https://www.federalreserve.gov/newsevents/pressreleases.htm)
    - [FOMC Calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)
    - [Treasury](https://home.treasury.gov/news/press-releases)
    - [SEC](https://www.sec.gov/news)
    """)

with col2:
    st.markdown(f"""
    **{t('mv_overseas')}**
    - [{t('mv_ecb')}](https://www.ecb.europa.eu/press/html/index.en.html)
    - [{t('mv_boj')}](https://www.boj.or.jp/announcements/index.htm/)
    - [{t('mv_boe')}](https://www.bankofengland.co.uk/news)
    - [{t('mv_pboc')}](http://www.pbc.gov.cn/english/130721/index.html)
    - [BIS](https://www.bis.org/speeches/index.htm)
    - [IMF](https://www.imf.org/en/News)
    """)

st.markdown("---")

# =============================================================================
# RSS Feeds
# =============================================================================
st.markdown(f"### {t('mv_rss_feeds')}")

feed_tabs = st.tabs(list(RSS_FEEDS.keys()))

for idx, (name, url) in enumerate(RSS_FEEDS.items()):
    with feed_tabs[idx]:
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                st.caption(t('mv_no_articles'))
                continue
                
            for entry in feed.entries[:8]:
                time_str = get_time_diff_str(entry.get('published', ''))
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                
                st.markdown(f"**⏳ {time_str}** - [{title}]({link})")
                
        except Exception as e:
            st.caption(t('mv_error_feed'))

st.markdown("---")

# =============================================================================
# 情報源の信頼性ガイド
# =============================================================================
with st.expander(t('mv_guide_title'), expanded=False):
    st.markdown(t('mv_guide_content'))

# =============================================================================
# フッター
# =============================================================================
st.caption(t('mv_footer'))
