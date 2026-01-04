import re
import uuid

with open('market_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Counter for truly unique keys
counter = [0]

def fix_line_chart_key(line):
    counter[0] += 1
    # Generate a unique key
    unique_key = f'lc_{counter[0]}'
    
    # If line has key= in it, replace the key value
    if 'key=' in line:
        line = re.sub(r'key="[^"]*"', f'key="{unique_key}"', line)
    else:
        # Add key before the last )
        if line.rstrip().endswith(')'):
            line = line.rstrip()[:-1] + f', key="{unique_key}")\n'
    return line

lines = content.split('\n')
new_lines = []

for line in lines:
    if 'st.line_chart(' in line:
        new_lines.append(fix_line_chart_key(line))
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)

with open('market_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {counter[0]} st.line_chart calls")
