import re

# Read the app.py file
with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
max_length = 79
i = 0

while i < len(lines):
    line = lines[i].rstrip('\n')
    line_length = len(line.rstrip())

    # Fix long HTTPException lines
    if 'raise HTTPException' in line and 'detail=' in line and line_length > max_length:
        match = re.match(
            r'(\s*)raise HTTPException\(status_code=(\d+), detail="([^"]+)"\)',
            line
        )
        if match:
            indent, code, detail = match.groups()
            fixed_lines.append(f'{indent}detail = "{detail}"\n')
            fixed_lines.append(
                f'{indent}raise HTTPException(status_code={code}, detail=detail)\n'
            )
            i += 1
            continue

    # Fix access_token lines (long token assignment)
    if 'access_token = create_access_token' in line and line_length > max_length:
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        fixed_lines.append(f'{indent_str}token_data = {{\n')
        fixed_lines.append(f'{indent_str}    "user_id": user.id,\n')
        fixed_lines.append(f'{indent_str}    "email": user.email\n')
        fixed_lines.append(f'{indent_str}}}\n')
        fixed_lines.append(
            f'{indent_str}access_token = create_access_token(data=token_data)\n'
        )
        i += 1
        continue

    # Fix long message strings
    if '"message":' in line and line_length > max_length:
        if 'Paragraph selected for age' in line:
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            fixed_lines.append(f'{indent_str}group = age_group_info["age_group"]\n')
            fixed_lines.append(f'{indent_str}msg = f"\u2705 Paragraph selected for age')
            fixed_lines.append(' {age} ({group})"\n')
            fixed_lines.append(f'{indent_str}return {{"paragraph": paragraph, "message": msg}}\n')
            # Skip the next few lines
            while i < len(lines) and 'return' not in lines[i]:
                i += 1
            if i < len(lines):
                i += 1
            continue

    # Keep the line as is if no special handling
    fixed_lines.append(line + '\n')
    i += 1

# Remove extra blank lines at end
while fixed_lines and fixed_lines[-1].strip() == '':
    fixed_lines.pop()

# Write the fixed content
with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('✅ Fixed long lines in app.py')
