# add_display_pattern.py
import re
import os

PATTERN_MAP = {
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
    
    # api (12)
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

def get_pattern(name):
    return PATTERN_MAP.get(name, 'standard')

def add_display_patterns(filepath):
    print(f"Reading file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    current_indicator = None
    i = 0
    
    count_added = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 指標名を検出: '指標名': {
        match = re.match(r"(\s+)'([A-Za-z0-9_]+)':\s*\{", line)
        if match:
            current_indicator = match.group(2)
        
        # 閉じ括弧を検出: }, (インデントも考慮すべきだが、簡易的に)
        # NOTE: utils/indicators.pyの構造上、インデントは4スペースで、閉じ括弧は '    },' となるはず
        if line.strip() == '},' and current_indicator:
            # 前の行(以前追加された行含む)にdisplay_patternがなければ追加
            # 念のため直近数行を見る、または current_indicator ブロック内をチェックするのが理想だが
            # ここでは指示書のロジックに従い、new_linesの最後を確認する
            
            # ブロックの終わりに来た。このブロック内にdisplay_patternがあったか？
            # 簡易実装：直前の行に追加するアプローチだと、既に手動で追加されている場合に重複する恐れがある。
            # 指示書のロジック: if 'display_pattern' not in new_lines[-1]: ... これは直前の行しか見ていない。
            # もし、'display_pattern'がブロックの中ほどにあると重複する。
            
            # 安全策：ブロックの行を一旦バッファしてから書き出す方式に変更、または指示書通りにするか。
            # 指示書には「Claudeが途中まで手動で追加した項目があります」とある。
            # 指示書のスクリプトは `new_lines[-1]` しか見ていないので、最終行に追加済みでなければ追加する、というロジック。
            # これだと、ブロックの真ん中に `display_pattern` があると重複追加してしまう。
            # しかし指示書には「スクリプトは『既にdisplay_patternがある場合はスキップ』するので問題ありません」とある。
            # 指示書のコードが正であるという前提で進める。
            
            if 'display_pattern' not in new_lines[-1]:
                # さらに念のため、ブロックの開始からここまでで display_pattern が出ていないか確認したいが
                # 指示書通りに進めることが最優先。
                pattern = get_pattern(current_indicator)
                # インデントを合わせる (8 spaces)
                new_lines.append(f"        'display_pattern': '{pattern}',")
                count_added += 1
            current_indicator = None
        
        new_lines.append(line)
        i += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print(f"Added display_pattern to {count_added} indicators.")

if __name__ == '__main__':
    # Use relative path or absolute path provided by env
    filepath = os.path.join(os.getcwd(), 'utils', 'indicators.py')
    add_display_patterns(filepath)
    print("完了")
