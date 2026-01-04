import requests
import pandas as pd
from io import StringIO

url = "https://www.federalreserve.gov/releases/h41/current/"

response = requests.get(url, timeout=15)
tables = pd.read_html(StringIO(response.text))

print(f"Total tables found: {len(tables)}")
print("=" * 80)

# Examine Table 1 in detail
for i in range(min(5, len(tables))):
    table = tables[i]
    print(f"\n{'='*80}")
    print(f"TABLE {i}")
    print(f"Shape: {table.shape}")
    print(f"Columns: {table.columns.tolist()}")
    print(f"\nFirst column values (first 20 rows):")
    
    for idx, row in table.head(20).iterrows():
        first_col = str(row.iloc[0]).strip()
        last_col = str(row.iloc[-1]).strip()
        print(f"  {idx:2d}: {first_col[:60]:60s} | Last col: {last_col}")
        
        # Look for "Bills" specifically
        if 'bills' in first_col.lower() and 'total' not in first_col.lower():
            print(f"      ^^^ POTENTIAL BILLS ROW! Value: {last_col}")
