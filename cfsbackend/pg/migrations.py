from django.db.migrations.operations.base import Operation
from django.db import router

from django.db.migrations.operations import RunSQL

class CreateView(RunSQL):
    reduces_to_sql = True
    reversible = True

    def __init__(self, name):
        self.name = name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        new_model = to_state.apps.get_model(app_label, self.name)
        import pdb; pdb.set_trace()
        sql = new_model._meta.sql

        if router.allow_migrate(schema_editor.connection.alias, app_label):
            self._run_sql(schema_editor, ("CREATE VIEW %s AS %s", (db_table, sql,)))

    def database_backwards(self, app_label, schema_editor, from_state,
                           to_state):
        model = from_state.apps.get_model(app_label, self.name)
        db_table = model._meta.db_table
        if router.allow_migrate(schema_editor.connection.alias, app_label):
            self._run_sql(schema_editor, ("DROP VIEW %s", (db_table,)))

    def describe(self):
        return "Create view"


class UpdateView(Operation):
    reduces_to_sql = True
    reversible = True

    def __init__(self, model_name):
        pass

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state,
                           to_state):
        pass

    def describe(self):
        return "Update view"


class DropView(Operation):
    reduces_to_sql = True
    reversible = True

    def __init__(self, model_name):
        pass

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state,
                           to_state):
        pass

    def describe(self):
        return "Drop view"
