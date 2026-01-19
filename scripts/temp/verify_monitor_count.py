
import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

from utils.config import DATA_FRESHNESS_RULES

def verify_count():
    daily = DATA_FRESHNESS_RULES['daily']['indicators']
    weekly = DATA_FRESHNESS_RULES['weekly']['indicators']
    monthly = DATA_FRESHNESS_RULES['monthly']['indicators']
    quarterly = DATA_FRESHNESS_RULES['quarterly']['indicators']
    
    print(f"Daily: {len(daily)}")
    print(f"Weekly: {len(weekly)}")
    print(f"Monthly: {len(monthly)}")
    print(f"Quarterly: {len(quarterly)}")
    
    total = len(daily) + len(weekly) + len(monthly) + len(quarterly)
    print(f"Total: {total}")
    
    all_items = daily + weekly + monthly + quarterly
    unique_items = set(all_items)
    print(f"Unique items: {len(unique_items)}")
    
    if len(all_items) != len(unique_items):
        print("⚠️ DUPLICATES FOUND!")
        seen = set()
        for x in all_items:
            if x in seen:
                print(f" - Duplicate: {x}")
            seen.add(x)

if __name__ == "__main__":
    verify_count()
