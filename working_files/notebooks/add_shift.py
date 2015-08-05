
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

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_
    
def safe_map(m,d):
    return m[d] if d else None    

def safe_int(x):
    return int(x) if x else None

def safe_datetime(x):
    # to_datetime returns a pandas Timestamp object, and we want a vanilla datetime
    return pd.to_datetime(x).to_datetime() if x not in ('NULL', None) else None

# Populate the mappings from the database
call_unit_mapping = {}

for row in db.query("SELECT * FROM call_unit;"):
    call_unit_mapping[row['descr']] = row['call_unit_id']
    
start = dt.datetime.now()
j = 0

shift = db['shift']
db_rows = []
db.begin()

try:
    with open('../csv_data/cfs_2014_unitper.csv', 'r') as f:
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
                'shift_id': safe_int(row[0]),
                'shift_unit_id': safe_int(row[1]),
                'call_unit_id': safe_map(call_unit_mapping, row[2]),
                'officer_id': safe_int(row[3]),
                'time_in': safe_datetime(row[6]),
                'time_out': safe_datetime(row[7]),
                'unit': row[8],
                'division': row[9],
                'section': row[10]
            }
            
            # have to insert one by one to properly handle the duplicate PKs in the data
            shift.insert(db_row, ensure=False) # we know the right columns are already there
            
            j+=1
            if j % 10000 == 0:
                print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j))    
            
    db.commit()
            
except Exception as e:
    db.rollback()
    raise e
