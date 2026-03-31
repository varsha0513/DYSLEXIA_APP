import re

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix continuation lines for ternary operator
content = content.replace(
    '''        age_info = get_age_group_info(5 if age_group == "4-6" else
                          8 if age_group == "7-9" else
                          11 if age_group == "10-12" else
                          14 if age_group == "13-15" else
                          17 if age_group == "16-18" else 20)''',
    '''        age_info = get_age_group_info(
            5 if age_group == "4-6" else
            8 if age_group == "7-9" else
            11 if age_group == "10-12" else
            14 if age_group == "13-15" else
            17 if age_group == "16-18" else 20
        )'''
)

# Fix "Perform an action" docstring
content = content.replace(
    '    Perform an action on the training session (start, pause, resume, reset, advance).',
    '    Perform an action on the training session (start/pause/resume/reset/advance).'
)

# Fix function signature for perform_session_action
content = content.replace(
    'async def perform_session_action(session_id: str, action_request: SpeedTrainerAction):',
    '''async def perform_session_action(
    session_id: str, action_request: SpeedTrainerAction
):'''
)

# Fix function signature for perform_chunk_reading_action
content = content.replace(
    'async def perform_chunk_reading_action(session_id: str, action_request: ChunkReadingAction):',
    '''async def perform_chunk_reading_action(
    session_id: str, action_request: ChunkReadingAction
):'''
)

# Fix docstring for chunk reading action
content = content.replace(
    '        action_request: Action to perform (start, pause, resume, reset, advance_phrase)',
    '        action_request: Action (start, pause, resume, reset, advance_phrase)'
)

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed continuation lines and function signatures')
