import datetime as dt
import math
import os
import os.path
import re
from itertools import chain
import pandas as pd
from django.db import connection
from django.core.management import call_command
from core.models import *


# TODO
# - call_latlong
# - beat shapefiles


def flatmap(f, items):
    return chain.from_iterable(map(f, items))


def safe_strip(str_):
    if isnan(str_):
        return ''
    try:
        return str_.strip()
    except AttributeError:
        return str_


def strip_dataframe(df):
    string_cols = list(df.select_dtypes(include=['object']).columns)

    for col in string_cols:
        df[col] = df[col].apply(lambda x: safe_strip(x))


def safe_map(m, d):
    return m.get(d) if d else None


def safe_int(x):
    return int(x) if x else None


def safe_datetime(x):
    # to_datetime returns a pandas Timestamp object, and we want a datetime
    try:
        return pd.to_datetime(x).to_datetime() if x not in (
            'NULL', None) else None
    except ValueError:
        return None


def safe_float(x):
    return float(x) if x else None


def safe_bool(x):
    return bool(x)


def clean_case_id(c):
    if c:
        c = str(c).replace('-', '').replace(' ', '')
        try:
            return int(c)
        except ValueError:  # got some weird rows with non-digits in the case_id that def. won't map back to incident
            return None
    return None


def clean_officer_name(name):
    return ', '.join([t.strip() for t in name.split(',')]) if name else ''


timestamp_expr = re.compile(
    "(.*?)\[(\d{2}/\d{2}/(?:\d{2}|\d{4}) \d{2}:\d{2}:\d{2}) (.*?)\]")


def split_notes(notes):
    """
    Return a list of tuples.  Each tuple represents a single note and contains the corresponding call_id,
    the timestamp, the note-taker, and the text of the note.
    """
    tuples = []
    if notes is None or isnan(notes):
        return []
    regex_split = re.findall(timestamp_expr, notes)
    for tup in regex_split:
        text = tup[0].split()
        text = " ".join(text) if text else None  # turn blanks into null
        try:
            timestamp = dt.datetime.strptime(tup[1], "%m/%d/%y %H:%M:%S")
        except ValueError:  # 4 digit year
            timestamp = dt.datetime.strptime(tup[1], "%m/%d/%Y %H:%M:%S")
        author = tup[2] if tup[2] else None
        tuples.append((text, timestamp, author))
    return tuples


def isnan(x):
    return type(x) == float and math.isnan(x)


def unique_clean_values(column):
    return {x.strip()
            for x in pd.unique(column.values)
            if x and not isnan(x) and x.strip()}


