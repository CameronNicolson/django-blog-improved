from django.urls import resolve
from django.conf import settings

from threading import local

from django.db import connections

# Thread-local storage for database selection
_db_context = local()

from django.utils.deprecation import MiddlewareMixin

class DatabaseSwitcher:
    """
    A database router that switches queries to a dynamically selected database.
    The database name is set at the beginning of a request and used throughout.
    """

    @staticmethod
    def set_db(db_name):
        """Set the current database for this request thread."""
        _db_context.db_name = db_name if db_name in connections.databases else "default"

    @staticmethod
    def get_db():
        """Get the currently active database for this request."""
        return getattr(_db_context, "db_name", "default")

    def db_for_read(self, model, **hints):
        """Route read operations to the dynamically selected database."""
        return self.get_db()

    def db_for_write(self, model, **hints):
        """Route write operations to the dynamically selected database."""
        return self.get_db()

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Allow migrations on the default database."""
        return db == "default"

class DynamicDatabaseMiddleware(MiddlewareMixin):
    """
    Middleware to dynamically switch the database for the entire request.
    This allows ORM queries in templates and views to automatically use the selected database.
    """

    def process_request(self, request, *args, **kwargs):
        try:
            resolver_match = resolve(request.path)  # Get view info
            request.resolved_view_name = resolver_match.view_name  # Store view name
            request.kwargs = resolver_match.kwargs  # Extract URL kwargs

            group = request.kwargs["group_name"]
            example = request.kwargs["example_name"]
            example_ident = str(group + example).lower()
            db_name = settings.EXAMPLES[example_ident]["database"]
        except KeyError:
            db_name = "default"
        if db_name:
            DatabaseSwitcher.set_db(db_name)
