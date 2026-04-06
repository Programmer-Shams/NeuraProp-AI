-- Initialize pgvector extension and app user
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create a role for the application that respects RLS
-- (The default superuser bypasses RLS, so we need an app-level role)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'neuraprop_app') THEN
        CREATE ROLE neuraprop_app LOGIN PASSWORD 'neuraprop_app';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE neuraprop TO neuraprop_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO neuraprop_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO neuraprop_app;
