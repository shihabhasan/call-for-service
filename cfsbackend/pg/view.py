from django.db import models, connection

# Create your views here.

models.options.DEFAULT_NAMES += ('sql',)


class ViewManager(models.Manager):
    def bulk_create(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def get_or_create(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

class View(models.Model):
    objects = ViewManager()

    class Meta:
        abstract = True
        managed = False

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        raise NotImplementedError

class MaterializedView(View):
    @classmethod
    def update_view(cls):
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW {}".format(cls._meta.db_table))

    class Meta:
        abstract = True
        managed = False
