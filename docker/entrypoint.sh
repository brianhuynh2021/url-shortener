#!/bin/sh
set -e
echo "Applying migrations (SQLite) and auto-seeding demo data (once)..."
python manage.py migrate --noinput
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
