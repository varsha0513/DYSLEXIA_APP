#!/usr/bin/env python3
"""Fix all remaining PEP 8 line length violations (>79 chars)"""

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix specific long lines
fixes = [
    # File validation
    ('if audio_file.filename and not audio_file.filename.lower().endswith((\'.wav\', \'.mp3\', \'.webm\')):',
     'if audio_file.filename:\n            exts = (\'.wav\', \'.mp3\', \'.webm\')\n            if not audio_file.filename.lower().endswith(exts):'),
    
    # Print statements with multiple variables
    ('print(f"⏱️ Reading time: {elapsed_time:.2f}s, WPM: {wpm:.1f} ({step_times[\'speed_analysis\']:.2f}s)")',
     'et = elapsed_time\n        wpm_val = wpm\n        duration = step_times[\'speed_analysis\']\n        print(f"⏱️ Time: {et:.2f}s, WPM: {wpm_val:.1f} ({duration:.2f}s)")'),
    
    ('print(f"⚠️ Risk Level: {risk_assessment[\'risk_level\']} ({step_times[\'risk_scoring\']:.2f}s)")',
     'level = risk_assessment[\'risk_level\']\n        ts = step_times[\'risk_scoring\']\n        print(f"⚠️ Risk: {level} ({ts:.2f}s)")'),
    
    ('accuracy_feedback = get_performance_feedback(comparison_result[\'accuracy_percent\'])',
     'accuracy_pct = comparison_result[\'accuracy_percent\']\n        accuracy_feedback = get_performance_feedback(accuracy_pct)'),
    
    ('difficulty = "✅ Excellent reader - Challenge with harder passages"',
     'difficulty = "✅ Excellent - Challenge harder passages"'),
    
    ('difficulty = "⚠️ Accurate but slow - May need confidence building"',
     'difficulty = "⚠️ Accurate but slow - Build confidence"'),
    
    ('if tts_engine and (comparison_result[\'wrong_words\'] > 0 or comparison_result[\'missing_words\'] > 0):',
     'has_errors = (comparison_result[\'wrong_words\'] > 0 or\n                  comparison_result[\'missing_words\'] > 0)\n        if tts_engine and has_errors:'),
    
    ('wrong_words=[[w, c] for w, c in wrong_words],  # Convert tuples to lists for JSON',
     'wrong_words=[[w, c] for w, c in wrong_words],'),
    
    ('print(f"✅ Assistance data generated: {assistance_data.error_count} errors found ({step_times[\'assistance\']:.2f}s)")',
     'ec = assistance_data.error_count\n            ts = step_times[\'assistance\']\n            print(f"✅ Assistance: {ec} errors ({ts:.2f}s)")'),
    
    ('print(f"⏱️ PERFORMANCE SUMMARY")',
     'print("⏱️ PERFORMANCE SUMMARY")'),
    
    ('print(f"✅ ASSESSMENT COMPLETE - SENDING RESPONSE")',
     'print("✅ ASSESSMENT COMPLETE")'),
    
    # HTTPException lines > 79 chars
    ('raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")',
     'raise HTTPException(\n            status_code=500,\n            detail=f"Assessment failed: {str(e)}"\n        )'),
    
    ('raise HTTPException(status_code=400, detail="Age must be between 5 and 100")',
     'raise HTTPException(\n            status_code=400,\n            detail="Age must be 5-100"\n        )'),
    
    ('raise HTTPException(status_code=400, detail="Paragraph must be at least 5 characters")',
     'raise HTTPException(\n            status_code=400,\n            detail="Paragraph >= 5 chars"\n        )'),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ Fixed: {old[:60]}...")

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Done! Fixed multiple long lines")
