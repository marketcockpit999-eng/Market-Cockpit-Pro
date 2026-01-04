import requests
from bs4 import BeautifulSoup
import pandas as pd

# Test fetching H.4.1 data
url = "https://www.federalreserve.gov/releases/h41/current/"

print("Fetching H.4.1 Report...")
print("=" * 60)

try:
    response = requests.get(url, timeout=10)
    print(f"HTTP Status: {response.status_code}")
    
    if response.status_code == 200:
        # Try pandas read_html first (easiest method)
        print("\nTrying pandas.read_html...")
        tables = pd.read_html(response.text)
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables[:5]):  # Show first 5 tables
            print(f"\nTable {i}:")
            print(f"Shape: {table.shape}")
            print(f"Columns: {table.columns.tolist()[:5]}")  # First 5 columns
            print(table.head(3))
            
except Exception as e:
    print(f"Error: {str(e)}")
