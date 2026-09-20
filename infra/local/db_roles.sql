-- Local development DB role setup (14 §46 PKG-25: "Service identity
-- and DB principals" -- "migration_owner, api_reader,
-- governed_commit_writer, ai_gateway_writer, projection_writer,
-- recovery_reader, security_event_writer, audit_reader,
-- test_principal. No runtime superuser.").
--
-- Run once against the local `postgres` container after it is up:
--   psql "$DATABASE_URL" -f infra/local/db_roles.sql
-- (or, from outside the container: `docker compose exec -T postgres
-- psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
-- -f - < infra/local/db_roles.sql`).
--
-- Idempotent: safe to re-run. Every role is created NOSUPERUSER,
-- NOCREATEDB, NOCREATEROLE, NOBYPASSRLS -- 14's own "No runtime
-- superuser" requirement, verified for real by
-- `tests/security/test_db_principals.py::test_no_principal_is_a_superuser_or_can_create_roles_or_databases`.
-- Table-level GRANTs are NOT made here -- those live in
-- `migrations/versions/*_service_identity_db_principals.py`, which
-- assumes these roles already exist (a real Postgres error if a role
-- is missing is the correct "fail technically" behavior, not a
-- silent no-op).
--
-- LOCAL-DEV-ONLY passwords, matching `docker-compose.yml`'s own
-- existing `nquiry_local_dev_only` convention -- never used for a real
-- deployment (11 §23 SECRET MANAGEMENT; a production credential
-- source is `GAP-14-001`-adjacent future work, disclosed, not solved
-- here).

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'migration_owner') THEN
        CREATE ROLE migration_owner LOGIN PASSWORD 'migration_owner_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'api_reader') THEN
        CREATE ROLE api_reader LOGIN PASSWORD 'api_reader_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'governed_commit_writer') THEN
        CREATE ROLE governed_commit_writer LOGIN PASSWORD 'governed_commit_writer_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_gateway_writer') THEN
        CREATE ROLE ai_gateway_writer LOGIN PASSWORD 'ai_gateway_writer_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'projection_writer') THEN
        CREATE ROLE projection_writer LOGIN PASSWORD 'projection_writer_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'recovery_reader') THEN
        CREATE ROLE recovery_reader LOGIN PASSWORD 'recovery_reader_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'security_event_writer') THEN
        CREATE ROLE security_event_writer LOGIN PASSWORD 'security_event_writer_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'audit_reader') THEN
        CREATE ROLE audit_reader LOGIN PASSWORD 'audit_reader_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'test_principal') THEN
        CREATE ROLE test_principal LOGIN PASSWORD 'test_principal_local_dev_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
END
$$;
