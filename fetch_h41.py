import requests
import pandas as pd
import re

def fetch_h41_data():
    """
    Fetch latest H.4.1 data from FRB website
    Returns: (report_date, soma_bills, total_loans) or (None, None, None) on error
    """
    url = "https://www.federalreserve.gov/releases/h41/current/"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None, None, None
        
        # Parse tables
        tables = pd.read_html(response.text)
        
        # Extract report date from page title or first table
        report_date = None
        date_match = re.search(r'Week ended (\w+ \d+, \d+)', response.text)
        if date_match:
            report_date = pd.to_datetime(date_match.group(1))
        
        # Table 1: Securities held outright (contains SOMA data)
        # Look for "U.S. Treasury securities" row
        table1 = tables[1] if len(tables) > 1 else None
        soma_bills = None
        
        if table1 is not None:
            # The last column usually contains Wednesday values
            last_col_idx = table1.shape[1] - 1
            
            # Find "U.S. Treasury securities" or similar
            for idx, row in table1.iterrows():
                row_text = str(row.iloc[0]).lower()
                if 'u.s. treasury securities' in row_text or 'treasury securities' in row_text:
                    try:
                        soma_bills = float(row.iloc[last_col_idx]) / 1000  # Convert to Billions
                        break
                    except:
                        pass
        
        # Find Total Loans - usually in a separate section
        # Look for "Loans" keyword in tables
        total_loans = None
        for table in tables:
            for idx, row in table.iterrows():
                row_text = str(row.iloc[0]).lower()
                if 'loans' in row_text and 'total' not in row_text:
                    try:
                        # Try to extract numeric value from last column
                        val = row.iloc[-1]
                        if pd.notna(val) and isinstance(val, (int, float)):
                            total_loans = float(val) / 1000  # Convert to Billions
                            break
                    except:
                        pass
            if total_loans is not None:
                break
        
        return report_date, soma_bills, total_loans
        
    except Exception as e:
        print(f"Error fetching H.4.1: {str(e)}")
        return None, None, None

# Test
if __name__ == "__main__":
    print("Testing H.4.1 auto-fetch...")
    date, soma, loans = fetch_h41_data()
    
    if date:
        print(f"Report Date: {date}")
    if soma:
        print(f"SOMA Bills (estimated): ${soma:.1f}B")
    if loans:
        print(f"Total Loans: ${loans:.1f}B")
    
    if not date and not soma and not loans:
        print("Failed to fetch data")
