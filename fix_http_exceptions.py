#!/usr/bin/env python3
"""
Fix remaining long HTTPException lines in app.py
Strategy: Extract error messages to variables to break lines
"""

import re

with open('backend/app.py', 'r') as f:
    lines = f.readlines()

# Process the file
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Look for long HTTPException lines
    if 'raise HTTPException' in line and len(line.rstrip()) > 79:
        # Extract the parts
        match = re.search(r'raise HTTPException\(status_code=(\d+), detail=(.+)\)', line)
        if match:
            status_code = match.group(1).strip()
            detail = match.group(2).strip().rstrip(')')
            indent = len(line) - len(line.lstrip())
            
            # Try to reformat
            if len(f'{" " * indent}raise HTTPException(status_code={status_code}, detail=detail)') <= 79:
                # Simple case: extract to variable
                new_lines.append(f'{" " * indent}detail = {detail}\n')
                new_lines.append(f'{" " * indent}raise HTTPException(status_code={status_code}, detail=detail)\n')
                i += 1
                continue
        
        # Fallback: keep original line but try wrapping in parentheses
        if detail.startswith('f"') or detail.startswith('f\''):
            # Split f-string if possible
            if 'f"' in line:
                parts = re.search(r'(f"[^"]*") \+ (.*)\)', line)
                if not parts:
                    # Can't easily split, keep as is
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)
    
    i += 1

# Write back
with open('backend/app.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Processed app.py - attempted to extract long errors")
