
import dataset
import datetime as dt
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

# CHANGE CREDENTIALS AS APPROPRIATE
sqlalchemy_uri = 'postgresql://datascientist:1234thumbwar@localhost:5432/cfs'


db = dataset.connect(sqlalchemy_uri)
engine = create_engine(sqlalchemy_uri)

import csv
import re

# There are a million of these, so let's make life easier and reuse all that code

# We need to save the mapping between DPD's short codes and our database ids so we can apply it to the records
# in the main tables
#
# These have the DPD's codes as keys and our internal database PKs as values
case_status_code_mapping = {}
division_code_mapping = {}
unit_code_mapping = {}
bureau_code_mapping = {}
investigation_status_code_mapping = {}
call_source_code_mapping = {}
close_code_mapping = {}
oos_code_mapping = {}

lookup_jobs = [
    {
        "file": "LWMAIN.CSSTATUS.csv",
        "table": "case_status",
        "mapping": {"descriptn": "descr"},
        "code_column": "code_agcy",
        "code_mapping": case_status_code_mapping
    },
    {
        "file": "LWMAIN.EMDIVISION.csv",
        "table": "division",
        "mapping": {"descriptn": "descr"},
        "code_column": "code_agcy",
        "code_mapping": division_code_mapping
    },
    {
        "file": "LWMAIN.EMSECTION.csv",
        "table": "unit",
        "mapping": {"descriptn": "descr"},
        "code_column": "code_agcy",
        "code_mapping": unit_code_mapping
    },
    {
        "file": "LWMAIN.EMUNIT.csv",
        "table": "bureau",
        "mapping": {"descriptn": "descr"},
        "code_column": "code_agcy",
        "code_mapping": bureau_code_mapping
    },
    {
        "file": "LWMAIN.INVSTSTATS.csv",
        "table": "investigation_status",
        "mapping": {"descriptn": "descr"},
        "code_column": "code_agcy",
        "code_mapping": investigation_status_code_mapping
    },
    {
        "file": "inmain.callsource.tsv",
        "table": "call_source",
        "mapping": {"Description": "descr"},
        "code_column": "code_agcy",
        "code_mapping": call_source_code_mapping
    },
    {
        "file": "inmain.closecode.tsv",
        "table": "close_code",
        "mapping": {"Description": "descr"},
        "code_column": "code_agcy",
        "code_mapping": close_code_mapping
    },
    {
        "file": "outserv.oscode.tsv",
        "table": "oos_code",
        "mapping": {"Description": "descr"},
        "code_column": "Code",
        "code_mapping": oos_code_mapping
    }
]

for job in lookup_jobs:
    print("loading %s into %s" % (job['file'], job['table']))
    
    if job['file'].endswith(".csv"):
        data = pd.read_csv("../csv_data/%s" % (job['file']))
    elif job['file'].endswith(".tsv"):
        data = pd.read_csv("../csv_data/%s" % (job['file']), sep='\t')
    
    # Keep track of the ids, as the data is ordered, so these will be the same assigned by the incrementing
    # primary key in the database.
    id_ = 1    
    for (i,row) in data.iterrows():
        job['code_mapping'][row[job['code_column']]] = id_
        id_ += 1

    # Keep only the desired columns
    keep_columns = set(job['mapping'].keys())
    for c in data.columns:
        if c not in keep_columns:
            data = data.drop(c, axis=1)
            
    # Change the column names to the ones we want and insert the data
    data.rename(columns=job['mapping'], inplace=True)
    data.to_sql(job['table'], engine, index=False, if_exists='append')
    
# They neglected to give us this code which is frequently in the database
investigation_status_code_mapping['CBA'] = None

# Some more that are in the db but not the lookup table they gave us
for bogus_code in ('15:13.0', 'SLFIN', 'EYE', 'WALK', '911', 'A'):
    call_source_code_mapping[bogus_code] = None



def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_
    

timestamp_expr = re.compile("(.*?)\[(\d{2}/\d{2}/(?:\d{2}|\d{4}) \d{2}:\d{2}:\d{2}) (.*?)\]")

# We'll use this to ensure we either map to a value of the foreign key or null
def safe_map(m,d):
    return m[d] if d else None

# We have several columns we need to convert to int that can also be None
def safe_int(x):
    return int(x) if x else None

def safe_float(x):
    return float(x) if x else None

def safe_bool(x):
    return True if x == '1' else False if x == '0' else None

def safe_datetime(x):
    # to_datetime returns a pandas Timestamp object, and we want a vanilla datetime
    return pd.to_datetime(x).to_datetime() if x not in ('NULL', None) else None

def clean_case_id(c):
    if c:
        c = str(c).replace('-','').replace(' ','')
        try:
            return int(c)
        except ValueError: #got some weird rows with non-digits in the case_id that def. won't map back to incident
            return None
    return None

