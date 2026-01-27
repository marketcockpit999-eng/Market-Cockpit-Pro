# -*- coding: utf-8 -*-
"""
Analyze display patterns in indicators.py
"""

from utils.indicators import INDICATORS

# Count by display_pattern
patterns = {}
for name, config in INDICATORS.items():
    pattern = config.get('display_pattern', 'UNDEFINED')
    if pattern not in patterns:
        patterns[pattern] = []
    patterns[pattern].append(name)

print("=" * 60)
print("Display Pattern Analysis")
print("=" * 60)
print()

for pattern, indicators in sorted(patterns.items()):
    print(f"\n📊 {pattern}: {len(indicators)} items")
    print("-" * 40)
    for name in indicators:
        config = INDICATORS[name]
        notes = config.get('notes', '')[:40]
        source = config.get('source', '?')
        print(f"  {name:<25} [{source}] {notes}")

print()
print("=" * 60)
print(f"Total indicators: {len(INDICATORS)}")
print("=" * 60)
