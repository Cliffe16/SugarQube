class SugarPricesRouter:
    """
    A router to control all database operations on models in the
    dashboard and trading applications.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ('dashboard', 'trading'):
            return 'sugarprices'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ('dashboard', 'trading'):
            return 'sugarprices'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the dashboard or trading app is involved.
        """
        if (
            obj1._meta.app_label in ('dashboard', 'trading') or
            obj2._meta.app_label in ('dashboard', 'trading')
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ('dashboard', 'trading'):
            return db == 'sugarprices'
        return None