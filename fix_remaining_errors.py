#!/usr/bin/env python3
"""
Fix remaining 133 errors systematically.
Focuses on practical fixes that don't break functionality.
"""

import re

# Read app.py
with open('backend/app.py', 'r') as f:
    content = f.read()

# Fix 1: Remove unused 'result' variable assignment (line 1241)
# The result is not used after creation, so we can remove the assignment
pattern1 = r'(\s+)result = ResultCRUD\.create_result\(\s*db,'
replacement1 = r'\1ResultCRUD.create_result(\n\1    db,'
content = re.sub(pattern1, replacement1, content)

# Fix 2: Fix f-string missing placeholders (line 2067)
# Convert f"..." to regular strings when no placeholders
content = content.replace(
    'print(f"\\n✅ CHUNK READING SESSION COMPLETED")',
    'print("\\n✅ CHUNK READING SESSION COMPLETED")'
)

# Fix 3: Remove extra blank line before @app.exception_handler
# Replace multiple blank lines with exactly 2 blank lines
content = re.sub(r'\n\n\n+# ================== Error Handlers ==================\n+@',
                 r'\n\n\n# ================== Error Handlers ==================\n\n@',
                 content)

# Fix 4: Add blank line before @app.post("/assess-text"...)
# Find the line and ensure 2 blank lines before it
pattern4 = r'(raise HTTPException\(status_code=500, detail=msg\))\n\n(@app\.post\("/assess-text")'
replacement4 = r'\1\n\n\2'
content = re.sub(pattern4, replacement4, content)

# Write back
with open('backend/app.py', 'w') as f:
    f.write(content)

print("✅ Fixed app.py issues:")
print("  - Removed unused result variable assignment")
print("  - Fixed f-string without placeholder")
print("  - Fixed blank line spacing issues")

# Now fix age_based_paragraphs.py by wrapping long paragraph strings
with open('backend/age_based_paragraphs.py', 'r') as f:
    para_content = f.read()

# Function to wrap long strings in paragraphs
def wrap_long_paragraph(match):
    """Wrap long paragraph strings to fit in 79 chars"""
    quote_char = match.group(1)
    text = match.group(2)
    indent = match.group(3) if match.lastindex >= 3 else "        "
    
    if len(text) + len(indent) + len(quote_char) * 2 <= 79:
        return match.group(0)  # Already fits
    
    # Split long text into sentences or reasonable chunks
    sentences = text.split('. ')
    lines = []
    current_line = ""
    
    for i, sentence in enumerate(sentences):
        if i < len(sentences) - 1:
            sentence = sentence + ". "
        
        if len(current_line) + len(sentence) <= 65:  # Leave room for quotes and indent
            current_line += sentence
        else:
            if current_line:
                lines.append(current_line.rstrip())
            current_line = sentence
    
    if current_line:
        lines.append(current_line.rstrip())
    
    if len(lines) <= 1:
        return match.group(0)  # Can't improve
    
    # Reconstruct with line continuation
    result = f'{indent}{quote_char}\n'
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            result += f'{indent}{quote_char}{line}{quote_char}\n'
        else:
            result += f'{indent}{quote_char}{line}{quote_char}'
            # Add trailing comma and newline if needed
            if match.group(0).rstrip().endswith(','):
                result += ','
    
    return result

# Find and wrap paragraphs in lists
# Pattern: quoted strings in lists
para_pattern = r'(\s{8})(["\'])(.+?)\2(,?)$'
lines = para_content.split('\n')
output_lines = []

for i, line in enumerate(lines):
    # Check if line is too long
    if len(line) > 79 and any(x in line for x in ['The cat sat', 'A big red', 'The sun is', 'The butterfly']):
        # This is a paragraph line to fix
        match = re.match(r'(\s{8})(["\'])(.+?)\2(,?)', line)
        if match:
            indent = match.group(1)
            quote = match.group(2)
            text = match.group(3)
            comma = match.group(4)
            trailing = line[len(match.group(0)):]
            
            # For simpler approach: just split at sentence boundaries if possible
            if len(text) > 79:
                # Try to find a good split point (after a period)
                parts = text.split('. ')
                if len(parts) > 1:
                    # Keep first sentence(s) on first line, rest on next
                    part1 = parts[0] + '. '
                    part2 = '. '.join(parts[1:])
                    
                    # Check if we can fit more
                    while len(part1) < 65 and len(parts) > 1:
                        if len(part1) + len(parts[1]) + 2 < 65:  # +2 for '. '
                            parts.pop(0)
                            part1 += parts[0] + '. '
                        else:
                            break
                    
                    part2 = text[len(part1):]
                    output_lines.append(f'{indent}{quote}{part1}{quote}')
                    output_lines.append(f'{indent}{quote}{part2}{quote}{comma}')
                    continue
        
        output_lines.append(line)
    else:
        output_lines.append(line)

para_content = '\n'.join(output_lines)

with open('backend/age_based_paragraphs.py', 'w') as f:
    f.write(para_content)

print("✅ Fixed age_based_paragraphs.py:")
print("  - Wrapped long paragraph strings")

print("\n✅ All critical fixes applied!")
