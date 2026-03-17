#!/usr/bin/env python
"""
Fix database schema - add missing password_hash column
"""

from sqlalchemy import inspect, text
from database import engine, init_db

def check_and_fix_schema():
    """Check if password_hash column exists, add if missing"""
    
    # Create inspector to check existing tables/columns
    inspector = inspect(engine)
    
    # Check if users table exists
    if 'users' not in inspector.get_table_names():
        print('[WARN] users table does not exist - initializing database...')
        init_db()
        print('[OK] Database tables initialized')
        return
    
    # Get existing columns
    columns = inspector.get_columns('users')
    col_names = [col['name'] for col in columns]
    
    print('Existing columns in users table:')
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
    
    # Check if password_hash exists
    if 'password_hash' in col_names:
        print('\n[OK] password_hash column already exists')
        return
    
    # Add the missing column
    print('\n[!] password_hash column is MISSING')
    print('[*] Adding password_hash column now...')
    
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))
        print('[OK] password_hash column added successfully')
    except Exception as e:
        print(f'[ERROR] Failed to add column: {e}')
        raise

if __name__ == '__main__':
    check_and_fix_schema()
