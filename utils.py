# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Unified Utils Module
設定、データ取得、表示関数を統合
"""

import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser
import os
import requests
import re
import json
import uuid
import pickle
import time
from io import StringIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ========== API KEYS & SETTINGS ==========
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
PAGE_TITLE = "Market Cockpit Pro"
MANUAL_DATA_FILE = "manual_h41_data.csv"

# AI Model Names
GEMINI_MODEL = "gemini-3-flash-preview"
CLAUDE_MODEL = "claude-opus-4-5-20251101"

# ========== DATA FRESHNESS MONITORING ==========
DATA_FRESHNESS_RULES = {
    'daily': {
        'fresh': 3, 'stale': 7, 'critical': 14,
        'indicators': ['EFFR', 'IORB', 'SOFR', 'SP500', 'VIX', 'HYG', 'DXY', 'USDJPY', 
                      'EURUSD', 'USDCNY', 'Gold', 'Silver', 'Oil', 'Copper', 'BTC', 'ETH',
                      'Credit_Spread', 'US_TNX', 'T10Y2Y', 'ON_RRP', 'FedFundsUpper', 'FedFundsLower']
    },
    'weekly': {
        'fresh': 10, 'stale': 14, 'critical': 21,
        'indicators': ['Reserves', 'TGA', 'Fed_Assets', 'SOMA_Total', 'SOMA_Bills', 
                      'SRF', 'FIMA', 'Primary_Credit', 'Total_Loans', 'Bank_Cash', 'ICSA',
                      'Net_Liquidity', 'SomaBillsRatio', 'CRE_Loans']
    },
    'monthly': {
        'fresh': 45, 'stale': 60, 'critical': 90,
        'indicators': ['M2SL', 'M2REAL', 'CPI', 'CPICore', 'PPI', 'Unemployment', 'UNRATE', 'CorePCE', 
                      'ConsumerSent', 'CN_M2', 'JP_M2', 'EU_M2', 'NFP', 'ADP', 'AvgHourlyEarnings', 'JOLTS',
                      'RetailSales', 'CN_CPI', 'JP_CPI', 'EU_CPI', 'US_Real_M2_Index', 'CI_Loans']
    },
    'quarterly': {
        'fresh': 100, 'stale': 120, 'critical': 150,
        'indicators': ['Lending_Standards', 'CI_Std_Large', 'CI_Std_Small', 'CI_Demand',
                      'CRE_Std_Construction', 'CRE_Std_Office', 'CRE_Std_Multifamily', 'CRE_Demand', 'RealGDP']
    }
}

# ========== DATA FREQUENCY LABELS ==========
DATA_FREQUENCY = {
    'EFFR': '日次', 'IORB': '日次', 'SOFR': '日次', 'SP500': '日次', 'VIX': '日次', 
    'HYG': '日次', 'DXY': '日次', 'USDJPY': '日次', 'EURUSD': '日次', 'USDCNY': '日次',
    'Gold': '日次', 'Silver': '日次', 'Oil': '日次', 'Copper': '日次', 'BTC': '日次', 'ETH': '日次',
    'Credit_Spread': '日次', 'US_TNX': '日次', 'T10Y2Y': '日次', 'ON_RRP': '日次',
    'FedFundsUpper': '日次', 'FedFundsLower': '日次',
    'Reserves': '週次', 'TGA': '週次', 'Fed_Assets': '週次', 'SOMA_Total': '週次', 'SOMA_Bills': '週次',
    'SRF': '週次', 'FIMA': '週次', 'Primary_Credit': '週次', 'Total_Loans': '週次', 
    'Bank_Cash': '週次', 'ICSA': '週次', 'Net_Liquidity': '週次', 'SomaBillsRatio': '週次',
    'M2SL': '月次', 'M2REAL': '月次', 'CPI': '月次', 'CPICore': '月次', 'PPI': '月次', 
    'Unemployment': '月次', 'UNRATE': '月次', 'CorePCE': '月次', 'ConsumerSent': '月次', 
    'CN_M2': '月次', 'JP_M2': '月次', 'EU_M2': '月次', 'CN_CPI': '月次', 'JP_CPI': '月次', 
    'EU_CPI': '月次', 'US_Real_M2_Index': '月次', 'NFP': '月次', 'ADP': '月次',
    'AvgHourlyEarnings': '月次', 'JOLTS': '月次', 'RetailSales': '月次', 'CI_Loans': '月次',
    'Lending_Standards': '四半期', 'RealGDP': '四半期',
    'CI_Std_Large': '四半期', 'CI_Std_Small': '四半期', 'CI_Demand': '四半期',
    'CRE_Std_Construction': '四半期', 'CRE_Std_Office': '四半期', 
    'CRE_Std_Multifamily': '四半期', 'CRE_Demand': '四半期', 'CRE_Loans': '週次',
}

# ========== FRED INDICATORS MAPPING ==========
FRED_INDICATORS = {
    'ON_RRP': 'RRPONTSYD', 'Reserves': 'WRESBAL', 'TGA': 'WTREGEN',
    'Fed_Assets': 'WALCL', 'SOMA_Total': 'WALCL', 'SOMA_Bills': 'TREAST',
    'EFFR': 'EFFR', 'IORB': 'IORB',
    'Bank_Cash': 'CASACBW027SBOG', 'Lending_Standards': 'DRTSCILM',
    'CI_Std_Large': 'DRTSCILM', 'CI_Std_Small': 'DRTSCIS', 'CI_Demand': 'DRTSCLCC', 'CI_Loans': 'BUSLOANS',
    'CRE_Std_Construction': 'SUBLPDRCSC', 'CRE_Std_Office': 'DRTSSP', 
    'CRE_Std_Multifamily': 'DRTSSP', 'CRE_Demand': 'DRTSCLCC', 'CRE_Loans': 'CREACBW027SBOG',
    'SRF': 'WORAL', 'FIMA': 'H41RESPPALGTRFNWW', 'SOFR': 'SOFR',
    'Primary_Credit': 'WLCFLPCL', 'Total_Loans': 'WLCFLL',
    'Credit_Spread': 'BAMLH0A0HYM2', 'US_TNX': 'DGS10',
    'Unemployment': 'UNRATE', 'CPI': 'CPIAUCSL', 'M2SL': 'M2SL', 'M2REAL': 'M2REAL',
    'CN_M2': 'MYAGM2CNM189N', 'JP_M2': 'MANMM101JPM189S', 'EU_M2': 'MABMM301EZM189S',
    'CN_CPI': 'CHNCPIALLMINMEI', 'JP_CPI': 'JPNCPIALLMINMEI', 'EU_CPI': 'CP0000EZ19M086NEST',
    'T10Y2Y': 'T10Y2Y', 'ICSA': 'ICSA', 'UNRATE': 'UNRATE',
    'CorePCE': 'PCETRIM12M159SFRBDAL', 'ConsumerSent': 'UMCSENT',
    'FedFundsUpper': 'DFEDTARU', 'FedFundsLower': 'DFEDTAR',
    'NFP': 'PAYEMS', 'ADP': 'ADPWNUSNERSA', 'AvgHourlyEarnings': 'CES0500000003', 'JOLTS': 'JTSJOL',
    'CPICore': 'CPILFESL', 'PPI': 'PPIACO', 'RetailSales': 'RSAFS', 'RealGDP': 'GDPC1',
}

# ========== YAHOO FINANCE INDICATORS ==========
YAHOO_INDICATORS = {
    'SP500': '^GSPC', 'VIX': '^VIX', 'HYG': 'HYG',
    'DXY': 'DX-Y.NYB', 'USDJPY': 'JPY=X', 'EURUSD': 'EURUSD=X', 'USDCNY': 'CNY=X',
    'Gold': 'GC=F', 'Silver': 'SI=F', 'Oil': 'CL=F', 'Copper': 'HG=F',
    'BTC': 'BTC-USD', 'ETH': 'ETH-USD',
}

# ========== EXPLANATIONS (67項目の詳細説明) ==========
EXPLANATIONS = {
    # === H.4.1 / Fed Balance Sheet ===
    "Net_Liquidity": "【ネットリクイディティ】\n市場に出回る「真の資金量」。(FRB総資産 - TGA - RRP) で計算されます。株式市場と強い相関があり、増加は株高、減少は株安を示唆。",
    "Reserves": "【銀行準備預金】\n民間銀行がFRBに預けているお金。これが減りすぎるとショックが起きやすくなります。「潤沢（ample）」レベルの維持がFRBの目標。",
    "TGA": "【TGA (財務省一般口座)】\n政府の銀行口座。ここが増えると市場から資金が吸い上げられます。財政支出時に放出され、市場に流動性を供給。",
    "ON_RRP": "【ON RRP (翌日物リバースレポ)】\nMMFなどがFRBにお金を預ける場所。余剰資金の滞留を示します。ゼロに近づくと「流動性の緩衝材」がなくなり、市場ストレスが高まりやすい。",
    "Fed_Assets": "【FRB総資産】\nFRBのバランスシート規模。QEで拡大、QTで縮小。市場流動性の根幹。",
    "SOMA_Total": "【SOMA総資産】\nFRBが保有する国債やMBSの総額。これが増える=QE（量的緩和）、減る=QT（量的引き締め）です。",
    "SOMA_Bills": "【SOMA Bills (短期国債)】\nFRBが保有する短期国債（T-Bills）。2025年12月12日からRMP（Reserve Management Purchases）として月額400億ドルペースで買い入れ中。QT終了後の準備金維持が目的だが、実質的な資金供給となる。",
    "SomaBillsRatio": "【SOMA Bills比率】\nFRBの総資産に占める短期国債の割合。RMP実行により上昇トレンドとなる。FRBは「技術的措置」と主張するが、市場への流動性供給効果はQEに類似。",
    
    # === Market Plumbing / Repo ===
    "SRF": "【Standing Repo Facility】\n国内の金融機関が国債を担保に現金を借りる常設窓口。リポ市場の目詰まりを検知します。利用増加は短期金融市場のストレス上昇を示唆。",
    "FIMA": "【FIMA Repo Facility】\n海外の中央銀行向け融資。世界的なドル不足が発生しているかを測る指標です。新興国の通貨危機やドル流動性危機の先行指標。",
    "Primary_Credit": "【Primary Credit (一次信用)】\n健全な銀行向けの緊急融資。急増時は銀行が市場で現金を調達できなくなっている危険信号です。2023年SVB危機時に急増。",
    "Total_Loans": "【Total Loans (融資総額)】\nFRBによる金融機関への貸出総額。市場の緊急事態を測る総合指標です。ディスカウントウィンドウの利用状況を示す。",
    "Primary": "【Primary Credit】\n健全な銀行向けの緊急融資。急増時は銀行が市場で現金を調達できなくなっている危険信号です。",
    "Window": "【Total Loans】\nFRBによる金融機関への貸出総額。市場の緊急事態を測る総合指標です。",
    
    # === Rates / 金利 ===
    "EFFR": "【EFFR (実効FF金利)】\n銀行間の翌日物貸借金利の加重平均。FRBの政策金利（FF金利）がどれだけ実際に効いているかを示す。IORB付近で推移するのが正常。",
    "IORB": "【IORB (準備預金付利)】\nFRBが銀行の準備預金に付与する金利。EFFRの「天井」として機能。EFFRがIORBを大きく下回ると金融環境の緩み、上回ると引き締まりを示唆。",
    "SOFR": "【SOFR (担保付翌日物金利)】\n国債を担保にした資金調達コスト。LIBORに代わる新たな基準金利。急騰は現金不足（リポ市場のストレス）を示します。",
    "FedFundsUpper": "【FF金利上限】\nFRBが設定するフェデラルファンド金利の誘導目標上限。",
    "FedFundsLower": "【FF金利下限】\nFRBが設定するフェデラルファンド金利の誘導目標下限。",
    "US_TNX": "【米国10年債利回り】\n長期金利の指標。住宅ローンや企業借入コストに影響。景気期待・インフレ期待を反映。",
    "T10Y2Y": "【2年-10年スプレッド（イールドカーブ）】\n逆イールド（マイナス）はリセッションの強力な先行指標。正常化（プラス転換）後の景気後退に注意。",
    "Credit_Spread": "【ハイイールドスプレッド】\nジャンク債と国債の金利差。信用リスクのバロメーター。拡大は信用収縮、縮小はリスクオン。",
    
    # === Banking Sector / 銀行セクター ===
    "Bank_Cash": "【銀行の現金保有】\n全米の銀行が保有する現金資産の推移。銀行が不安を感じて現金を抱え込み始めると市場の流動性が低下します。危機の先行指標。",
    "Lending_Standards": "【C&I Lending Tightening / 商工業融資基準の厳格化】\n銀行の融資態度を示す純割合（Net %）。0が中立、+は引き締め（融資基準を厳しくする銀行が多い）、−は緩和。数値上昇は信用収縮を示し、景気後退の先行指標として重要。",
    "VIX": "【VIX指数 (恐怖指数)】\nS&P500オプションから算出されるボラティリティ指数。20以上で市場の不安が高まっている状態。30超は恐怖、12以下は過度の楽観。",
    
    # === SLOOS - C&I Lending (商工業融資) ===
    "CI_Std_Large": "【C&I融資基準（大・中堅企業）】\n0を超えると貸し渋り。40%超で強力なリセッションシグナル。リセッションの先行指標（20%超で警戒）。",
    "CI_Std_Small": "【C&I融資基準（小企業）】\n中小企業の資金繰りと雇用の先行指標。小企業向けが先に悪化する場合は雇用悪化に注意。中小企業は景気に敏感。",
    "CI_Demand": "【C&I融資需要（大・中堅企業）】\n企業の設備投資意欲を測定。基準が緩んでも需要が低い場合は企業が将来を悲観。基準と需要の「乖離」が最大の注目点。",
    "CI_Loans": "【C&I融資残高】\n商工業向け融資の総額。融資基準厳格化後にこの残高が減少すると「クレジットクランチ（信用収縮）」開始のサイン。",
    
    # === SLOOS - CRE Lending (商業用不動産融資) ===
    "CRE_Std_Construction": "【CRE融資基準（建設・土地開発）】\n不動産開発の蛇口。ここが閉まると数年後の新規供給と建設投資が止まる。先行性が高い。",
    "CRE_Std_Office": "【CRE融資基準（オフィス等）】\n既存物件の借り換え難易度を示す。厳格化は物件価格暴落のトリガーとなる。オフィスクライシス・借り換えリスクの測定。",
    "CRE_Std_Multifamily": "【CRE融資基準（集合住宅）】\n居住用不動産市場の流動性を確認。住宅供給に影響。賃貸市場の先行指標。",
    "CRE_Demand": "【CRE融資需要】\n投資家が不動産から資金を引き揚げる動きを察知する指標。不動産投資意欲の減退確認。",
    "CRE_Loans": "【CRE融資残高（週次）】\n週次で追える最速のデータ。四半期統計を待たずに銀行の融資姿勢の変化をリアルタイムで察知。",
    
    # === Money Supply / マネーサプライ ===
    "M2SL": "【通貨供給量 M2 (名目)】\n世の中に流通しているマネー(現金・預金等)の総量。FRBの金融政策の結果を示す。",
    "M2REAL": "【通貨供給量 M2 (実質)】\nインフレ調整後の実質的な購買力。名目M2よりも実体経済への影響を測定。",
    "US_Real_M2_Index": "【米国実質M2指数】\nインフレ調整後のM2の推移を指数化したもの。",
    "CN_M2": "【中国M2】\n中国の通貨供給量。世界第2位の経済大国の流動性状況を示す。",
    "JP_M2": "【日本M2】\n日本の通貨供給量。日銀の金融政策の結果を反映。",
    "EU_M2": "【欧州M2】\nユーロ圏の通貨供給量。ECBの金融政策の結果を反映。",
    
    # === Economic Indicators / 経済指標 ===
    "Unemployment": "【失業率】\n労働市場の健全性を示す遅行指標。FRBのデュアルマンデートの一つ。",
    "UNRATE": "【失業率 (Sahm Rule用)】\nサーム・ルールの計算に使用。3ヶ月移動平均が12ヶ月最低値から0.5%上昇でリセッション入りのシグナル。",
    "CPI": "【消費者物価指数 (CPI)】\nインフレの主要指標。FRBの金融政策判断に直結。",
    "CPICore": "【コアCPI】\n食品・エネルギーを除いたCPI。基調的なインフレ傾向を示す。",
    "PPI": "【生産者物価指数 (PPI)】\n企業の仕入れコスト。CPIの先行指標となることも。",
    "CorePCE": "【コアPCE】\nFRBが最も重視するインフレ指標。2%が目標。",
    "ConsumerSent": "【消費者信頼感指数】\n消費者のマインド。個人消費（GDPの7割）の先行指標。",
    "NFP": "【非農業部門雇用者数 (NFP)】\n毎月第1金曜発表の最重要指標。労働市場の強さを示す。",
    "ADP": "【ADP雇用統計】\n民間調査会社による雇用統計。NFPの先行指標として注目。",
    "AvgHourlyEarnings": "【平均時給】\n賃金インフレの指標。NFPと同時発表。",
    "JOLTS": "【求人数 (JOLTS)】\n労働需要の強さを示す。求人/求職者比率も重要。",
    "ICSA": "【新規失業保険申請件数】\n週次で発表される最速の雇用指標。景気の先行指標。",
    "RetailSales": "【小売売上高】\n個人消費の動向を示す。GDPの先行指標。",
    "RealGDP": "【実質GDP】\n経済成長の最終指標。四半期ごとに発表。",
    
    # === FX / 為替 ===
    "DXY": "【ドル指数 (DXY)】\n主要通貨に対するドルの強さ。上昇はドル高、新興国・コモディティに逆風。",
    "USDJPY": "【ドル円】\n日米金利差に敏感。リスクオフ時は円高傾向。",
    "EURUSD": "【ユーロドル】\n世界最大の取引量を持つ通貨ペア。",
    "USDCNY": "【ドル人民元】\n米中関係と中国経済を反映。管理フロート制。",
    
    # === Commodities / コモディティ ===
    "Gold": "【金 (Gold)】\n安全資産・インフレヘッジ。実質金利と逆相関。",
    "Silver": "【銀 (Silver)】\n工業用途もあり、金よりボラティリティが高い。",
    "Oil": "【原油 (WTI)】\nエネルギー価格の指標。インフレ・景気に影響。",
    "Copper": "【銅】\n「ドクター・カッパー」と呼ばれる景気先行指標。",
    
    # === Crypto / 暗号資産 ===
    "BTC": "【ビットコイン (BTC)】\n暗号資産の代表。リスク資産と相関。",
    "ETH": "【イーサリアム (ETH)】\nスマートコントラクト・DeFiの基盤。",
    
    # === Market / 市場 ===
    "SP500": "【S&P 500】\n米国大型株500社の株価指数。米国経済のバロメーター。",
    "HYG": "【ハイイールド債ETF (HYG)】\nジャンク債市場の流動性と信用リスクを反映。",
}

# ========== RSS FEEDS ==========
RSS_FEEDS = {
    "🏛️ Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "🇪🇺 ECB": "https://www.ecb.europa.eu/rss/press.html",
    "🇯🇵 BOJ": "https://www.boj.or.jp/rss/news.xml",
}

MONITORED_AGENCIES = {
    "FRB": {"domain": "federalreserve.gov", "rss": "https://www.federalreserve.gov/feeds/press_all.xml", "label": "🏦 Federal Reserve"},
    "Treasury": {"domain": "treasury.gov", "rss": "https://home.treasury.gov/news/press-releases/rss.xml", "label": "💵 Treasury"},
}

# ========== CONTEXT KEYWORDS ==========
CONTEXT_KEYWORDS = {
    "🌐 地政学リスク (Geopolitics)": {"main_keyword": "geopolitical risk", "desc": "制裁・貿易戦争・軍事紛争"},
    "📊 マクロ経済 (Macro)": {"main_keyword": "recession risk", "desc": "景気後退・インフレ・GDP"},
    "🏛️ 中央銀行 (Central Bank)": {"main_keyword": "Fed policy", "desc": "利下げ・QT・バランスシート"},
    "💧 流動性・配管 (Liquidity/Plumbing)": {"main_keyword": "liquidity crisis", "desc": "レポ・準備金・ON RRP"},
    "🛢️ コモディティ (Commodities)": {"main_keyword": "oil price gold", "desc": "原油・金・銅・供給制約"},
    "₿ 仮想通貨 (Crypto)": {"main_keyword": "Bitcoin regulation", "desc": "BTC規制・ETF・ステーブルコイン"},
    "🏦 銀行・信用 (Banking/Credit)": {"main_keyword": "bank stress", "desc": "銀行破綻・信用収縮・CRE"},
    "🏢 不動産 (Real Estate)": {"main_keyword": "commercial real estate", "desc": "商業用不動産・オフィス空室"},
    "💵 通貨・為替 (Currency/FX)": {"main_keyword": "dollar strength", "desc": "ドル高・円安・介入"},
    "🇨🇳 中国 (China)": {"main_keyword": "China economy", "desc": "中国経済・不動産危機・資本流出"},
    "🇪🇺 欧州 (Europe)": {"main_keyword": "ECB policy", "desc": "ECB・エネルギー危機・債務"},
    "🌍 新興国 (Emerging Markets)": {"main_keyword": "emerging market crisis", "desc": "新興国危機・通貨暴落・IMF"},
}

# ========== HELPER FUNCTIONS ==========

def get_freshness_badge(last_updated_str: str) -> str:
    """データ鮮度バッジを返す"""
    if not last_updated_str:
        return ""
    try:
        last_updated = datetime.datetime.strptime(last_updated_str, '%Y-%m-%d')
        now = datetime.datetime.now()
        days_ago = (now - last_updated).days
        if days_ago <= 1:
            return "🆕"
        elif days_ago <= 7:
            return "✅"
        elif days_ago <= 30:
            return "⏳"
        else:
            return "⚠️"
    except:
        return ""

def get_data_freshness_status(last_valid_dates: dict, release_dates: dict = None) -> dict:
    """全指標のデータ鮮度をチェック"""
    today = datetime.datetime.now().date()
    
    results = {
        'fresh': [], 'stale': [], 'critical': [], 'missing': [],
        'details': {},
        'summary': {'fresh_count': 0, 'stale_count': 0, 'critical_count': 0, 'health_score': 100}
    }
    
    indicator_category = {}
    for category, config in DATA_FRESHNESS_RULES.items():
        for ind in config['indicators']:
            indicator_category[ind] = category
    
    for indicator, date_str in last_valid_dates.items():
        if indicator in ['RMP_Alert_Active', 'RMP_Status_Text']:
            continue
        try:
            check_date_str = date_str
            if release_dates and indicator in release_dates and release_dates[indicator]:
                check_date_str = release_dates[indicator]
            last_date = datetime.datetime.strptime(check_date_str, '%Y-%m-%d').date()
            days_old = (today - last_date).days
            
            category = indicator_category.get(indicator, 'weekly')
            rules = DATA_FRESHNESS_RULES[category]
            
            if days_old <= rules['fresh']:
                status = 'fresh'
                results['fresh'].append(indicator)
            elif days_old <= rules['stale']:
                status = 'stale'
                results['stale'].append(indicator)
            else:
                status = 'critical'
                results['critical'].append(indicator)
            
            results['details'][indicator] = {
                'last_date': date_str,
                'days_old': days_old,
                'status': status,
                'category': category
            }
        except:
            results['missing'].append(indicator)
    
    total = len(results['fresh']) + len(results['stale']) + len(results['critical'])
    if total > 0:
        results['summary']['fresh_count'] = len(results['fresh'])
        results['summary']['stale_count'] = len(results['stale'])
        results['summary']['critical_count'] = len(results['critical'])
        results['summary']['health_score'] = int((len(results['fresh']) / total) * 100)
    
    return results

# ========== AI CLIENT INITIALIZATION ==========
def init_ai_clients():
    """AI クライアントを初期化"""
    gemini_client = None
    claude_client = None
    
    try:
        from google import genai
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY:
            gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except:
        pass
    
    try:
        import anthropic
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        if ANTHROPIC_API_KEY:
            claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    except:
        pass
    
    return gemini_client, claude_client

# ========== MARKET DATA FUNCTIONS ==========

def _get_disk_cache_path():
    """ディスクキャッシュのパスを取得"""
    return os.path.join(os.path.dirname(__file__), '.market_data_cache.pkl')

def _load_from_disk_cache():
    """ディスクキャッシュから読み込み"""
    cache_path = _get_disk_cache_path()
    try:
        if os.path.exists(cache_path):
            cache_age = time.time() - os.path.getmtime(cache_path)
            if cache_age < 600:  # 10分以内
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
    except:
        pass
    return None, None

def _save_to_disk_cache(df, df_original):
    """ディスクキャッシュに保存"""
    cache_path = _get_disk_cache_path()
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump((df, df_original), f)
    except:
        pass

def get_fred_release_dates(series_ids: list) -> dict:
    """FRED APIからリリース日を取得"""
    release_info = {}
    for series_id in series_ids:
        try:
            url = f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'seriess' in data and len(data['seriess']) > 0:
                    series_info = data['seriess'][0]
                    release_info[series_id] = {
                        'last_updated': series_info.get('last_updated', '')[:10]
                    }
        except:
            pass
    return release_info

@st.cache_data(ttl=600, show_spinner=False)
def get_market_data(_csv_mtime=None, _force_refresh=False):
    """市場データを取得"""
    if not _force_refresh:
        cached_df, cached_original = _load_from_disk_cache()
        if cached_df is not None and cached_original is not None:
            return cached_df, cached_original
    
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=730)
    
    fred_series = []
    for name, ticker in FRED_INDICATORS.items():
        try:
            s = web.DataReader(ticker, 'fred', start, end, api_key=FRED_API_KEY)
            s.columns = [name]
            fred_series.append(s)
        except:
            pass
    
    # Yahoo Data
    try:
        y_tickers = list(YAHOO_INDICATORS.values())
        y_data = yf.download(y_tickers, start=start, end=end, progress=False)['Close']
        inv_yahoo = {v: k for k, v in YAHOO_INDICATORS.items()}
        y_data = y_data.rename(columns=inv_yahoo)
    except:
        y_data = pd.DataFrame()
    
    # Join All
    df = pd.concat(fred_series + ([y_data] if not y_data.empty else []), axis=1).sort_index()
    
    # Unit Normalization (Million to Billion)
    mil_to_bil = ['Fed_Assets', 'TGA', 'Reserves', 'SOMA_Total', 'Bank_Cash', 'SRF', 'FIMA', 
                  'Primary_Credit', 'Total_Loans', 'SOMA_Bills', 'M2SL', 'M2REAL', 'CI_Loans', 'CRE_Loans']
    for col in mil_to_bil:
        if col in df.columns:
            df[col] = df[col] / 1000
    
    # Calculate Net Liquidity
    if all(c in df.columns for c in ['Fed_Assets', 'TGA', 'ON_RRP']):
        df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['ON_RRP']
    
    # Calculate SOMA Bills Ratio
    if all(c in df.columns for c in ['SOMA_Bills', 'SOMA_Total']):
        df['SomaBillsRatio'] = (df['SOMA_Bills'] / df['SOMA_Total']) * 100
    
    # RMP Status
    if 'SOMA_Bills' in df.columns:
        df['RMP_Alert_Active'] = False
        df['RMP_Status_Text'] = "📊 RMP監視中"
        
        bills_recent = df['SOMA_Bills'].tail(30)
        if len(bills_recent) >= 7:
            bills_7d_ago = bills_recent.iloc[-7]
            bills_now = bills_recent.iloc[-1]
            weekly_change = bills_now - bills_7d_ago
            
            if weekly_change >= 4.5:
                df.loc[df.index[-1], 'RMP_Alert_Active'] = True
                df.loc[df.index[-1], 'RMP_Status_Text'] = f"✅ RMP実行中: +${weekly_change:.1f}B/週"
    
    # Store last valid dates
    last_valid_dates = {}
    for col in df.columns:
        valid_data = df[col].dropna()
        if len(valid_data) > 0:
            last_valid_dates[col] = valid_data.index[-1].strftime('%Y-%m-%d')
    
    # Fetch FRED release dates
    fred_ids = list(set(FRED_INDICATORS.values()))
    fred_release_info = get_fred_release_dates(fred_ids)
    
    col_release_dates = {}
    for indicator, series_id in FRED_INDICATORS.items():
        if series_id in fred_release_info:
            col_release_dates[indicator] = fred_release_info[series_id]['last_updated']
    
    df_original = df.copy()
    df = df.ffill()
    
    df.attrs['last_valid_dates'] = last_valid_dates
    df.attrs['fred_release_dates'] = col_release_dates
    df_original.attrs = df.attrs.copy()
    
    _save_to_disk_cache(df, df_original)
    
    return df, df_original

# ========== DISPLAY FUNCTIONS ==========

def show_metric(label, series, unit="", explanation_key="", notes="", alert_func=None):
    """シンプルなメトリック表示"""
    df = st.session_state.get('df')
    
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
        release_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        latest_date = None
        release_date = None
        col_name = series.name if hasattr(series, 'name') else explanation_key
        if df is not None and hasattr(df, 'attrs'):
            if 'last_valid_dates' in df.attrs and col_name in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][col_name]
            if 'fred_release_dates' in df.attrs and col_name in df.attrs['fred_release_dates']:
                release_date = df.attrs['fred_release_dates'][col_name]
    
    help_text = EXPLANATIONS.get(explanation_key, "")
    freshness_badge = get_freshness_badge(release_date or latest_date) if (release_date or latest_date) else ""
    display_label = f"{freshness_badge} {label}" if freshness_badge else label
    
    if alert_func and val is not None and alert_func(val):
        st.metric(display_label, f"{val:.1f} {unit}" if val is not None else "N/A", 
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(display_label, f"{val:.1f} {unit}" if val is not None else "N/A",
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text)
    
    if latest_date:
        freq_label = DATA_FREQUENCY.get(explanation_key, '')
        st.caption(f"📅 対象期間: {latest_date} ({freq_label})" if freq_label else f"📅 対象日: {latest_date}")
    
    if release_date:
        st.caption(f"🔄 提供元更新日: {release_date}")
    
    if notes:
        st.caption(notes)

def show_metric_with_sparkline(label, series, df_column, unit="", explanation_key="", notes="", alert_func=None, decimal_places=1):
    """メトリック + スパークライン（提供元更新日表示対応）"""
    df = st.session_state.get('df')
    
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
        release_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        latest_date = None
        release_date = None
        if df is not None and hasattr(df, 'attrs'):
            if 'last_valid_dates' in df.attrs and df_column in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][df_column]
            if 'fred_release_dates' in df.attrs and df_column in df.attrs['fred_release_dates']:
                release_date = df.attrs['fred_release_dates'][df_column]
    
    help_text = EXPLANATIONS.get(explanation_key or df_column, "")
    freshness_badge = get_freshness_badge(release_date or latest_date) if (release_date or latest_date) else ""
    display_label = f"{freshness_badge} {label}" if freshness_badge else label
    
    val_format = f"{{:.{decimal_places}f}}"
    delta_format = f"{{:+.{decimal_places}f}}"
    
    if alert_func and val is not None and alert_func(val):
        st.metric(display_label, f"{val_format.format(val)} {unit}" if val is not None else "N/A", 
                 delta=delta_format.format(delta) if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(display_label, f"{val_format.format(val)} {unit}" if val is not None else "N/A",
                 delta=delta_format.format(delta) if delta is not None else None,
                 help=help_text)
    
    # 📅 対象期間
    if latest_date:
        freq_label = DATA_FREQUENCY.get(df_column, '')
        st.caption(f"📅 対象期間: {latest_date} ({freq_label})" if freq_label else f"📅 対象日: {latest_date}")
    
    # 🔄 提供元更新日
    if release_date:
        st.caption(f"🔄 提供元更新日: {release_date}")
    
    if notes:
        st.caption(notes)
    
    # スパークライン
    if df is not None and df_column in df.columns and not df.get(df_column, pd.Series()).isna().all():
        recent_data = df[df_column].tail(60)
        st.caption("📊 過去60日間のトレンド")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recent_data.index,
            y=recent_data.values,
            mode='lines',
            line=dict(color='cyan', width=1),
            fill='tozeroy',
            fillcolor='rgba(0,255,255,0.1)',
            showlegend=False
        ))
        
        fig.update_layout(
            height=100,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode=False
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, 
                       key=f"spark_{df_column}_{uuid.uuid4().hex[:8]}")

def plot_dual_axis(df, left_col, right_col, left_name, right_name):
    """2軸チャート"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if left_col in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df[left_col], name=left_name, line=dict(color='cyan')),
            secondary_y=False
        )
    
    if right_col in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df[right_col], name=right_name, line=dict(color='orange')),
            secondary_y=True
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    fig.update_yaxes(title_text=left_name, secondary_y=False)
    fig.update_yaxes(title_text=right_name, secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True, key=f"dual_{uuid.uuid4().hex[:8]}")

