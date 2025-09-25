class CredentialsRouter:
    """
    A router to control all database operations on models in the
    auth, contenttypes, sessions, and admin applications.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ('users', 'auth', 'contenttypes', 'sessions', 'admin', 'notifications'):
            return 'credentials'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ('users', 'auth', 'contenttypes', 'sessions', 'admin'):
            return 'credentials'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in ('users', 'auth', 'contenttypes', 'sessions', 'admin') or
            obj2._meta.app_label in ('users', 'auth', 'contenttypes', 'sessions', 'admin')
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ('users', 'auth', 'contenttypes', 'sessions', 'admin'):
            return db == 'credentials'
        return None