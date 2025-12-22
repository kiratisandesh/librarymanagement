# librarymanagement/fix_utc.py

from django.db.backends.postgresql.utils import utc_tzinfo_factory

# Monkey-patch to disable the UTC assertion
def utc_tzinfo_factory_no_assert(*args, **kwargs):
    import datetime
    return datetime.timezone.utc

# Apply the patch
import django.db.backends.postgresql.utils
django.db.backends.postgresql.utils.utc_tzinfo_factory = utc_tzinfo_factory_no_assert
