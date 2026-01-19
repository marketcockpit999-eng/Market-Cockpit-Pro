import re

with open('market_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

keys = re.findall(r'key="([^"]+)"', content)
print(f"Total keys found: {len(keys)}")

# Find duplicates
from collections import Counter
counter = Counter(keys)
duplicates = {k: v for k, v in counter.items() if v > 1}

if duplicates:
    print(f"\nDuplicate keys found:")
    for k, v in duplicates.items():
        print(f"  {k}: {v} times")
else:
    print("\nNo duplicate keys found!")
