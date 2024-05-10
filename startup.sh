#!/bin/sh

printf "Running migrations...\n"
# Run Alembic migrations
alembic upgrade heads

# Check for the existence of the alembic_version table
printf "Checking for alembic_version table...\n"
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_SERVER" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT to_regclass('$POSTGRES_SCHEMA.alembic_version');" | grep -q 'alembic_version'; then
    printf "Migrations applied successfully and alembic_version table exists.\n"
else
    printf "Migration check failed or alembic_version table does not exist.\n"
    exit 1
fi

printf "Starting app...\n"
gunicorn -c python_api_template/internal/config/gunicorn.py