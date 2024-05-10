#! /usr/bin/env bash

# Load environment variables from .env file
export "$(grep -v '^#' .env | xargs)"

printf "Running migrations...\n"
# Run Alembic migrations
alembic upgrade heads

printf "Starting app in development mode with Uvicorn...\n"
uvicorn "${APP_NAME}".main:app --host "${APP_HOST}" --port "${APP_PORT}" --reload
