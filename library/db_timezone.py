from django.db.backends.signals import connection_created
from django.db.backends.postgresql.base import DatabaseWrapper
from django.db.backends.postgresql.utils import utc_tzinfo_factory

def register_utc_timezone(sender, connection, **kwargs):
    """
    Forces the PostgreSQL connection to use UTC timezone check on creation.
    This resolves the "database connection isn't set to UTC" assertion error.
    """
    if isinstance(connection, DatabaseWrapper):
        # Explicitly set the session timezone before any checks occur
        # We ensure the connection cursor is used directly here
        if connection.connection is not None:
             connection.connection.cursor().execute("SET TIME ZONE 'UTC'")
             connection.ensure_timezone() # Now run the check after setting it manually

# Connect the signal handler
connection_created.connect(register_utc_timezone)