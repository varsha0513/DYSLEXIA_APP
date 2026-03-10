$env:PGPASSWORD='12Varsh@0513'; & "C:\Program Files\PostgreSQL\18\bin\psql" -h localhost -U dyslexia_user -d dyslexia_db-- Create dyslexia_user role
CREATE USER dyslexia_user WITH PASSWORD '12Varsh@0513';

-- Create dyslexia_db database
CREATE DATABASE dyslexia_db OWNER dyslexia_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dyslexia_db TO dyslexia_user;

-- Connect to dyslexia_db and grant schema privileges
\c dyslexia_db
GRANT ALL ON SCHEMA public TO dyslexia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dyslexia_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dyslexia_user;
