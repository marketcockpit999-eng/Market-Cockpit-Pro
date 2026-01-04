import re

with open('market_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove key= from st.line_chart calls
# Pattern: st.line_chart(..., key="...")
content = re.sub(r'(st\.line_chart\([^)]*),\s*key="[^"]*"', r'\1', content)

with open('market_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed key parameter from st.line_chart calls")
