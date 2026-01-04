import requests
import pandas as pd
from io import StringIO
import re

url = "https://www.federalreserve.gov/releases/h41/current/"

print("Testing H.4.1 fetch...")
print("=" * 60)

try:
    print("1. Sending request...")
    response = requests.get(url, timeout=15)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ERROR: HTTP {response.status_code}")
        exit(1)
    
    print("2. Parsing HTML tables...")
    tables = pd.read_html(StringIO(response.text))
    print(f"   Found {len(tables)} tables")
    
    print("3. Extracting date...")
    date_match = re.search(r'Week ended (\w+ \d+, \d+)', response.text)
    if date_match:
        report_date = pd.to_datetime(date_match.group(1))
        print(f"   Date: {report_date}")
    else:
        print("   Date: Not found")
    
    print("4. Looking for SOMA Bills...")
    table1 = tables[1] if len(tables) > 1 else None
    if table1 is not None:
        print(f"   Table 1 shape: {table1.shape}")
        last_col_idx = table1.shape[1] - 1
        
        for idx, row in table1.iterrows():
            row_text = str(row.iloc[0]).lower()
            if 'u.s. treasury securities' in row_text:
                try:
                    soma_bills = float(row.iloc[last_col_idx]) / 1000
                    print(f"   SOMA Bills: ${soma_bills:.1f}B")
                    break
                except Exception as e:
                    print(f"   Error parsing: {e}")
    
    print("5. Looking for Total Loans...")
    found = False
    for i, table in enumerate(tables):
        for idx, row in table.iterrows():
            row_text = str(row.iloc[0]).lower()
            if 'loans' in row_text and 'total' not in row_text:
                try:
                    val = row.iloc[-1]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        total_loans = float(val) / 1000
                        print(f"   Total Loans: ${total_loans:.1f}B (Table {i})")
                        found = True
                        break
                except Exception as e:
                    print(f"   Error parsing: {e}")
        if found:
            break
    
    if not found:
        print("   Total Loans: Not found")
    
    print("\nSUCCESS!")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
