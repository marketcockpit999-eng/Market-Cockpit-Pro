# -*- coding: utf-8 -*-
"""
一括でdisplay_patternを追加するスクリプト
"""
import re

# パターン割り当て
PATTERN_ASSIGNMENTS = {
    # mom_yoy (6)
    'CPI': 'mom_yoy',
    'CPICore': 'mom_yoy',
    'CorePCE': 'mom_yoy',
    'PPI': 'mom_yoy',
    'RetailSales': 'mom_yoy',
    'ConsumerSent': 'mom_yoy',
    
    # manual_calc (6)
    'NFP': 'manual_calc',
    'UNRATE': 'manual_calc',
    'AvgHourlyEarnings': 'manual_calc',
    'ICSA': 'manual_calc',
    'RealGDP': 'manual_calc',
    'ADP': 'manual_calc',
    
    # web_scrape (2)
    'Richmond_Fed_Mfg': 'web_scrape',
    'Richmond_Fed_Services': 'web_scrape',
    
    # calculated (1)
    'Global_Liquidity_Proxy': 'calculated',
    
    # api (12) - df_stored=Falseの項目
    'SP500_PE': 'api',
    'NASDAQ_PE': 'api',
    'BTC_Funding_Rate': 'api',
    'BTC_Open_Interest': 'api',
    'BTC_Long_Short_Ratio': 'api',
    'ETH_Funding_Rate': 'api',
    'ETH_Open_Interest': 'api',
    'Stablecoin_Total': 'api',
    'Treasury_TVL': 'api',
    'Gold_TVL': 'api',
    'Crypto_Fear_Greed': 'api',
    'CNN_Fear_Greed': 'api',
}

def get_pattern(indicator_name):
    """指標名からパターンを取得（デフォルトはstandard）"""
    return PATTERN_ASSIGNMENTS.get(indicator_name, 'standard')

def add_display_patterns(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 各指標エントリを見つけてdisplay_patternを追加
    # パターン: 'INDICATOR_NAME': { ... },
    
    # 既にdisplay_patternがある項目はスキップ
    indicator_pattern = r"'([A-Za-z0-9_]+)':\s*\{([^}]+)\},"
    
    def add_pattern(match):
        name = match.group(1)
        body = match.group(2)
        
        # 既にdisplay_patternがあればスキップ
        if 'display_pattern' in body:
            return match.group(0)
        
        pattern = get_pattern(name)
        
        # 最後の行の前にdisplay_patternを追加
        lines = body.rstrip().split('\n')
        last_line = lines[-1]
        
        # インデント検出
        indent = '        '
        
        # 最後の行の後にdisplay_patternを追加
        new_body = body.rstrip() + f"\n{indent}'display_pattern': '{pattern}',"
        
        return f"'{name}': {{{new_body}\n    }},"
    
    # 単純な方法：各項目の閉じ括弧の前にdisplay_patternを追加
    lines = content.split('\n')
    new_lines = []
    current_indicator = None
    
    for i, line in enumerate(lines):
        # 指標名を検出
        indicator_match = re.match(r"\s+'([A-Za-z0-9_]+)':\s*\{", line)
        if indicator_match:
            current_indicator = indicator_match.group(1)
        
        # 閉じ括弧を検出（指標の終わり）
        if line.strip() == '},' and current_indicator:
            # 前の行にdisplay_patternがなければ追加
            if "'display_pattern'" not in new_lines[-1]:
                pattern = get_pattern(current_indicator)
                new_lines.append(f"        'display_pattern': '{pattern}',")
            current_indicator = None
        
        new_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("完了！")

if __name__ == '__main__':
    add_display_patterns(r'C:\Users\81802\.gemini\antigravity\scratch\market_monitor\utils\indicators.py')