def split_notes(notes):
    """
    Return a list of tuples.  Each tuple represents a single note and contains the corresponding call_id,
    the timestamp, the note-taker, and the text of the note.
    """
    tuples = []
    if notes is None:
        return []
    regex_split = re.findall(timestamp_expr, notes)
    for tup in regex_split:
        text = tup[0].strip()
        text = text if text else None  # turn blanks into null
        try:
            timestamp = dt.datetime.strptime(tup[1], "%m/%d/%y %H:%M:%S")
        except ValueError: # 4 digit year
            timestamp = dt.datetime.strptime(tup[1], "%m/%d/%Y %H:%M:%S")
        author = tup[2]
        tuples.append((text, timestamp, author))
    return tuples

nature_code_mapping = {}
call_unit_code_mapping = {}
note_author_mapping = {}
city_code_mapping = {}

# Populate the mappings from the database
for row in db.query("SELECT * FROM nature;"):
    nature_code_mapping[row['descr']] = row['nature_id']

for row in db.query("SELECT * FROM call_unit;"):
    call_unit_code_mapping[row['descr']] = row['call_unit_id']
    
for row in db.query("SELECT * FROM note_author;"):
    note_author_mapping[row['descr']] = row['note_author_id']
    
for row in db.query("SELECT * FROM city;"):
    city_code_mapping[row['descr']] = row['city_id']

start = dt.datetime.now()
j = 0

note_authors_set = set()

call_rows = []
note_rows = []
call = db['call']
note = db['note']
db.begin()

try:
    with open('../csv_data/cfs_2014_inmain.csv', 'r', encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        first_row = True
        for row in reader:
            if first_row:
                header = row
                first_row = False
                continue
            
            #for i in range(len(header)):
            #    print(i, header[i])
            
            # Strip whitespace and convert empty strings to None
            row = list(map(lambda x: x if x else None, map(safe_strip, row)))
            time_received = pd.to_datetime(row[1]).to_datetime()  # we need a datetime, not a pandas timestamp
            call_id = safe_int(row[0]) # going to be using this again with the notes
            db_row = {
                'call_id': call_id,
                'time_received': time_received,
                'hour_received': time_received.hour,
                'month_received': time_received.month,
                'week_received': time_received.isocalendar()[1],
                'dow_received': time_received.weekday(),
                'case_id': clean_case_id(row[3]),
                'call_source_id': safe_map(call_source_code_mapping, row[4]),
                'primary_unit_id': safe_map(call_unit_code_mapping, row[5]),
                'first_dispatched_id': safe_map(call_unit_code_mapping, row[6]),
                'reporting_unit_id': safe_map(call_unit_code_mapping, row[50]),
                'street_num': safe_int(row[7]),
                'street_name': row[8],
                'city_id': safe_map(city_code_mapping, row[10]),
                'zip': safe_int(row[11]),
                'crossroad1': row[12],
                'crossroad2': row[13],
                'geox': safe_float(row[14]),
                'geoy': safe_float(row[15]),
                'beat': row[18],
                'district': row[19],
                'sector': row[20],
                'business': row[21],
                'nature_id': safe_map(nature_code_mapping, row[23]),
                'priority': row[24],
                'report_only': safe_bool(row[25]),
                'cancelled': safe_bool(row[26]),
                'time_routed': safe_datetime(row[28]),
                'time_finished': safe_datetime(row[30]),
                'first_unit_dispatch': safe_datetime(row[32]),
                'first_unit_enroute': safe_datetime(row[36]),
                'first_unit_arrive': safe_datetime(row[39]),
                'first_unit_transport': safe_datetime(row[42]),
                'last_unit_clear': safe_datetime(row[45]),
                'time_closed': safe_datetime(row[49]),
                'close_code_id': safe_map(close_code_mapping, row[51]),
                'close_comm': row[52]
            }
            notes = split_notes(row[27])
            
            #try:
#               have to insert one by one to properly handle the duplicate PKs in the data
#               db.query("SAVEPOINT integrity_checkpoint;")
#               call.insert(db_row, ensure=False) # we know the right columns are already there
            call_rows.append(db_row)
            
            for n in notes:
                note_author_mapped = safe_map(note_author_mapping, n[2])
                note_db_row = {'body': n[0],
                             'time_recorded': n[1],
                             'call_id': call_id,
                             'note_author_id': note_author_mapped}
                #note.insert(note_db_row, ensure=False)
                note_rows.append(note_db_row)
            #except IntegrityError:
                # we seem to be missing some incident data
                #print("insert of call_id %d failed due to integrity error" % (call_id))
                #db.query("ROLLBACK TO SAVEPOINT integrity_checkpoint;")
                
            #db.query("RELEASE SAVEPOINT integrity_checkpoint;")
            
            

            j+=1
            if j % 10000 == 0:
                call.insert_many(call_rows, chunk_size=10000, ensure=False)
                note.insert_many(note_rows, chunk_size=10000, ensure=False)
                call_rows = []
                note_rows = []
                print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j))
            
    call.insert_many(call_rows, ensure=False)
    note.insert_many(note_rows, ensure=False)
    db.commit()
            
except Exception as e:
    db.rollback()
    raise e
