# core/pre_migrate_utc.py
# Ensures UTC across all DB aliases immediately before migrations execute.
from django.db import connections
from django.db.models.signals import pre_migrate

def _ensure_utc_before_migrate(sender, **kwargs):
    for alias in connections:
        conn = connections[alias]
        if conn.vendor == "postgresql":
            with conn.cursor() as cursor:
                cursor.execute("SET TIME ZONE 'UTC'")

pre_migrate.connect(_ensure_utc_before_migrate)
