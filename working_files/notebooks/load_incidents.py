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
 

def combine_date_time(str_date, str_time):
    date = dt.datetime.strptime(str_date, "%m/%d/%y")
    time = dt.datetime.strptime(str_time, "%I:%M %p")
    return dt.datetime(date.year, date.month, date.day, time.hour, time.minute)

# We'll use this to ensure we either map to a value of the foreign key or null
def safe_map(m,d):
    return m[d] if d else d

# We have several columns we need to convert to int that can also be None
def safe_int(x):
    return int(x) if x else None

att_com_mapping = {
    'COM': True,
    'ATT': False,
    '': None
}

city_code_mapping = {}
ucr_descr_code_mapping = {}

# Populate the mappings from the database
for row in db.query("SELECT * FROM city;"):
    city_code_mapping[row['descr']] = row['city_id']

# the pairs of short/long_descr are unique, so that needs to be our key
for row in db.query("SELECT * FROM ucr_descr;"):
    ucr_descr_code_mapping[(row['short_descr'], row['long_descr'])] = row['ucr_descr_id']

start = dt.datetime.now()
j = 0

incident = db['incident']
db.begin()

try:
    with open('../csv_data/cfs_2014_lwmain.csv', 'r') as f:
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
            time_filed = combine_date_time(row[2], row[3])
            db_row = {
                'incident_id': safe_int(row[0]),
                'case_id': safe_int(row[1]),
                'time_filed': time_filed,
                'month_filed': time_filed.month,
                'week_filed': time_filed.isocalendar()[1],
                'dow_filed': time_filed.weekday(),
                'street_num': row[7],
                'street_name': row[8],
                'city_id': safe_map(city_code_mapping, row[9]),
                'zip': None if row[10] == 'NC' else row[10],
                'geox': row[11],
                'geoy': row[12],
                'beat': row[13],
                'district': row[14],
                'sector': row[15],
                'premise_id': safe_map(premise_code_mapping, safe_int(row[16])),
                'weapon_id': safe_map(weapon_code_mapping, safe_int(row[17])),
                'domestic': True if row[18]=='Y' else False if row[18]=='N' else None,
                'juvenile': True if row[19]=='Y' else False if row[19]=='N' else None,
                'gang_related': True if row[20]=='YES' else False if row[20]=='NO' else None,
                'emp_bureau_id': safe_map(bureau_code_mapping, row[21]),
                'emp_division_id': safe_map(division_code_mapping, row[22]),
                'emp_unit_id': safe_map(unit_code_mapping, row[23]),
                'num_officers': (lambda x: None if x in ('',None) else safe_int(x))(row[24]),
                'investigation_status_id': safe_map(investigation_status_code_mapping,row[25]),
                'investigator_unit_id': safe_map(unit_code_mapping, row[26]),
                'case_status_id': safe_map(case_status_code_mapping, safe_int(row[27])),
                'ucr_code': row[30],
                'ucr_descr_id': safe_map(ucr_descr_code_mapping, (row[31],row[32])),
                'committed': safe_map(att_com_mapping, row[33])
            }
            
            try:
                # have to insert one by one to properly handle the duplicate PKs in the data
                db.query("SAVEPOINT integrity_checkpoint;")
                incident.insert(db_row, ensure=False) # we know the right columns are already there
            except IntegrityError:
                #ignore the duplicate pks; the lower chrgid comes first, so we already have the record we want
                #postgres complains if we keep inserting records into an aborted transaction
                db.query("ROLLBACK TO SAVEPOINT integrity_checkpoint;")
                
            db.query("RELEASE SAVEPOINT integrity_checkpoint;")
            
            j+=1
            if j % 10000 == 0:
                print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j))
            
            
    db.commit()
            
except Exception as e:
    db.rollback()
    raise e


