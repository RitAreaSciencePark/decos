# Copyright (c) 2025 Marco Prenassi
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-02-25
# Description:
# Database router for PRP_CDM_app, ensuring that all database operations related to PRP_CDM_app 
# are directed to the external database (prpmetadata-db) while preventing unintended replication 
# of unrelated tables. This router enforces strict database isolation, allowing inter-database 
# relations only when necessary. The migration policy guarantees that each database contains 
# only the relevant schema, avoiding conflicts and redundant table creation.
#
# Additionally, this routing mechanism ensures a clear separation between the common data model 
# ontology and the service tables of the web application. By isolating PRP_CDM_app’s schema, 
# it prevents structural interference between core research data and the operational components 
# of the web application.
#
# Important Notes:
# - All migration operations must be executed separately for each database:
#   `python3 manage.py migrate && python3 manage.py migrate --database=external_generic_db`
#   This ensures proper schema synchronization across both databases.
# - Relations involving models from PRP_CDM_app are explicitly permitted, while all others defer 
#   to Django’s default behavior.
# - This router isolates PRP_CDM_app’s schema to improve database performance and integrity 
#   within the multi-database architecture.
#
# WHY 2 databases? It ensures that the operations are directed

# to the external common data model database while maintaining separation from web application service tables.
class ExternalDbRouter:

    route_app_labels = {"PRP_CDM_app"}  # Set of apps managed by this router.

    # Determines the database for read operations.
    # Returns 'prpmetadata-db' for PRP_CDM_app models, otherwise falls back to Django’s default routing.
    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'prpmetadata-db'
        return None  # Use default database for other apps.

    # Determines the database for write operations.
    # Routes PRP_CDM_app models to 'prpmetadata-db'.
    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'prpmetadata-db'
        return None  # Use default database for other apps.

    # Allows relations between models if at least one belongs to PRP_CDM_app.
    # Ensures compatibility in cases where models from different databases require associations.
    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None  # Defer decision to Django's default behavior.

    # Determines whether a model can be migrated to a given database.
    # - PRP_CDM_app models are migrated exclusively to 'prpmetadata-db'.
    # - Models from other applications remain in the default database.
    # - Prevents unnecessary table replication by ensuring proper schema isolation.
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'prpmetadata-db':
            return app_label in self.route_app_labels  # Only migrate PRP_CDM_app models.

        # Prevent external models from being migrated into the default database.
        if app_label in self.route_app_labels:
            return False

        return None  # Defer other migration decisions to Django’s default behavior.
