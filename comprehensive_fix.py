import re

with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    original_line = line

    # Fix continuation lines with wrong indentation (809-812)
    if 'age_group == "7-9"' in line:
        # This is part of a ternary operator, fix indentation
        fixed_lines.append('                          8 if age_group == "7-9" else\n')
        i += 1
        continue
    elif 'age_group == "10-12"' in line and '11 if' in line:
        fixed_lines.append('                          11 if age_group == "10-12" else\n')
        i += 1
        continue
    elif 'age_group == "13-15"' in line and '14 if' in line:
        fixed_lines.append('                          14 if age_group == "13-15" else\n')
        i += 1
        continue
    elif 'age_group == "16-18"' in line and '17 if' in line:
        fixed_lines.append('                          17 if age_group == "16-18" else 20)\n')
        i += 1
        continue

    # Fix f-string without placeholders - convert to regular string
    if 'f"✅ Chunk Reading Session Created"' in line:
        fixed_lines.append(line.replace('f"✅ Chunk Reading Session Created"',
                                        '"✅ Chunk Reading Session Created"'))
        i += 1
        continue
    elif 'f"\\n✅ SPEED TRAINER SESSION COMPLETED"' in line:
        fixed_lines.append(line.replace('f"\\n✅ SPEED TRAINER SESSION COMPLETED"',
                                        '"\\n✅ SPEED TRAINER SESSION COMPLETED"'))
        i += 1
        continue
    elif 'f"   Status: Completed"' in line:
        fixed_lines.append(line.replace('f"   Status: Completed"',
                                        '"   Status: Completed"'))
        i += 1
        continue

    # Remove unused variable assignment
    if 'result = ResultCRUD.create_result(' in line:
        # Skip this line and the next to remove the unused assignment
        if i + 1 < len(lines) and ')' in lines[i + 1]:
            i += 2  # Skip both lines
            continue

    if 'comparison = PronunciationComparator.compare_word("", word)' in line:
        # Skip this unused assignment
        i += 1
        continue

    # Fix long lines with f-strings - extract the variable first
    if 'elapsed_time_formatted=' in line and len(line.rstrip()) > 79:
        # This is part of a multi-line dict, leave as is
        fixed_lines.append(line)
        i += 1
        continue

    if 'for batch, we\'ll just provide pronunciation' in line.lower():
        # Split the comment
        fixed_lines.append('                # For batch, we provide pronunciation\n')
        fixed_lines.append('                # and similarity without audio\n')
        i += 1
        continue

    # Fix expected blank lines before @app.post decorators
    if '@app.post("/assess-text"' in line and i > 0:
        if fixed_lines and fixed_lines[-1].strip() != '':
            # Insert blank line before
            if fixed_lines[-1].rstrip() != '':
                # Check if previous line is also a blank line
                if i > 1 and lines[i-1].strip() == '':
                    # Already has one blank, add another
                    fixed_lines.append('\n')
                else:
                    fixed_lines.append('\n')
                    fixed_lines.append('\n')

    # Fix long lines in decorators
    if '@app.post("/speed-trainer/submit-results"' in line and len(line.rstrip()) > 79:
        fixed_lines.append('@app.post(\n')
        fixed_lines.append('    "/speed-trainer/submit-results",\n')
        fixed_lines.append('    response_model=SpeedTrainerCompletionResult\n')
        fixed_lines.append(')\n')
        i += 1
        continue

    if '@app.get("/chunk-reading/session/' in line and len(line.rstrip()) > 79:
        m = re.match(r'(\s*)@app\.get\("([^"]+)",\s*response_model=([^)]+)\)', line)
        if m:
            indent, path, model = m.groups()
            fixed_lines.append(f'{indent}@app.get(\n')
            fixed_lines.append(f'{indent}    "{path}",\n')
            fixed_lines.append(f'{indent}    response_model={model}\n')
            fixed_lines.append(f'{indent})\n')
            i += 1
            continue

    # Keep the line as is if no special handling
    fixed_lines.append(line)
    i += 1

# Write back
with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('✅ Fixed remaining errors in app.py')
