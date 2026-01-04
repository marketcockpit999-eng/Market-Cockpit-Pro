import re

with open('market_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any existing key= in st.line_chart and st.plotly_chart
# Then add new unique keys properly

counter = [0]

def fix_line_chart(match):
    counter[0] += 1
    full_match = match.group(0)
    
    # Remove any existing key= from the match
    full_match = re.sub(r',\s*key="[^"]*"', '', full_match)
    
    # Insert key before the closing parenthesis
    return full_match[:-1] + f', key="lc_{counter[0]}")'

def fix_plotly_chart(match):
    counter[0] += 1
    full_match = match.group(0)
    
    # Remove any existing key= from the match
    full_match = re.sub(r',\s*key="[^"]*"', '', full_match)
    
    # Insert key before the closing parenthesis  
    return full_match[:-1] + f', key="pc_{counter[0]}")'

# Match st.line_chart with all contents until closing paren, handling nested parens
# Using a simpler approach - find line by line

lines = content.split('\n')
new_lines = []
lc_counter = 0
pc_counter = 0

for line in lines:
    # Handle st.line_chart
    if 'st.line_chart(' in line and 'key=' not in line:
        lc_counter += 1
        # Add key before the last )
        if line.rstrip().endswith(')'):
            line = line.rstrip()[:-1] + f', key="lc_{lc_counter}")' + '\n'
    elif 'st.line_chart(' in line and 'key=' in line:
        # Already has key, make it unique
        lc_counter += 1
        line = re.sub(r'key="[^"]*"', f'key="lc_{lc_counter}"', line)
    
    # Handle st.plotly_chart
    if 'st.plotly_chart(' in line and 'key=' not in line:
        pc_counter += 1
        if line.rstrip().endswith(')'):
            line = line.rstrip()[:-1] + f', key="pc_{pc_counter}")' + '\n'
    elif 'st.plotly_chart(' in line and 'key=' in line:
        pc_counter += 1
        line = re.sub(r'key="[^"]*"', f'key="pc_{pc_counter}"', line)
    
    new_lines.append(line)

content = '\n'.join(new_lines)

with open('market_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {lc_counter} st.line_chart and {pc_counter} st.plotly_chart calls")
