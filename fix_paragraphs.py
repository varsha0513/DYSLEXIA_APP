import re

# Read the file
with open('backend/age_based_paragraphs.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix long lines by wrapping strings
lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Fix blank lines with whitespace
    if line.strip() == '':
        fixed_lines.append('')
        i += 1
        continue
    
    # For very long string literals (>79 chars), wrap them
    if '"' in line and len(line.rstrip()) > 79:
        # Extract the lead whitespace and the string
        match = re.match(r'^(\s*)"(.*)("?,?)$', line)
        if match:
            indent, text, trailing = match.groups()
            # If the line is too long, we'll leave it as is for now
            # as breaking paragraph text could affect formatting
            fixed_lines.append(line.rstrip())
        else:
            fixed_lines.append(line.rstrip())
    else:
        fixed_lines.append(line.rstrip())
    
    i += 1

# Write back
with open('backend/age_based_paragraphs.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines) + '\n')

print('✅ Fixed age_based_paragraphs.py (whitespace)')
