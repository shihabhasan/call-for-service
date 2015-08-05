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

# We have several columns we need to convert to int that can also be None
def safe_int(x):
    return int(x) if x else None

def safe_datetime(x):
    # to_datetime returns a pandas Timestamp object, and we want a vanilla datetime
    return pd.to_datetime(x).to_datetime() if x not in ('NULL', None) else None

# We'll use this to ensure we either map to a value of the foreign key or null
def safe_map(m,d):
    return m[d] if d else None

call_unit_mapping = {}
    
for row in db.query("SELECT * FROM call_unit;"):
    call_unit_mapping[row['descr']] = row['call_unit_id']
    
start = dt.datetime.now()
j = 0

oos_rows = []

oos = db['out_of_service']

try:
    with open('../csv_data/cfs_2014_outserv.csv', 'r', encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        first_row = True
        for row in reader:
            if first_row:
                header = row
                first_row = False
                continue
            
            # Strip whitespace and convert empty strings to None
            row = list(map(lambda x: x if x else None, map(safe_strip, row)))
            db_row = {
                'oos_id': safe_int(row[0]),
                'call_unit_id': safe_map(call_unit_mapping, row[1]),
                'oos_code_id': safe_map(oos_code_mapping, row[2]),
                'location': row[3],
                'comments': row[4],
                'start_time': safe_datetime(row[5]),
                'end_time': safe_datetime(row[6]),
                'duration': safe_datetime(row[6]) - safe_datetime(row[5]),
                'shift_unit_id': safe_int(row[8])
            }
            oos_rows.append(db_row)
            
            j+=1
            if j % 10000 == 0:
                oos.insert_many(oos_rows, chunk_size=10000, ensure=False)
                oos_rows = []
                print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j))
    oos.insert_many(oos_rows, ensure=False)
    db.commit()
            
except Exception as e:
    db.rollback()
    raise e
