import requests
import re

url = "https://www.federalreserve.gov/releases/h41/current/"

print("Testing date extraction...")
response = requests.get(url, timeout=10)

# Try different date patterns
patterns = [
    r'Week ended (\w+ \d+, \d+)',
    r'week ended (\w+\s+\d+,\s+\d{4})',
    r'ended (\w+\s+\d+,\s+\d{4})',
    r'(\w+\s+\d+,\s+\d{4})',
]

for pattern in patterns:
    matches = re.findall(pattern, response.text, re.IGNORECASE)
    if matches:
        print(f"Pattern '{pattern}' found: {matches[:3]}")
        break
else:
    print("No date pattern matched")
    
# Search for specific keywords
if 'Week ended' in response.text:
    print("'Week ended' found in text")
    # Show context around it
    idx = response.text.find('Week ended')
    print(f"Context: ...{response.text[idx:idx+100]}...")
elif 'week ended' in response.text.lower():
    print("'week ended' (lowercase) found")
else:
    print("'Week ended' NOT found in text")