class ETL:
    def __init__(self, dir, subsample=None, batch_size=2000):
        self.dir = dir
        self.subsample = subsample
        self.mapping = {}
        self.start_time = None
        self.batch_size = batch_size

    def run(self):
        self.start_time = dt.datetime.now()
        self.clear_database()

        self.calls = self.load_calls()
        self.call_log = self.load_call_log()
        self.in_service = self.load_in_service()

        self.mapping['City'] = self.create_from_calls(column="citydesc",
                                                      model=City,
                                                      to_field="city_id")
        self.mapping['Sector'] = self.create_from_calls(column="ra",
                                                        model=Sector,
                                                        to_field="sector_id")
        self.mapping['District'] = self.create_from_calls(column="district",
                                                          model=District,
                                                          to_field="district_id")
        self.mapping['Beat'] = self.create_from_calls(column="statbeat",
                                                      model=Beat,
                                                      to_field="beat_id")
        self.mapping['Nature'] = self.create_from_calls(column="nature",
                                                        model=Nature,
                                                        to_field="nature_id")
        self.mapping['ZipCode'] = self.create_from_calls(column="zip",
                                                         model=ZipCode,
                                                         to_field="zip_code_id")
        self.mapping['Priority'] = self.create_from_calls(column="priority",
                                                          model=Priority,
                                                          to_field="priority_id")
        self.mapping['CallSource'] = self.create_from_lookup(
            model=CallSource,
            filename="inmain.callsource.tsv",
            mapping={"descr": "Description"},
            code_column="code_agcy",
            to_field="call_source_id")
        self.mapping['CallUnit'] = self.create_call_units()
        self.mapping['CloseCode'] = self.create_from_lookup(
            filename="inmain.closecode.tsv",
            model=CloseCode,
            mapping={"descr": "Description"},
            code_column="code_agcy",
            to_field="close_code_id")
        self.mapping['Bureau'] = self.create_from_lookup(
            filename="LWMAIN.EMUNIT.csv",
            model=Bureau,
            mapping={"descr": "descriptn"},
            code_column="code_agcy",
            to_field="bureau_id")
        self.mapping['Unit'] = self.create_from_lookup(
            filename="LWMAIN.EMSECTION.csv",
            model=Unit,
            mapping={"descr": "descriptn"},
            code_column="code_agcy",
            to_field="unit_id")
        self.mapping['Division'] = self.create_from_lookup(
            filename="LWMAIN.EMDIVISION.csv",
            model=Division,
            mapping={"descr": "descriptn"},
            code_column="code_agcy",
            to_field="division_id")
        self.mapping['OOSCode'] = self.create_from_lookup(
            filename="outserv.oscode.tsv",
            model=OOSCode,
            mapping={"descr": "Description"},
            code_column="Code",
            to_field="oos_code_id"
        )
        self.mapping['NoteAuthor'] = self.create_note_authors()
        self.mapping['Shift'] = self.create_shifts()
        self.mapping['Officer'] = self.create_officers()
        self.mapping['Transaction'] = self.create_transactions()

        self.connect_beats_districts_sectors()
        self.connect_call_unit_squads()

        self.create_calls()

        self.shrink_call_log()
        self.create_shift_units()
        self.create_out_of_service()
        self.create_call_log()

        self.log("Updating materialized views")
        update_materialized_views()

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

    def map(self, model_name, value):
        return safe_map(self.mapping[model_name], value)

    def load_calls(self):
        self.log("Loading calls...")

        filename = os.path.join(self.dir, "cfs_2014_inmain.csv")
        df = pd.read_csv(filename, encoding='ISO-8859-1',
                         dtype={"streetno": "object"})
        strip_dataframe(df)

        if self.subsample:
            df = df.sample(frac=self.subsample)

        return df

    def create_from_calls(self, column, model, to_field, from_field='descr'):
        self.log("Creating {} data from calls...".format(model.__name__))
        xs = unique_clean_values(self.calls[column])
        model.objects.bulk_create(model(**{from_field: x}) for x in xs)
        return dict(model.objects.values_list(from_field, to_field))

    def create_from_lookup(self, model, filename, mapping, code_column,
                           to_field, from_field='code'):
        self.log("Creating {} data from {}...".format(model.__name__, filename))
        model_data = {}

        if filename.endswith(".csv"):
            data = pd.read_csv(os.path.join(self.dir, filename))
        elif filename.endswith(".tsv"):
            data = pd.read_csv(os.path.join(self.dir, filename), sep='\t')

        for idx, row in data.iterrows():
            md = {}
            for k, v in mapping.items():
                md[k] = row[v]
            model_data[row[code_column]] = md

        model.objects.bulk_create(
            model(code=k, **v) for k, v in model_data.items())
        return dict(model.objects.values_list(from_field, to_field))

    def create_call_units(self):
        self.log("Creating call units...")
        units = list(self.calls.primeunit.values) + list(
            self.calls.firstdisp.values) + list(self.calls.reptaken.values)
        units += list(self.in_service.unitcode.values)
        units += list(self.call_log.unitcode.values)
        unitset = {unit.strip() for unit in units if
                   unit and not isnan(unit) and unit.strip()}
        CallUnit.objects.bulk_create(CallUnit(descr=unit) for unit in unitset)
        return dict(CallUnit.objects.values_list('descr', 'call_unit_id'))

    def create_note_authors(self):
        self.log("Creating note authors...")
        notes = flatmap(split_notes, self.calls.notes.values)
        note_authors = set()
        for note in notes:
            if note[2] is not None:
                note_authors.add(note[2])
        NoteAuthor.objects.bulk_create(
            [NoteAuthor(descr=n) for n in note_authors])
        return dict(NoteAuthor.objects.values_list('descr', 'note_author_id'))

    def create_calls(self):
        try:
            start = 0
            while start < len(self.calls):
                batch = self.calls[start:start + self.batch_size]
                calls = []
                notes = []

                for idx, c in batch.iterrows():
                    call = Call(call_id=c.inci_id,
                                time_received=safe_datetime(c.calltime),
                                case_id=clean_case_id(c.case_id),
                                call_source_id=self.map('CallSource',
                                                        c.callsource),
                                primary_unit_id=self.map('CallUnit',
                                                         c.primeunit),
                                first_dispatched_id=self.map('CallUnit',
                                                             c.firstdisp),
                                street_num=safe_int(c.streetno),
                                street_name=c.streetonly,
                                city_id=self.map('City', c.citydesc),
                                zip_code_id=self.map('ZipCode', c.zip),
                                crossroad1=c.crossroad1,
                                crossroad2=c.crossroad2,
                                geox=safe_float(c.geox),
                                geoy=safe_float(c.geoy),
                                beat_id=self.map('Beat', c.statbeat),
                                district_id=self.map('District', c.district),
                                sector_id=self.map('Sector', c.ra),
                                business=c.business,
                                nature_id=self.map('Nature', c.nature),
                                priority_id=self.map('Priority', c.priority),
                                report_only=safe_bool(c.rptonly),
                                cancelled=safe_bool(c.cancelled),
                                time_routed=safe_datetime(c.timeroute),
                                time_finished=safe_datetime(c.timefini),
                                first_unit_dispatch=safe_datetime(c.firstdtm),
                                first_unit_enroute=safe_datetime(c.firstenr),
                                first_unit_arrive=safe_datetime(c.firstarrv),
                                last_unit_clear=safe_datetime(c.lastclr),
                                time_closed=safe_datetime(c.timeclose),
                                reporting_unit_id=self.map('CallUnit',
                                                           c.reptaken),
                                close_code_id=self.map('CloseCode',
                                                       c.closecode),
                                close_comments=c.closecomm)
                    call.update_derived_fields()

                    _notes = split_notes(c.notes)
                    for n in _notes:
                        if n[0]:
                            note = Note(call_id=call.call_id,
                                        note_author_id=self.map('NoteAuthor',
                                                                n[2]),
                                        body=n[0],
                                        time_recorded=n[1])
                            notes.append(note)

                    calls.append(call)

                Call.objects.bulk_create(calls)
                Note.objects.bulk_create(notes)
                self.log("Call {}-{} created".format(start, start + len(batch)))
                start += self.batch_size
        except ValueError as ex:
            import pdb;
            pdb.set_trace()

    def connect_beats_districts_sectors(self):
        self.log("Connecting beats to districts and sectors...")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE beat
                SET district_id = (
                  SELECT district_id
                  FROM district
                  WHERE district.descr = 'D' || SUBSTRING(beat.descr::text FROM 1 FOR 1)
                )
                WHERE beat.descr NOT IN ('DSO', 'OOJ');
            """)
            cursor.execute("""
                UPDATE beat
                SET sector_id = (
                  SELECT sector_id
                  FROM sector
                  WHERE sector.descr = 'NTH')
                WHERE beat.district_id IN (
                  SELECT district_id
                  FROM district
                  WHERE district.descr IN ('D2', 'D1', 'D5')
                );
            """)
            cursor.execute("""
                UPDATE beat
                SET sector_id = (
                  SELECT sector_id
                  FROM sector
                  WHERE sector.descr = 'STH')
                WHERE beat.district_id IN (
                  SELECT district_id
                  FROM district
                  WHERE district.descr IN ('D3', 'D4')
                );
            """)
            cursor.execute("""
                UPDATE district
                SET sector_id = (
                SELECT sector_id
                  FROM sector
                  WHERE sector.descr = 'STH')
                WHERE district.descr IN ('D3', 'D4');
            """)
            cursor.execute("""
                UPDATE district
                SET sector_id = (
                SELECT sector_id
                  FROM sector
                  WHERE sector.descr = 'NTH')
                WHERE district.descr IN ('D2', 'D1', 'D5');
            """)

    def connect_call_unit_squads(self):
        self.log("Connecting call units and squads...")
        call_unit_squad_regexes = {
            'A': '^A[1-5][0-9]{2}$',
            'B': '^B[1-5][0-9]{2}$',
            'C': '^C[1-5][0-9]{2}$',
            'D': '^D[1-5][0-9]{2}$',
            'BIKE': '^L5[0-9]{2}$',
            'HEAT': '^H[1-4][0-9]{2}$',
            'K9': '^K[0-9]{2}$',
            'MOTORS': '^MTR[2-8]$',
            'TACT': '^T[2-8]$',
            'VIR': '^ED6[0-6]$'
        }

        Squad.objects.bulk_create(
            Squad(descr=s) for s in call_unit_squad_regexes.keys())
        self.mapping['Squad'] = dict(
            Squad.objects.values_list('descr', 'squad_id'))

        for squad, regex in call_unit_squad_regexes.items():
            CallUnit.objects.filter(descr__regex=regex).update(
                squad_id=self.map('Squad', squad))

    def load_in_service(self):
        self.log("Loading in service data...")
        filename = os.path.join(self.dir, "cfs_2014_unitper.csv")
        df = pd.read_csv(filename, encoding='ISO-8859-1',
                         dtype={"name": "object", 'emdept_id': "object"})
        strip_dataframe(df)

        if self.subsample:
            df = df.sample(frac=self.subsample)

        return df

    def create_shifts(self):
        self.log("Create shifts from in service data...")
        shift_ids = set(pd.unique(self.in_service.unitperid.values))
        Shift.objects.bulk_create(Shift(shift_id=id) for id in shift_ids)
        return dict(Shift.objects.values_list('shift_id', 'shift_id'))

    def create_officers(self):
        self.log("Creating officers from in service data...")
        officers = {}
        for idx, row in self.in_service.iterrows():
            id = row.officerid
            name = clean_officer_name(row['name'])

            if id not in officers:
                if name.isdigit():
                    officers[id] = {'name_aka': [name]}
                else:
                    officers[id] = {'name': name, 'name_aka': []}
            else:
                if ('name' in officers[id] or name.isdigit()) and \
                        name and name not in officers[id]['name_aka'] and \
                                name != officers[id]['name']:
                    officers[id]['name_aka'].append(name)
                elif not ('name' in officers[id] or name.isdigit()):
                    officers[id]['name'] = name
        Officer.objects.bulk_create(
            Officer(officer_id=k, **v) for k, v in officers.items())
        return dict(Officer.objects.values_list('name', 'officer_id'))

    def create_shift_units(self):
        try:
            start = 0
            while start < len(self.in_service):
                batch = self.in_service[start:start + self.batch_size]
                shift_units = []

                for idx, s in batch.iterrows():
                    shift_unit = ShiftUnit(shift_unit_id=s.primekey,
                                           shift_id=self.map('Shift',
                                                             s.unitperid),
                                           call_unit_id=self.map('CallUnit',
                                                                 s.unitcode),
                                           officer_id=safe_int(s.officerid),
                                           in_time=safe_datetime(s.intime),
                                           out_time=safe_datetime(s.outtime),
                                           bureau_id=self.map('Bureau',
                                                              s.emunit),
                                           division_id=self.map('Division',
                                                                s.emdivision),
                                           unit_id=self.map('Unit',
                                                            s.emsection))

                    shift_units.append(shift_unit)

                ShiftUnit.objects.bulk_create(shift_units)
                self.log(
                    "ShiftUnit {}-{} created".format(start, start + len(batch)))
                start += self.batch_size
        except ValueError as ex:
            import pdb;
            pdb.set_trace()

    def create_out_of_service(self):
        filename = os.path.join(self.dir, "cfs_2014_outserv.csv")
        df = pd.read_csv(filename, encoding='ISO-8859-1')
        strip_dataframe(df)

        start = 0
        while start < len(df):
            batch = df[start:start + self.batch_size]
            ooss = []

            for idx, s in batch.iterrows():
                oos = OutOfServicePeriod(oos_id=safe_int(s.outservid),
                                         call_unit_id=self.map('CallUnit',
                                                               s.unitcode),
                                         oos_code_id=self.map('OOSCode',
                                                              s.oscode),
                                         location=s.location,
                                         comments=s.comments,
                                         start_time=safe_datetime(s.starttm),
                                         end_time=safe_datetime(s.endtm),
                                         shift_id=self.map('Shift',
                                                           s.unitperid))
                oos.update_derived_fields()
                ooss.append(oos)

            OutOfServicePeriod.objects.bulk_create(ooss)
            self.log("OutOfServicePeriod {}-{} created".format(start,
                                                               start + len(
                                                                   batch)))
            start += self.batch_size

    def load_call_log(self):
        self.log("Loading call log...")
        months = (
            "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
            "oct", "nov", "dec")
        dfs = []
        for month in months:
            filename = os.path.join(self.dir,
                                    "cfs_{}2014_incilog.csv".format(month))
            if not os.path.isfile(filename):
                continue
            dfs.append(pd.read_csv(filename, encoding='ISO-8859-1'))
        df = pd.concat(dfs)
        strip_dataframe(df)

        df['transtype'] = df['transtype'].map(lambda x: x.upper())
        return df

    def shrink_call_log(self):
        self.log("Removing fire and EMS calls from call log...")
        call_ids = set(Call.objects.all().values_list('call_id', flat=True))
        criterion = self.call_log['inci_id'].map(lambda id: id in call_ids)
        df = self.call_log.loc[criterion]
        self.call_log = df

    def create_transactions(self):
        self.log("Creating transactions from call log...")
        transactions = {}

        trans_data = self.call_log[["transtype", "descript"]]
        grouped = trans_data.groupby("transtype")
        for code, row in grouped.first().iterrows():
            transactions[code] = row.descript

        Transaction.objects.bulk_create(
            Transaction(code=code, descr=descr) for code, descr in
            transactions.items())
        return dict(Transaction.objects.values_list('code', 'transaction_id'))

    def create_call_log(self):
        try:
            start = 0
            while start < len(self.call_log):
                batch = self.call_log[start:start + self.batch_size]
                cls = []

                for idx, s in batch.iterrows():
                    cl = CallLog(call_log_id=safe_int(s.incilogid),
                                 transaction_id=self.map('Transaction',
                                                         s.transtype),
                                 time_recorded=safe_datetime(s.timestamp),
                                 call_id=safe_int(s.inci_id),
                                 call_unit_id=self.map('CallUnit', s.unitcode),
                                 shift_id=self.map('Shift', s.unitperid),
                                 close_code_id=self.map('CloseCode',
                                                        s.closecode))
                    cls.append(cl)

                CallLog.objects.bulk_create(cls)
                self.log(
                    "CallLog {}-{} created".format(start, start + len(batch)))
                start += self.batch_size
        except ValueError as ex:
            import pdb;
            pdb.set_trace()

    def create_nature_groups(self):
        self.log("Creating nature groups...")
        filename = os.path.join(self.dir, "nature_grouping.csv")
        df = pd.read_csv(filename, encoding='ISO-8859-1')
        strip_dataframe(df)

        groups = unique_clean_values(df['group'])
        NatureGroup.objects.bulk_create(NatureGroup(descr=g) for g in groups)
        self.mapping['NatureGroup'] = dict(NatureGroup.objects.values_list('descr', 'nature_group_id'))

        for idx, row in df.iterrows():
            Nature.objects.filter(descr=row['nature']).update(nature_group_id=self.map('NatureGroup', row['group']))