from collections import Counter
from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.db.models import Min, Max, Count, Case, When, IntegerField, F, \
    Avg, DurationField, Q
from postgres_stats import Extract, DateTrunc, Percentile
from url_filter.filtersets import StrictMode

from .filters import CallFilterSet
from .models import Call, Beat, NatureGroup, District


def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


class Secs(Extract):
    name = 'secs'

    def __init__(self, expression, **extra):
        super().__init__(expression, subfield='EPOCH', **extra)


class CallOverview:
    def __init__(self, filters):
        self._filters = filters
        self.filter = CallFilterSet(data=filters, queryset=Call.objects.all(),
                                    strict_mode=StrictMode.fail)
        self.bounds = self.qs.aggregate(min_time=Min('time_received'),
                                        max_time=Max('time_received'))
        if self.bounds['max_time'] and self.bounds['min_time']:
            self.span = self.bounds['max_time'] - self.bounds['min_time']
        else:
            self.span = timedelta(0, 0)

    @property
    def qs(self):
        return self.filter.filter()

    def count(self):
        return self.qs.count()

    def precision(self):
        if self.span >= timedelta(days=365):
            return 'month'
        elif self.span >= timedelta(days=7):
            return 'day'
        else:
            return 'hour'

    def merge_data(self, src_data, all_ids):
        src_data = list(src_data)
        all_ids = set(all_ids)
        present_ids = set(x['id'] for x in src_data)

        if len(present_ids) > 0:
            for id in all_ids.difference(present_ids):
                src_data.append(merge_dicts({"id": id}, self.default))

        return src_data

    def beat_ids(self):
        return dict(Beat.objects.all().values_list('descr', 'beat_id'))

    def district_ids(self):
        return dict(District.objects.all().values_list('descr', 'district_id'))

    def by_dow(self):
        results = self.qs \
            .annotate(id=F('dow_received'), name=F('dow_received')) \
            .values("id", "name") \
            .annotate(**self.annotations)

        return self.merge_data(results, range(0, 7))

    def by_shift(self):
        results = self.qs \
            .annotate(id=Case(
            When(Q(hour_received__gte=6) & Q(
                hour_received__lt=18), then=0),
            default=1,
            output_field=IntegerField())) \
            .values("id") \
            .annotate(**self.annotations)

        return self.merge_data(results, [0, 1])

    def by_nature_group(self):
        all_in_field = NatureGroup.objects.annotate(
            name=F("descr"),
            id=F("nature_group_id")).values('name', 'id')

        results = self.qs \
            .annotate(id=F("nature__nature_group_id"),
                      name=F("nature__nature_group__descr")) \
            .values("name", "id") \
            .annotate(**self.annotations)

        results = list(results)

        present_ids = set(x['id'] for x in results)

        if len(present_ids) > 0:
            for row in all_in_field:
                if row['id'] not in present_ids:
                    row.update(**self.default)
                    results.append(row)

        return results

    def by_field(self, field):
        field_model = getattr(self.qs.model, field).field.related_model
        all_in_field = field_model.objects.annotate(
            name=F("descr"),
            id=F(field + "_id")).values('name', 'id')
        results = self.qs \
            .annotate(id=F(field + "_id"),
                      name=F(field + '__descr')) \
            .values("id", "name") \
            .exclude(id=None) \
            .annotate(**self.annotations)

        results = list(results)
        present_ids = set(x['id'] for x in results)

        if results:
            for row in all_in_field:
                if row['id'] not in present_ids:
                    row.update(**self.default)
                    results.append(row)

        return results


