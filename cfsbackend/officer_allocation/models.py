from django.db import models
from django.db import connection
from pg.view import MaterializedView
from core.models import DateTimeNoTZField, Call, CallUnit, ModelWithDescr, Shift


class OfficerActivity(MaterializedView):
    officer_activity_id = models.IntegerField(primary_key=True,
                                              db_column="discrete_officer_activity_id")
    call_unit = models.ForeignKey(CallUnit,
                                  db_column="call_unit_id",
                                  related_name="+")
    time = DateTimeNoTZField(db_column="time_")
    activity_type = models.ForeignKey('OfficerActivityType',
                                      db_column="officer_activity_type_id",
                                      related_name="+")
    call = models.ForeignKey(Call, blank=True, null=True,
                             db_column="call_id",
                             related_name="+",
                             on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'discrete_officer_activity'
        managed = False

    @classmethod
    def update_view(cls):
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW officer_activity")
            cursor.execute(
                "REFRESH MATERIALIZED VIEW discrete_officer_activity")


class OfficerActivityType(ModelWithDescr):
    officer_activity_type_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'officer_activity_type'


class InCallPeriod(MaterializedView):
    in_call_id = models.IntegerField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, db_column="call_unit_id",
                                  related_name="+")
    shift = models.ForeignKey(Shift, db_column="shift_id",
                              related_name="+")
    call = models.ForeignKey(Call, db_column="call_id",
                             related_name="+",
                             on_delete=models.DO_NOTHING)
    start_time = DateTimeNoTZField()
    end_time = DateTimeNoTZField()

    class Meta:
        db_table = 'in_call'
        managed = False


class OOSCode(ModelWithDescr):
    oos_code_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'oos_code'


class OutOfServicePeriod(models.Model):
    oos_id = models.AutoField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    shift = models.ForeignKey(Shift, blank=True, null=True)
    oos_code = models.ForeignKey(OOSCode, blank=True, null=True,
                                 db_column="oos_code_id",
                                 related_name="+")
    location = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    start_time = DateTimeNoTZField(blank=True, null=True)
    end_time = DateTimeNoTZField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)

    def update_derived_fields(self):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time

    class Meta:
        db_table = 'out_of_service'

