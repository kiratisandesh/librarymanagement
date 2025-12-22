from django.apps import AppConfig


class LibraryConfig(AppConfig):
    name = 'library'
    
    def ready(self):
        # This function runs when Django starts up.
        # Importing the db_timezone file here guarantees the signal handler 
        # is connected BEFORE the migration system checks the connection.
        import library.db_timezone