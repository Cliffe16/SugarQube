class SugarPricesRouter:
    """
    A router to control all database operations on models in the
    'market' and 'dashboard' applications.
    """
    # Define the apps that this router will manage.
    route_app_labels = {'market', 'dashboard'}

    # Define the apps that this router must NOT handle.
    # This is the crucial addition.
    excluded_app_labels = {'auth', 'contenttypes', 'sessions', 'admin', 'users', 'notifications', 'support', 'blog', 'trading_engine'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.excluded_app_labels:
            return 'default' # Explicitly send to 'default'
        if model._meta.app_label in self.route_app_labels:
            return 'sugarprices'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.excluded_app_labels:
            return 'default' # Explicitly send to 'default'
        if model._meta.app_label in self.route_app_labels:
            return 'sugarprices'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # If both models are in apps managed by this router, allow the relation.
        if obj1._meta.app_label in self.route_app_labels and \
           obj2._meta.app_label in self.route_app_labels:
            return True
        # If one model is managed and the other is not, disallow relations.
        # This prevents accidental cross-database foreign keys.
        elif obj1._meta.app_label in self.route_app_labels or \
             obj2._meta.app_label in self.route_app_labels:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'sugarprices'
        # For all other apps, ensure they only migrate on the 'default' db.
        # This router should not allow them on the 'sugarprices' db.
        elif db == 'sugarprices':
            return False
        return None