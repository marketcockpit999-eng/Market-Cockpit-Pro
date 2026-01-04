import re

with open('market_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count before
before_count = len(re.findall(r'key="lc_\d+"', content))
print(f"Found {before_count} lc_ keys before removal")

# Remove key="lc_XX" patterns (handles various whitespace)
content = re.sub(r',\s*key="lc_\d+"', '', content)

# Also remove any chart_ keys that might still exist
content = re.sub(r',\s*key="chart_\d+"', '', content)

# Verify removal
after_count = len(re.findall(r'key="lc_\d+"', content))
print(f"Found {after_count} lc_ keys after removal")

with open('market_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Keys removed successfully!")
