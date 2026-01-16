# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Configuration & Constants
全ての設定値、定数、マッピングを管理
"""

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
    'EU_CPI': '月次', 'US_Real_M2_Index': '月次', 'NFP': '月次', 'AvgHourlyEarnings': '月次', 
    'JOLTS': '月次', 'RetailSales': '月次', 'CI_Loans': '月次',
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
    'CN_Credit_Stock': 'CRDQCNAPABIS', 'CN_GDP': 'MKTGDPCNA646NWDB',
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

# ========== MANUAL GLOBAL M2 DATA ==========
# FREDで取得できない国のM2データ（手動更新）
# 更新時はvalueとdateを変更すること
MANUAL_GLOBAL_M2 = {
    'CN_M2': {
        'value': 336.9,      # 単位: Trillion CNY
        'date': '2025-11',   # 対象月
        'source': 'PBoC',    # 人民銀行
        'cpi': 0.2,          # CPIインフレ率(%)
    },
    'JP_M2': {
        'value': 1260,       # 単位: Trillion JPY
        'date': '2025-11',
        'source': 'BOJ',
        'cpi': 2.9,
    },
    'EU_M2': {
        'value': 15.6,       # 単位: Trillion EUR
        'date': '2025-11',
        'source': 'ECB',
        'cpi': 2.1,
    },
}

# ========== FRED UNITS ==========
FRED_UNITS = {
    'ON_RRP': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Reserves': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'TGA': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Fed_Assets': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'SOMA_Total': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'SOMA_Bills': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Bank_Cash': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
}

# ========== VALIDATION RANGES ==========
VALIDATION_RANGES = {
    'EFFR': (0, 15), 'IORB': (0, 15), 'SOFR': (0, 15), 'FedFundsUpper': (0, 15),
    'UNRATE': (0, 25), 'CorePCE': (-5, 15), 'Credit_Spread': (0, 30), 'US_TNX': (0, 20), 'T10Y2Y': (-5, 5),
    'NFP': (100000, 200000), 'ADP': (100000, 200000), 'JOLTS': (3000, 15000), 'ICSA': (100, 1000),
    'CPI': (200, 400), 'CPICore': (200, 400), 'PPI': (100, 350), 'AvgHourlyEarnings': (20, 60),
    'ON_RRP': (0, 3000), 'Reserves': (0, 5000), 'TGA': (0, 2000), 
    'Fed_Assets': (4000, 12000), 'SOMA_Total': (4000, 12000), 'Net_Liquidity': (2000, 8000),
    'VIX': (5, 100), 'SP500': (2000, 8000), 'DXY': (70, 130), 'USDJPY': (80, 200), 
    'Gold': (1000, 4000), 'BTC': (10000, 500000),
}

# ========== EXPLANATIONS ==========
# 全67項目の詳細説明文（market_app_original.pyから復元）
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
    "RMP": "【RMP (Reserve Management Purchases)】\n2025年12月12日開始。QT終了後、銀行準備金を「潤沢（ample）」レベルに維持するため、月額400億ドル規模で短期国債を買い入れる政策。FRBは景気刺激策（QE）ではないと強調するが、市場への資金供給効果は実質的にQEと同等との指摘もある。",
    
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
    "M2_Nominal": "【通貨供給量 M2（名目）】\n世の中に流通しているマネーの総量。",
    "M2_Real": "【通貨供給量 M2（実質）】\nインフレ調整後の実質的な購買力。",
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

# ========== RSS & NEWS ==========
MONITORED_AGENCIES = {
    "FRB": {"domain": "federalreserve.gov", "rss": "https://www.federalreserve.gov/feeds/press_all.xml", "label": "🏦 Federal Reserve"},
    "Treasury": {"domain": "treasury.gov", "rss": "https://home.treasury.gov/news/press-releases/rss.xml", "label": "💵 Treasury"},
}

RSS_FEEDS = {
    "🏛️ Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "🇪🇺 ECB": "https://www.ecb.europa.eu/rss/press.html",
    "🇯🇵 BOJ": "https://www.boj.or.jp/rss/news.xml",
    "📈 Markets": "https://news.google.com/rss/search?q=stock+market+breaking&hl=en-US&gl=US&ceid=US:en",
}

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