def plot_soma_composition(df):
    """SOMA構成チャート"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'SOMA_Total' in df.columns:
        soma_resampled = df['SOMA_Total'].resample('W').last()
        fig.add_trace(
            go.Bar(x=soma_resampled.index, y=soma_resampled, name='SOMA Total (Billions)', marker_color='steelblue'),
            secondary_y=False
        )
    
    if 'SomaBillsRatio' in df.columns:
        ratio_resampled = df['SomaBillsRatio'].resample('W').last()
        fig.add_trace(
            go.Scatter(x=ratio_resampled.index, y=ratio_resampled, name='Bills Ratio (%)', 
                      line=dict(color='orange', width=2)),
            secondary_y=True
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    fig.update_yaxes(title_text="SOMA Total (B)", secondary_y=False)
    fig.update_yaxes(title_text="Bills Ratio (%)", secondary_y=True, tickformat='.1f')
    
    st.plotly_chart(fig, use_container_width=True, key=f"soma_{uuid.uuid4().hex[:8]}")

# ========== VALUATION & LEVERAGE INDICATORS ==========
@st.cache_data(ttl=3600, show_spinner=False)
def get_pe_ratios():
    """S&P500とNASDAQのP/Eを取得"""
    try:
        result = {
            'sp500_pe': None,
            'sp500_pe_avg': 19.5,
            'nasdaq_pe': None,
        }
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = "https://www.multpl.com/s-p-500-pe-ratio"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                match = re.search(r'Current S&P 500 PE Ratio is\s*([\d.]+)', response.text)
                if match:
                    result['sp500_pe'] = float(match.group(1))
        except:
            pass
        
        try:
            qqq = yf.Ticker("QQQ")
            info = qqq.info
            result['nasdaq_pe'] = info.get('trailingPE')
        except:
            pass
        
        return result
    except:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def get_crypto_leverage_data():
    """暗号資産レバレッジ指標を取得"""
    try:
        result = {
            'btc_funding_rate': None,
            'eth_funding_rate': None,
            'btc_open_interest': None,
            'eth_open_interest': None,
            'btc_long_short_ratio': None,
        }
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Binance Funding Rate
        try:
            url = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result['btc_funding_rate'] = float(data[0].get('fundingRate', 0)) * 100
        except:
            pass
        
        try:
            url = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=ETHUSDT&limit=1"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result['eth_funding_rate'] = float(data[0].get('fundingRate', 0)) * 100
        except:
            pass
        
        # Open Interest
        try:
            url = "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result['btc_open_interest'] = float(data.get('openInterest', 0))
        except:
            pass
        
        try:
            url = "https://fapi.binance.com/fapi/v1/openInterest?symbol=ETHUSDT"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result['eth_open_interest'] = float(data.get('openInterest', 0))
        except:
            pass
        
        # Historical OI (30 days)
        try:
            url = "https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=4h&limit=180"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    oi_values = [float(d.get('sumOpenInterest', 0)) for d in data]
                    result['btc_oi_avg_30d'] = sum(oi_values) / len(oi_values) if oi_values else None
                    result['btc_oi_ath'] = max(oi_values) if oi_values else None
        except:
            pass
        
        try:
            url = "https://fapi.binance.com/futures/data/openInterestHist?symbol=ETHUSDT&period=4h&limit=180"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    oi_values = [float(d.get('sumOpenInterest', 0)) for d in data]
                    result['eth_oi_avg_30d'] = sum(oi_values) / len(oi_values) if oi_values else None
                    result['eth_oi_ath'] = max(oi_values) if oi_values else None
        except:
            pass
        
        # Long/Short Ratio
        try:
            url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=1"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result['btc_long_short_ratio'] = float(data[0].get('longShortRatio', 1.0))
        except:
            pass
        
        return result
    except:
        return None

# ========== ALERT FUNCTIONS ==========
def check_for_market_alerts(df=None):
    """市場アラートをチェック"""
    alerts = []
    
    if df is None:
        df = st.session_state.get('df')
    
    if df is None:
        return alerts
    
    # VIX Alert
    if 'VIX' in df.columns:
        vix = df['VIX'].iloc[-1]
        if vix > 30:
            alerts.append({'severity': 'high', 'message': f'🔴 VIX高騰: {vix:.1f}'})
        elif vix > 25:
            alerts.append({'severity': 'medium', 'message': f'🟠 VIX上昇: {vix:.1f}'})
    
    # Credit Spread Alert
    if 'Credit_Spread' in df.columns:
        spread = df['Credit_Spread'].iloc[-1]
        if spread > 5:
            alerts.append({'severity': 'high', 'message': f'🔴 クレジットスプレッド拡大: {spread:.2f}%'})
    
    # ON RRP Alert
    if 'ON_RRP' in df.columns:
        rrp = df['ON_RRP'].iloc[-1]
        if rrp < 50:
            alerts.append({'severity': 'medium', 'message': f'🟠 ON RRP低下: ${rrp:.0f}B'})
    
    return alerts

# ========== MACRO INDICATOR FUNCTIONS ==========

def get_mom_yoy(df_column, freq='M'):
    """MoM%とYoY%を計算（オリジナルデータを使用）"""
    df_original = st.session_state.get('df_original')
    if df_original is None:
        return None, None
    
    series = df_original.get(df_column)
    if series is None or len(series.dropna()) < 2:
        return None, None
    s = series.dropna()
    curr = s.iloc[-1]
    prev = s.iloc[-2]
    mom = (curr / prev - 1) * 100 if prev != 0 else 0
    
    # YoY: Monthly=12, Quarterly=4
    offset = 12 if freq == 'M' else 4
    yoy = None
    if len(s) > offset:
        prev_yr = s.iloc[-(offset+1)]
        yoy = (curr / prev_yr - 1) * 100 if prev_yr != 0 else 0
    return mom, yoy

def display_macro_card(title, series, df_column, unit="", notes="", freq='M', show_level=True):
    """マクロ指標カードを表示（MoM, YoY, スパークライン、長期チャート）
    
    Args:
        show_level: FalseならスパークラインやLevel表示をスキップ（NFPのように変化のみが重要な場合）
    """
    df = st.session_state.get('df')
    df_original = st.session_state.get('df_original')
    
    st.markdown(f"#### {title}")
    mom, yoy = get_mom_yoy(df_column, freq=freq)
    
    # 1. Metrics Row (MoM, YoY)
    m_col1, m_col2 = st.columns(2)
    if mom is not None:
        m_col1.metric("前月比", f"{mom:+.1f}%")
    if yoy is not None:
        m_col2.metric("前年比", f"{yoy:+.1f}%")
    
    # 2. Main Metric with Sparkline & Update Date (optional)
    if show_level:
        show_metric_with_sparkline(title, series, df_column, unit, notes=notes)
    
    # 3. YoY% Trend Chart
    if df_original is not None:
        original_series = df_original.get(df_column)
        if original_series is not None and len(original_series.dropna()) > 12:
            data = original_series.dropna()
            yoy_series = (data / data.shift(12) - 1) * 100
            yoy_series = yoy_series.dropna()
            if len(yoy_series) > 0:
                st.markdown(f"###### {title} YoY% (前年比変化率)")
                st.line_chart(yoy_series, height=120)
    
    # 4. Long-term Chart (Level)
    if series is not None and not series.isna().all():
        st.markdown(f"###### {title} Long-term Trend (Level)")
        st.line_chart(series, height=150)

# ========== CRYPTO LIQUIDITY FUNCTIONS ==========

@st.cache_data(ttl=3600, show_spinner=False)
def get_stablecoin_data():
    """ステーブルコインデータを取得（DeFiLlama API）"""
    try:
        url = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        stablecoins = data.get('peggedAssets', [])
        
        top_coins = []
        total_supply = 0
        coin_ids = {}
        
        for coin in stablecoins:
            if coin.get('pegType') == 'peggedUSD':
                circulating = coin.get('circulating', {}).get('peggedUSD', 0)
                if circulating and circulating > 1000000:
                    total_supply += circulating
                    coin_data = {
                        'id': coin.get('id', ''),
                        'name': coin.get('name', ''),
                        'symbol': coin.get('symbol', ''),
                        'circulating': circulating / 1e9,
                        'mechanism': coin.get('pegMechanism', ''),
                        'price': coin.get('price', 1.0),
                        'prev_day': coin.get('circulatingPrevDay', {}).get('peggedUSD', 0) / 1e9,
                        'prev_week': coin.get('circulatingPrevWeek', {}).get('peggedUSD', 0) / 1e9,
                        'prev_month': coin.get('circulatingPrevMonth', {}).get('peggedUSD', 0) / 1e9,
                    }
                    top_coins.append(coin_data)
                    coin_ids[coin.get('symbol', '')] = coin.get('id', '')
        
        top_coins.sort(key=lambda x: x['circulating'], reverse=True)
        
        return {
            'total_supply': total_supply / 1e9,
            'top_coins': top_coins[:15],
            'coin_ids': coin_ids,
            'timestamp': datetime.datetime.now().isoformat()
        }
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_stablecoin_historical():
    """ステーブルコイン履歴データを取得（DeFiLlama API）"""
    try:
        url = "https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        records = []
        
        if isinstance(data, list):
            for point in data:
                try:
                    date_val = point.get('date', 0)
                    if isinstance(date_val, str):
                        date_val = int(date_val)
                    date = datetime.datetime.fromtimestamp(date_val)
                    
                    total = 0
                    if 'totalCirculating' in point and isinstance(point['totalCirculating'], dict):
                        total = point['totalCirculating'].get('peggedUSD', 0) / 1e9
                    elif 'totalCirculatingUSD' in point and isinstance(point['totalCirculatingUSD'], dict):
                        total = point['totalCirculatingUSD'].get('peggedUSD', 0) / 1e9
                    
                    if total > 0:
                        records.append({'date': date, 'Total': total})
                except:
                    continue
        
        df = pd.DataFrame(records)
        if not df.empty and len(df) > 0:
            df = df.set_index('date')
            df = df.sort_index()
            return df
        
        return None
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_tokenized_treasury_data():
    """トークン化国債データを取得（DeFiLlama API）"""
    try:
        url = "https://api.llama.fi/protocols"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        protocols = response.json()
        
        treasury_keywords = ['treasury', 'tbill', 't-bill', 'buidl', 'usdy', 'usdm', 'usyc', 'ondo', 'openeden', 'hashnote', 'mountain', 'backed']
        gold_keywords = ['gold', 'xaut', 'paxg', 'gld', 'xau']
        
        treasury_data = []
        gold_data = []
        other_rwa_data = []
        
        treasury_tvl = 0
        gold_tvl = 0
        other_rwa_tvl = 0
        
        for protocol in protocols:
            name = protocol.get('name', '').lower()
            slug = protocol.get('slug', '').lower()
            symbol = protocol.get('symbol', '').lower()
            category = protocol.get('category', '').lower()
            
            is_rwa = 'rwa' in category or 'real world' in category
            if not is_rwa:
                continue
            
            tvl = protocol.get('tvl', 0)
            if not tvl or tvl < 1000000:
                continue
            
            protocol_info = {
                'name': protocol.get('name', ''),
                'symbol': protocol.get('symbol', '-'),
                'slug': protocol.get('slug', ''),
                'tvl': tvl / 1e9,
                'category': protocol.get('category', 'RWA'),
                'change_1d': protocol.get('change_1d', 0),
                'change_7d': protocol.get('change_7d', 0),
            }
            
            is_gold = any(kw in name or kw in symbol or kw in slug for kw in gold_keywords)
            is_treasury = any(kw in name or kw in symbol or kw in slug for kw in treasury_keywords)
            
            if is_gold:
                gold_data.append(protocol_info)
                gold_tvl += tvl
            elif is_treasury:
                treasury_data.append(protocol_info)
                treasury_tvl += tvl
            else:
                other_rwa_data.append(protocol_info)
                other_rwa_tvl += tvl
        
        treasury_data.sort(key=lambda x: x['tvl'], reverse=True)
        gold_data.sort(key=lambda x: x['tvl'], reverse=True)
        other_rwa_data.sort(key=lambda x: x['tvl'], reverse=True)
        
        return {
            'treasury': {'total_tvl': treasury_tvl / 1e9, 'protocols': treasury_data[:10]},
            'gold': {'total_tvl': gold_tvl / 1e9, 'protocols': gold_data[:5]},
            'other_rwa': {'total_tvl': other_rwa_tvl / 1e9, 'protocols': other_rwa_data[:10]},
            'total_rwa_tvl': (treasury_tvl + gold_tvl + other_rwa_tvl) / 1e9,
            'timestamp': datetime.datetime.now().isoformat()
        }
    except:
        return None

# ========== AI ANALYSIS FUNCTIONS ==========

def search_google_news(query, num_results=3, gl='US', mode='general'):
    """Google News RSSを検索"""
    try:
        import urllib.request
        hl = 'ja' if gl == 'JP' else 'en-US'
        ceid = 'JP:ja' if gl == 'JP' else 'US:en'
        
        search_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl={hl}&gl={gl}&ceid={ceid}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            feed_content = response.read()
        feed = feedparser.parse(feed_content)
        
        results = []
        for entry in feed.entries[:num_results]:
            title = entry.get('title', '')
            pub_date = entry.get('published', '')[:20] if entry.get('published') else ''
            link = entry.get('link', '')
            source = entry.get('source', {}).get('title', 'Unknown Source')
            results.append(f"- [{gl}] [{pub_date}] Source: {source} | {title}\n  Link: {link}")
        
        return "\n".join(results) if results else "該当するニュースが見つかりませんでした"
    except Exception as e:
        return f"検索エラー: {str(e)}"

def get_market_summary():
    """市場サマリーを生成"""
    df = st.session_state.get('df')
    if df is None:
        return "データが利用できません"
    
    summary_parts = []
    
    # Net Liquidity
    if 'Net_Liquidity' in df.columns:
        nl = df['Net_Liquidity'].iloc[-1]
        summary_parts.append(f"Net Liquidity: ${nl:.0f}B")
    
    # VIX
    if 'VIX' in df.columns:
        vix = df['VIX'].iloc[-1]
        summary_parts.append(f"VIX: {vix:.1f}")
    
    # S&P 500
    if 'SP500' in df.columns:
        sp = df['SP500'].iloc[-1]
        summary_parts.append(f"S&P 500: {sp:,.0f}")
    
    # Bitcoin
    if 'BTC' in df.columns:
        btc = df['BTC'].iloc[-1]
        summary_parts.append(f"BTC: ${btc:,.0f}")
    
    return "\n".join(summary_parts)

def run_gemini_analysis(prompt, use_search=True):
    """Gemini分析を実行"""
    gemini_client = st.session_state.get('gemini_client')
    if gemini_client is None:
        return "Gemini APIが設定されていません"
    
    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini分析エラー: {str(e)}"

def run_claude_analysis(prompt):
    """Claude分析を実行"""
    claude_client = st.session_state.get('claude_client')
    if claude_client is None:
        return "Claude APIが設定されていません"
    
    try:
        message = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Claude分析エラー: {str(e)}"

def get_time_diff_str(date_str):
    """時間差分を人間可読の文字列に変換"""
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
            return "📅 予定"
        elif seconds < 3600:
            return f"🔴 {int(seconds/60)}分前"
        elif seconds < 86400:
            return f"🟠 {int(seconds/3600)}時間前"
        elif seconds < 604800:
            return f"🟡 {int(seconds/86400)}日前"
        else:
            return f"🟢 {int(seconds/604800)}週前"
    except:
        return f"📅 {date_str[:16] if date_str else 'N/A'}"

# ========== SENTIMENT FUNCTIONS ==========

@st.cache_data(ttl=3600, show_spinner=False)
def get_crypto_fear_greed():
    """Crypto Fear & Greed Index を取得（Alternative.me API）"""
    try:
        url = "https://api.alternative.me/fng/?limit=30"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                current = data['data'][0]
                history = []
                for item in data['data']:
                    history.append({
                        'date': datetime.datetime.fromtimestamp(int(item['timestamp'])),
                        'value': int(item['value']),
                        'classification': item['value_classification']
                    })
                return {
                    'current': int(current['value']),
                    'classification': current['value_classification'],
                    'history': pd.DataFrame(history).set_index('date').sort_index()
                }
    except:
        pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_cnn_fear_greed():
    """CNN Fear & Greed Index を取得"""
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'fear_and_greed' in data:
                fg = data['fear_and_greed']
                history = []
                if 'fear_and_greed_historical' in data:
                    for point in data['fear_and_greed_historical'].get('data', []):
                        history.append({
                            'date': datetime.datetime.fromtimestamp(point['x'] / 1000),
                            'value': point['y']
                        })
                return {
                    'current': fg.get('score', None),
                    'classification': fg.get('rating', ''),
                    'previous_close': fg.get('previous_close', None),
                    'history': pd.DataFrame(history).set_index('date').sort_index() if history else None
                }
    except:
        pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_put_call_ratio():
    """Put/Call Ratio を取得"""
    # Placeholder - VIX as proxy
    return None

@st.cache_data(ttl=86400, show_spinner=False)
def get_aaii_sentiment():
    """AAII Investor Sentiment を取得"""
    try:
        return {
            'bullish': 38.5,
            'neutral': 31.2,
            'bearish': 30.3,
            'bull_bear_spread': 8.2,
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'note': 'データソース準備中'
        }
    except:
        return None
