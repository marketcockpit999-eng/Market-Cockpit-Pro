import requests
import pandas as pd
from io import StringIO
import re

url = "https://www.federalreserve.gov/releases/h41/current/"

response = requests.get(url, timeout=15)

# Search for "Bills" in raw HTML
print("Searching for 'Bills' in HTML...")
print("=" * 80)

# Find all occurrences of numbers near "Bills"
pattern = r'(?i)(bills[^<]{0,100}?)([\d,]+\.?\d*)'
matches = re.findall(pattern, response.text)

for context, number in matches[:10]:
    clean_context = re.sub(r'<[^>]+>', '', context).strip()[:80]
    print(f"Context: {clean_context}")
    print(f"Number: {number}")
    print("-" * 40)

# Also check if there's a separate Table 1A
tables = pd.read_html(StringIO(response.text))
print(f"\nTotal tables: {len(tables)}")

# Look for table with "Bills" breakdown
for i, table in enumerate(tables[:10]):
    table_str = table.to_string()
    if 'bills' in table_str.lower() or 'notes' in table_str.lower():
        print(f"\n{'='*80}")
        print(f"TABLE {i} (contains 'bills' or 'notes'):")
        print(table.head(30))
