import sys

# Read the file with error handling
with open(r'c:\Users\81802\.gemini\antigravity\scratch\market_monitor\market_app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Replace expanded=False with expanded=True
fixed_content = content.replace('expanded=False', 'expanded=True')

# Write back with proper UTF-8 encoding
with open(r'c:\Users\81802\.gemini\antigravity\scratch\market_monitor\market_app.py', 'w', encoding='utf-8') as out:
    out.write(fixed_content)

print('File fixed and re-encoded successfully')
print(f'Made {content.count("expanded=False")} replacements')
