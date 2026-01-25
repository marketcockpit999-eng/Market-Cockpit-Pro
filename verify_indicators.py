# -*- coding: utf-8 -*-
"""
Verify 88 indicators and their display patterns
"""
import sys
sys.path.insert(0, '.')

from utils.indicators import INDICATORS

# Count by source
sources = {}
for name, info in INDICATORS.items():
    src = info['source']
    sources[src] = sources.get(src, 0) + 1

print('=== Source Breakdown ===')
for src, count in sorted(sources.items()):
    print(f'{src}: {count}')
print(f'Total: {len(INDICATORS)}')
print()

# Count by ui_page
pages = {}
for name, info in INDICATORS.items():
    page = info.get('ui_page', 'unknown')
    pages[page] = pages.get(page, 0) + 1

print('=== Page Breakdown ===')
for page, count in sorted(pages.items()):
    print(f'{page}: {count}')
print()

# Count by frequency
freqs = {}
for name, info in INDICATORS.items():
    freq = info['frequency']
    freqs[freq] = freqs.get(freq, 0) + 1

print('=== Frequency Breakdown ===')
for freq, count in sorted(freqs.items()):
    print(f'{freq}: {count}')
print()

# List all indicators grouped by source
print('=== All Indicators by Source ===')
for src in ['FRED', 'YAHOO', 'WEB', 'CALCULATED']:
    indicators = [(name, info) for name, info in INDICATORS.items() if info['source'] == src]
    print(f'\n{src} ({len(indicators)} items):')
    for name, info in sorted(indicators):
        print(f'  - {name}: {info["ui_page"]} ({info["frequency"]})')
