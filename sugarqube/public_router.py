class PublicRouter:
    """
    A router to control all database operations on models in the
    blog and support applications.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ('blog', 'support'):
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ('blog', 'support'):
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the blog or support app is involved.
        """
        if (
            obj1._meta.app_label in ('blog', 'support') or
            obj2._meta.app_label in ('blog', 'support')
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ('blog', 'support'):
            return db == 'default'
        return None