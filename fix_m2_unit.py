with open('market_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace line 752
for i, line in enumerate(lines):
    if i == 751:  # Line 752 (0-indexed)
        lines[i] = line.replace('"pt"', '"B"')
        print(f"Line {i+1} updated:")
        print(f"  Before: {repr(line[:80])}")
        print(f"  After:  {repr(lines[i][:80])}")

with open('market_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ M2 (Real) unit corrected from 'pt' to 'B'")
