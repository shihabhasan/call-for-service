import dataset
import datetime as dt
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

# CHANGE CREDENTIALS AS APPROPRIATE
sqlalchemy_uri = 'postgresql://datascientist:1234thumbwar@localhost:5432/cfs'


db = dataset.connect(sqlalchemy_uri)
engine = create_engine(sqlalchemy_uri)



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


#These have to create "nested" tables and are a little tougher, but we can still reuse the code

# Still need to keep track of the mappings
weapon_code_mapping = {}
premise_code_mapping = {}

nested_lookup_jobs = [
    {
        "file": "LWMAIN.PREMISE.csv",
        "outer_table": "premise",
        "inner_table": "premise_group",
        "outer_cols": ["premise_group_id","descr"],
        "inner_col": "descr",
        "inner_id": "premise_group_id",
        "code_mapping": premise_code_mapping
    },
    {
        "file": "LWMAIN.WEAPON.csv",
        "outer_table": "weapon",
        "inner_table": "weapon_group",
        "outer_cols": ["weapon_group_id","descr"],
        "inner_col": "descr",
        "inner_id": "weapon_group_id",
        "code_mapping": weapon_code_mapping
    }
]

for job in nested_lookup_jobs:
    print("loading %s into %s and %s" % (job['file'], job['outer_table'], job['inner_table']))
    data = pd.read_csv("../csv_data/%s" % (job['file']))
    
    # load the group table by getting all the unique groups
    inner_data = data['descriptn_a'].drop_duplicates()
    inner_data.name = job['inner_col']
    inner_data.to_sql(job['inner_table'], engine, index=False, if_exists='append')
    
    # Learn the mapping between groups and group_ids in the database so we can insert the proper
    # group_ids with the outer tables
    groups = {}
    for row in db.query("SELECT * FROM %s" % (job['inner_table'])):
        groups[row[job['inner_col']]] = row[job['inner_id']]
       
    # Figure out what the database ids will be, so we can convert DPD's columns to the database ids in the
    # main table load
    id_ = 1
    for (i,row) in data.iterrows():
        job['code_mapping'][row['code_agcy']] = id_
        id_ += 1
    
    # Concatenate and rename the series we want
    outer_data = pd.concat([data['descriptn_a'], data['descriptn_b']], axis=1, keys=job['outer_cols'])
    
    # use the groups mapping to turn group names into ids from our database
    outer_data[job['inner_id']] = outer_data[job['inner_id']].map(lambda x: groups[x])
    
    # Store the records
    outer_data.to_sql(job['outer_table'], engine, index=False, if_exists='append')

    chunksize=20000

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_
    
city = pd.DataFrame({'descr': []})
ucr_descr_pairs = pd.DataFrame({'short_descr':[], 'long_descr': []})

print("loading lookup tables")

# We'll start out by doing a pass through the file and loading the lookup tables we need (ucr_descr, city)
for incident in pd.read_csv('../csv_data/cfs_2014_lwmain.csv', chunksize=chunksize, 
                       iterator=True, encoding='ISO-8859-1', low_memory=False):
    
    #Strip extraneous white space and turn resulting blanks into NULLs
    incident = incident.applymap(safe_strip).applymap(lambda x: None if x == '' or pd.isnull(x) else x)
    
    # Turn the ucr_descrs into pairs, since it's the pairs that are unique
    ucr_descr_pairs = ucr_descr_pairs.append(
        pd.concat([incident['arr_chrg'], incident['chrgdesc']], axis=1).rename(
            columns={'arr_chrg': 'short_descr', 'chrgdesc': 'long_descr'}))
    ucr_descr_pairs = ucr_descr_pairs.drop_duplicates()
    
    # Add the cities in the current chunk to the dataframe
    city = pd.concat([city, pd.DataFrame(incident['city']).rename(columns={'city':'descr'})], axis=0)
    city = city.drop_duplicates()

# we don't need nulls in a lookup table
city = city[~city.descr.isnull()]

#store the records
city.to_sql('city', engine, index=False, if_exists='append')
ucr_descr_pairs.to_sql('ucr_descr', engine, index=False, if_exists='append')

print("lookup tables loaded")


import csv    

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