class CallVolumeOverview(CallOverview):
    annotations = dict(volume=Count("id"))
    default = dict(volume=0)

    def volume_by_date(self):
        results = self.qs \
            .annotate(
            date=DateTrunc('time_received', precision=self.precision())) \
            .values("date") \
            .annotate(volume=Count("date")) \
            .order_by("date")

        return results

    def volume_by_source(self):
        results = self.qs \
            .annotate(id=Case(
            When(call_source__descr="Self Initiated", then=0),
            default=1,
            output_field=IntegerField())) \
            .values("id") \
            .annotate(**self.annotations)

        return self.merge_data(results, [0, 1])

    def day_hour_heatmap(self):
        if self.span == timedelta(0, 0):
            return []
        # In order for this to show average volume, we need to know the number
        # of times each day of the week occurs.
        start = self.bounds['min_time'].date()
        end = self.bounds['max_time'].date()
        weekdays = Counter((start + timedelta(days=x)).weekday() for x in
                           range(0, (end - start).days + 1))
        results = self.qs \
            .values('dow_received', 'hour_received') \
            .annotate(volume=Count('dow_received')) \
            .order_by('dow_received', 'hour_received')
        for result in results:
            result['freq'] = weekdays[result['dow_received']]
            result['total'] = result['volume']
            try:
                result['volume'] /= result['freq']
            except ZeroDivisionError:
                result['volume'] = 0
        return results

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'bounds': self.bounds,
            'precision': self.precision(),
            'count': self.count(),
            'volume_by_date': self.volume_by_date(),
            'volume_by_source': self.volume_by_source(),
            'volume_by_district': self.by_field('district'),
            'volume_by_beat': self.by_field('beat'),
            'volume_by_nature': self.by_field('nature'),
            'volume_by_nature_group': self.by_nature_group(),
            'volume_by_dow': self.by_dow(),
            'volume_by_shift': self.by_shift(),
            'heatmap': self.day_hour_heatmap(),
            'beat_ids': self.beat_ids(),
            'district_ids': self.district_ids(),
        }


class CallResponseTimeOverview(CallOverview):
    annotations = dict(mean=Avg(Secs("officer_response_time")))
    default = dict(mean=0)

    def officer_response_time(self):
        results = self.qs.filter(
            officer_response_time__gt=timedelta(0)).aggregate(
            avg=Avg(Secs('officer_response_time')),
            quartiles=Percentile(Secs('officer_response_time'),
                                 [0.25, 0.5, 0.75],
                                 output_field=ArrayField(DurationField)),
            max=Max(Secs('officer_response_time')))

        quartiles = results['quartiles']

        if quartiles:
            return {
                'quartiles': quartiles,
                'avg': results['avg'],
                'max': results['max'],
                'iqr': quartiles[2] - quartiles[0]
            }
        else:
            return {}

    def by_field(self, field):
        results = super().by_field(field)
        return sorted(results, key=lambda x: -x['mean'] if x['mean'] else 0)

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'bounds': self.bounds,
            'count': self.count(),
            'officer_response_time': self.officer_response_time(),
            'officer_response_time_by_beat': self.by_field('beat'),
            'officer_response_time_by_priority': self.by_field('priority'),
            'officer_response_time_by_district': self.by_field('district'),
            'officer_response_time_by_nature_group': self.by_nature_group(),
            'officer_response_time_by_dow': self.by_dow(),
            'officer_response_time_by_shift': self.by_shift(),
            'beat_ids': self.beat_ids(),
        }


class CallMapOverview(CallOverview):
    def locations(self):
        return self.qs.values_list('geox', 'geoy', 'street_num', 'street_name',
                                   'business')

    def top_users(self):
        return self.qs. \
            exclude(street_name=""). \
            values('street_num', 'street_name', 'business'). \
            annotate(total=Count('street_num')). \
            order_by('-total')[:20]

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'bounds': self.bounds,
            'count': self.count(),
            'locations': self.locations()
        }


class MapOverview(CallOverview):
    def officer_response_time_by_beat(self):
        results = self.qs \
            .annotate(name=F("beat__descr")) \
            .values("name") \
            .exclude(name=None) \
            .annotate(mean=Avg(Secs("officer_response_time"))) \
            .order_by("-mean")
        return results

    def volume_by_beat(self):
        qs = self.qs \
            .annotate(name=F('beat__descr')) \
            .values('name') \
            .exclude(name=None)

        return qs.annotate(volume=Count('name'))

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'count': self.count(),
            'officer_response_time': self.officer_response_time_by_beat(),
            'call_volume': self.volume_by_beat()
        }


