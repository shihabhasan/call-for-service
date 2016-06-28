import datetime as dt
import pandas as pd
import math
from django.core.management import call_command

from django.core.management.base import BaseCommand

# File fields
# - Internal ID
# - Time Received
# - Time Dispatched
# - Time Arrived
# - Time Closed
# - Street Address
# - City
# - Zip
# - Latitude
# - Longitude
# - Priority
# - District
# - Nature Code
# - Nature Text
# - Close Code
# - Close Text
from core.models import District, Priority, Nature, CloseCode, Call


def isnan(x):
    return x is None or (type(x) == float and math.isnan(x))


def safe_int(x):
    if isnan(x):
        return None
    return int(x)


def safe_datetime(x):
    if x is pd.NaT:
        return None
    return x


def safe_zip(zip):
    if isnan(zip):
        return None
    return zip.strip()[:5]


def safe_sorted(coll):
    return sorted(x for x in coll if not isnan(x))


class Command(BaseCommand):
    help = "Load call for service data from a CSV."

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='The CSV file to load.')
        parser.add_argument('--reset', default=False, action='store_true',
                            help='Whether to clear the database before loading '
                                 '(defaults to False)')

    def clear_database(self):
        self.log("Clearing database")
        call_command("flush", interactive=False)

    def log(self, message):
        if self.start_time:
            current_time = dt.datetime.now()
            period = current_time - self.start_time
        else:
            period = dt.timedelta(0)
        print("[{:7.2f}] {}".format(period.total_seconds(), message))

    def handle(self, *args, **options):
        self.start_time = dt.datetime.now()

        if options['reset']:
            self.clear_database()

        self.batch_size = 2000

        self.log("Loading CSV")
        self.df = pd.read_csv(options['filename'],
                              parse_dates=['Time Received', 'Time Dispatched',
                                           'Time Arrived', 'Time Closed'],
                              dtype={'Internal ID': str, 'District': str,
                                     'Priority': str, 'Nature Code': str,
                                     'Close Code': str, 'Zip': str})

        self.log("CSV loaded")
        self.create_districts()
        self.create_priorities()
        self.create_natures()
        self.create_close_codes()
        self.create_calls()

    def create_calls(self):
        try:
            start = 0
            while start < len(self.df):
                batch = self.df[start:start + self.batch_size]
                calls = []

                for idx, c in batch.iterrows():
                    if Call.objects.filter(pk=c['Internal ID']).count() > 0:
                        continue

                    call = Call(call_id=c['Internal ID'],
                                time_received=safe_datetime(c['Time Received']),
                                first_unit_dispatch=safe_datetime(
                                    c['Time Dispatched']),
                                first_unit_arrive=safe_datetime(
                                    c['Time Arrived']),
                                time_closed=safe_datetime(c['Time Closed']),
                                street_address=c['Street Address'],
                                zip_code=safe_zip(c['Zip']),
                                nature_id=safe_int(c['Nature ID']),
                                priority_id=safe_int(c['Priority ID']),
                                district_id=safe_int(c['District ID']),
                                close_code_id=safe_int(c['Close Code ID']))
                    call.update_derived_fields()
                    calls.append(call)

                Call.objects.bulk_create(calls)
                self.log("Call {}-{} created".format(start, start + len(batch)))
                start += self.batch_size
        except Exception as ex:
            import pdb;
            pdb.set_trace()

    def create_districts(self):
        self.log("Creating districts")
        df = self.df

        district_names = safe_sorted(df['District'].unique())
        districts = [District.objects.get_or_create(descr=name)[0]
                     for name in district_names]
        district_map = {d.descr: d.district_id for d in districts}
        df['District ID'] = df['District'].apply(lambda x: district_map.get(x),
                                                 convert_dtype=False)

    def create_priorities(self):
        self.log("Creating priorities")
        df = self.df

        priority_names = safe_sorted(df['Priority'].unique())
        priorities = [Priority.objects.get_or_create(descr=name)[0]
                      for name in priority_names]
        priority_map = {p.descr: p.priority_id for p in priorities}
        df['Priority ID'] = df['Priority'].apply(lambda x: priority_map.get(x),
                                                 convert_dtype=False)

    def create_natures(self):
        self.log("Creating natures")
        df = self.df

        nature_tuples = [x for x in pd.DataFrame(
            df.groupby("Nature Code")['Nature Text'].min()).itertuples()
                         if x[0]]
        natures = [
            Nature.objects.get_or_create(key=n[0], defaults={'descr': n[1]})[0]
            for n in nature_tuples]
        nature_map = {n.key: n.nature_id for n in natures}
        df['Nature ID'] = df['Nature Code'].apply(lambda x: nature_map.get(x),
                                                  convert_dtype=False)

    def create_close_codes(self):
        self.log("Creating close codes")
        df = self.df

        close_tuples = [cc for cc in pd.DataFrame(
            df.groupby("Close Code")['Close Text'].min()).itertuples()
                        if cc[0]]
        close_codes = [
            CloseCode.objects.get_or_create(code=cc[0],
                                            defaults={'descr': cc[1]})[0]
            for cc in close_tuples]
        close_code_map = {cc.code: cc.close_code_id for cc in close_codes}
        df['Close Code ID'] = df['Close Code'].apply(
            lambda x: close_code_map.get(x),
            convert_dtype=False)
