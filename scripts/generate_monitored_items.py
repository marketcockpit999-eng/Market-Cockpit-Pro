# -*- coding: utf-8 -*-
"""
Generate MONITORED_ITEMS.md from utils/indicators.py
================================================================================
This script reads the unified indicator registry and generates documentation.
Run this script whenever indicators.py is updated to keep docs in sync.

Usage:
    python scripts/generate_monitored_items.py
================================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.indicators import INDICATORS


def generate_monitored_items_md():
    """Generate MONITORED_ITEMS.md content from INDICATORS registry."""
    
    # Group indicators by frequency
    by_frequency = defaultdict(list)
    for name, info in INDICATORS.items():
        freq = info.get('frequency', 'unknown')
        by_frequency[freq].append((name, info))
    
    # Sort each group by name
    for freq in by_frequency:
        by_frequency[freq].sort(key=lambda x: x[0])
    
    # Frequency display order and labels
    freq_order = ['daily', 'weekly', 'monthly', 'quarterly']
    freq_labels = {
        'daily': 'Daily (日次)',
        'weekly': 'Weekly (週次)',
        'monthly': 'Monthly (月次)',
        'quarterly': 'Quarterly (四半期)',
    }
    
    # Count totals
    total_count = len(INDICATORS)
    freq_counts = {f: len(by_frequency[f]) for f in freq_order}
    
    # Build markdown content
    lines = []
    lines.append("# 📊 Market Cockpit Pro - 監視対象項目一覧")
    lines.append("")
    lines.append("> **Source**: Auto-generated from `utils/indicators.py`  ")
    lines.append(f"> **更新日**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append("> **⚠️ このファイルは自動生成です。直接編集せず、indicators.pyを修正後にスクリプトを再実行してください。**")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Summary
    lines.append("## 📈 サマリー")
    lines.append("")
    lines.append(f"| 頻度 | 指標数 |")
    lines.append("|------|--------|")
    for freq in freq_order:
        label = freq_labels.get(freq, freq)
        count = freq_counts.get(freq, 0)
        lines.append(f"| {label} | {count} |")
    lines.append(f"| **合計** | **{total_count}** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Each frequency section
    for freq in freq_order:
        if freq not in by_frequency:
            continue
        
        indicators = by_frequency[freq]
        label = freq_labels.get(freq, freq)
        
        lines.append(f"## ✅ {label}: {len(indicators)}項目")
        lines.append("")
        lines.append("| # | Indicator | Source | ID | Unit | Category | Description |")
        lines.append("|---|-----------|--------|-----|------|----------|-------------|")
        
        for i, (name, info) in enumerate(indicators, 1):
            source = info.get('source', '-')
            id_val = info.get('id', '-')
            unit = info.get('unit', '-')
            category = info.get('category', '-')
            notes = info.get('notes', '-')
            
            # Escape pipe characters in notes
            notes = notes.replace('|', '\\|')
            
            lines.append(f"| {i} | `{name}` | {source} | {id_val} | {unit} | {category} | {notes} |")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Data sources section
    lines.append("## 📚 データソース")
    lines.append("")
    lines.append("| Source | Description |")
    lines.append("|--------|-------------|")
    lines.append("| FRED | Federal Reserve Economic Data (セントルイス連銀) |")
    lines.append("| YAHOO | Yahoo Finance (yfinance経由) |")
    lines.append("| CALCULATED | 他の指標から計算される派生値 |")
    lines.append("| MANUAL | 手動入力（utils/config.pyで管理） |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Maintenance notes
    lines.append("## 🔧 メンテナンス")
    lines.append("")
    lines.append("### 指標の追加・修正方法")
    lines.append("")
    lines.append("1. `utils/indicators.py` の `INDICATORS` ディクショナリを編集")
    lines.append("2. 以下のコマンドでこのドキュメントを再生成:")
    lines.append("   ```bash")
    lines.append("   python scripts/generate_monitored_items.py")
    lines.append("   ```")
    lines.append("3. `git commit` で変更をコミット")
    lines.append("")
    lines.append("### 必須フィールド")
    lines.append("")
    lines.append("```python")
    lines.append("'INDICATOR_NAME': {")
    lines.append("    'source': 'FRED',        # FRED, YAHOO, CALCULATED, MANUAL")
    lines.append("    'id': 'SERIES_ID',       # FRED series ID or Yahoo ticker")
    lines.append("    'unit': '%',             # Display unit")
    lines.append("    'frequency': 'daily',    # daily, weekly, monthly, quarterly")
    lines.append("    'freshness': 'daily',    # For staleness monitoring")
    lines.append("    'category': 'rates',     # Grouping category")
    lines.append("    'ui_page': '01_liquidity', # Which page displays this")
    lines.append("    'ai_include': True,      # Include in AI analysis?")
    lines.append("    'ai_section': '金利',    # AI summary section name")
    lines.append("    'notes': 'Description',  # Human-readable description")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    # Generate content
    content = generate_monitored_items_md()
    
    # Write to file
    output_path = Path(__file__).parent.parent / "MONITORED_ITEMS.md"
    output_path.write_text(content, encoding='utf-8')
    
    print(f"✅ Generated: {output_path}")
    print(f"   Total indicators: {len(INDICATORS)}")
    
    # Show frequency breakdown
    from collections import Counter
    freq_counts = Counter(info['frequency'] for info in INDICATORS.values())
    for freq, count in sorted(freq_counts.items()):
        print(f"   - {freq}: {count}")


if __name__ == '__main__':
    main()
