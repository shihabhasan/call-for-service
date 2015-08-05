
# coding: utf-8

# #Data Loading, Cleaning, and Normalization
# Now that we have a better idea of what the data contains, we're going to load it in a format that will be more efficient for analysis.  Changes still needed:
#  - note splitting regex still has issues.  `SELECT descr, COUNT(*) FROM note_author GROUP BY descr ORDER BY COUNT` will show the weird ones
#  
# We'll load each table as a two-step process.  First, we scan each table and accumulate a set for each lookup table associated.  We'll then load these lookup tables.  Second, we'll load the main table.  This should be less complicated than trying to accumulate the lookup tables during the chunked-out load of the main table.
# 
# Main table: call
# Lookup tables: call_unit, city, nature
# Lookup tables loaded separately: call_source
# 
# Main table: note
# Lookup tables: note_author
# 
# Main table: shift
# Lookup tables: officer_name, call_unit (update)
# 
# Main table: call_log
# Lookup tables: transaction
# Lookup tables loaded separately: close_code
# 
# Main table: incident
# Lookup tables: city (should already have everything from call), ucr_descr
# Lookup tables loaded separately: premise, weapon, bureau, division, unit, investigation_status, case_status
# 
# Main table: modus_operandi
# Lookup tables: mo_item
# 
# Main table: out_of_service
# Lookup tables: call_unit (update), os_code
# 
# Main table: shift
# Lookup tables: call_unit (update), officer_name

# We'll use dataset to stuff the data into a local instance of postgres.

# In[1]:

import dataset
import datetime as dt
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine


# We need to create the tables before touching the data so they have all the proper constraints.

# #Database DDL
# 
# Code to create the database schema is below.

# In[2]:

# CHANGE CREDENTIALS AS APPROPRIATE
sqlalchemy_uri = 'postgresql://datascientist:1234thumbwar@freyja.rtp.rti.org:5432/cfs'
#sqlalchemy_uri = 'postgresql://jnance:@localhost:5432/cfs'

db = dataset.connect(sqlalchemy_uri)
engine = create_engine(sqlalchemy_uri)


# In[3]:

def reset_db():
    """
    Remove and recreate tables to prepare for reloading the db
    """
    db.query("DROP TABLE IF EXISTS note CASCADE;")
    db.query("DROP TABLE IF EXISTS note_author CASCADE;")
    db.query("DROP TABLE IF EXISTS call CASCADE;")
    db.query("DROP TABLE IF EXISTS call_source CASCADE;")
    db.query("DROP TABLE IF EXISTS call_unit CASCADE;")
    db.query("DROP TABLE IF EXISTS city CASCADE;")
    db.query("DROP TABLE IF EXISTS officer_name CASCADE;")
    db.query("DROP TABLE IF EXISTS shift CASCADE;")
    db.query("DROP TABLE IF EXISTS call_log CASCADE;")
    db.query("DROP TABLE IF EXISTS transaction CASCADE;")
    db.query("DROP TABLE IF EXISTS close_code CASCADE;")
    db.query("DROP TABLE IF EXISTS ucr_descr CASCADE;")
    db.query("DROP TABLE IF EXISTS incident CASCADE;")
    db.query("DROP TABLE IF EXISTS modus_operandi CASCADE;")
    db.query("DROP TABLE IF EXISTS mo_item CASCADE;")
    db.query("DROP TABLE IF EXISTS bureau CASCADE;")
    db.query("DROP TABLE IF EXISTS case_status CASCADE;")
    db.query("DROP TABLE IF EXISTS division CASCADE;")
    db.query("DROP TABLE IF EXISTS unit CASCADE;")
    db.query("DROP TABLE IF EXISTS investigation_status CASCADE;")
    db.query("DROP TABLE IF EXISTS weapon CASCADE;")
    db.query("DROP TABLE IF EXISTS weapon_group CASCADE;")
    db.query("DROP TABLE IF EXISTS premise CASCADE;")
    db.query("DROP TABLE IF EXISTS premise_group CASCADE;")
    db.query("DROP TABLE IF EXISTS nature CASCADE;")
    db.query("DROP TABLE IF EXISTS oos_code CASCADE;")
    db.query("DROP TABLE IF EXISTS out_of_service CASCADE;")

    
    db.query("""
    CREATE TABLE ucr_descr
    (
      ucr_descr_id serial NOT NULL,
      short_descr text,
      long_descr text,
      CONSTRAINT ucr_descr_pk PRIMARY KEY (ucr_descr_id)
    );
    """)
    
    db.query("""
    CREATE TABLE bureau
    (
      bureau_id serial NOT NULL,
      descr text,
      CONSTRAINT bureau_pk PRIMARY KEY (bureau_id)
    );
    """)
    
    db.query("""
    CREATE TABLE division
    (
      division_id serial NOT NULL,
      descr text,
      CONSTRAINT division_pk PRIMARY KEY (division_id)
    );
    """)
    
    db.query("""
    CREATE TABLE investigation_status
    (
      investigation_status_id serial NOT NULL,
      descr text,
      CONSTRAINT investigation_status_pk PRIMARY KEY (investigation_status_id)
    );
    """)
    
    db.query("""
    CREATE TABLE case_status
    (
      case_status_id serial NOT NULL,
      descr text,
      CONSTRAINT case_status_pk PRIMARY KEY (case_status_id)
    );
    """)
    
    db.query("""
    CREATE TABLE unit
    (
      unit_id serial NOT NULL,
      descr text,
      CONSTRAINT unit_pk PRIMARY KEY (unit_id)
    );
    """)
    
    db.query("""
    CREATE TABLE weapon_group
    (
      weapon_group_id serial NOT NULL,
      descr text,
      CONSTRAINT weapon_group_pk PRIMARY KEY (weapon_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE premise_group
    (
      premise_group_id serial NOT NULL,
      descr text,
      CONSTRAINT premise_group_pk PRIMARY KEY (premise_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE weapon
    (
      weapon_id serial NOT NULL,
      descr text,
      weapon_group_id int,
      CONSTRAINT weapon_pk PRIMARY KEY (weapon_id),
      CONSTRAINT weapon_group_weapon_fk FOREIGN KEY (weapon_group_id) REFERENCES weapon_group (weapon_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE premise
    (
      premise_id serial NOT NULL,
      descr text,
      premise_group_id int,
      CONSTRAINT premise_pk PRIMARY KEY (premise_id),
      CONSTRAINT premise_group_premise_fk FOREIGN KEY (premise_group_id) REFERENCES premise_group (premise_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE city
    (
      city_id serial NOT NULL,
      descr text,
      CONSTRAINT city_pk PRIMARY KEY (city_id)
    );
    """)
    
    db.query("""
    CREATE TABLE incident
    (
      incident_id bigint NOT NULL,
      case_id bigint UNIQUE,
      time_filed timestamp without time zone,
      month_filed int,
      week_filed int,
      dow_filed int,
      street_num int,
      street_name text,
      city_id int,
      zip int,
      geox double precision,
      geoy double precision,
      beat text,
      district text,
      sector text,
      premise_id int,
      weapon_id int,
      domestic boolean,
      juvenile boolean,
      gang_related boolean,
      emp_bureau_id int,
      emp_division_id int,
      emp_unit_id int,
      num_officers int,
      investigation_status_id int,
      investigator_unit_id int,
      case_status_id int,
      ucr_code int,
      ucr_descr_id int,
      committed boolean,
      
      CONSTRAINT incident_pk PRIMARY KEY (incident_id),
      
      CONSTRAINT case_status_incident_fk
        FOREIGN KEY (case_status_id) REFERENCES case_status (case_status_id),
      CONSTRAINT bureau_incident_fk
        FOREIGN KEY (emp_bureau_id) REFERENCES bureau (bureau_id),
      CONSTRAINT division_incident_fk
        FOREIGN KEY (emp_division_id) REFERENCES division (division_id),
      CONSTRAINT unit_incident_emp_fk
        FOREIGN KEY (emp_unit_id) REFERENCES unit (unit_id),
      CONSTRAINT unit_incident_investigator_fk
        FOREIGN KEY (investigator_unit_id) REFERENCES unit (unit_id),
      CONSTRAINT investigation_status_incident_fk
        FOREIGN KEY (investigation_status_id) REFERENCES investigation_status (investigation_status_id),
      CONSTRAINT premise_incident_fk
        FOREIGN KEY (premise_id) REFERENCES premise (premise_id),
      CONSTRAINT weapon_incident_fk
        FOREIGN KEY (weapon_id) REFERENCES weapon (weapon_id),
      CONSTRAINT city_incident_fk
        FOREIGN KEY (city_id) REFERENCES city (city_id),
      CONSTRAINT ucr_descr_incident_fk
        FOREIGN KEY (ucr_descr_id) REFERENCES ucr_descr (ucr_descr_id)
    );
    """)
    
    db.query("""
    CREATE TABLE mo_item
    (
      mo_item_id serial NOT NULL,
      item_descr text,
      mo_group_id serial NOT NULL,
      group_descr text,
      CONSTRAINT mo_item_pk PRIMARY KEY (mo_item_id, mo_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE modus_operandi
    (
      incident_id bigint,
      mo_id bigint,
      mo_group_id int,
      mo_item_id int,
      
      CONSTRAINT mo_pk PRIMARY KEY (mo_id),
      
      CONSTRAINT incident_modus_operandi_fk FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
      CONSTRAINT mo_item_modus_operandi_fk FOREIGN KEY (mo_item_id, mo_group_id) 
        REFERENCES mo_item (mo_item_id, mo_group_id)
    );
    """)
    
    db.query("""
    CREATE TABLE call_source
    (
      call_source_id serial NOT NULL,
      descr text,
      CONSTRAINT call_source_pk PRIMARY KEY (call_source_id)
    );
    """)
    
    db.query("""
    CREATE TABLE call_unit
    (
      call_unit_id serial NOT NULL,
      descr text,
      CONSTRAINT call_unit_pk PRIMARY KEY (call_unit_id)
    );
    """)
    
    db.query("""
    CREATE TABLE close_code
    (
      close_code_id serial NOT NULL,
      descr text,
      CONSTRAINT close_code_pk PRIMARY KEY (close_code_id)
    );
    """)
    
    db.query("""
    CREATE TABLE nature
    (
      nature_id serial NOT NULL,
      descr text,
      CONSTRAINT nature_pk PRIMARY KEY (nature_id)
    );
    """)
    
    db.query("""
    CREATE TABLE call
    (
      call_id bigint NOT NULL,
      month_received int,
      week_received int,
      dow_received int,
      hour_received int,
      case_id bigint,
      call_source_id int,
      primary_unit_id int,
      first_dispatched_id int,
      reporting_unit_id int,
      street_num int,
      street_name text,
      city_id int,
      zip int,
      crossroad1 text,
      crossroad2 text,
      geox double precision,
      geoy double precision,
      beat text,
      district text,
      sector text,
      business text,
      nature_id int,
      priority text,
      report_only boolean,
      cancelled boolean,
      time_received timestamp without time zone,
      time_routed timestamp without time zone,
      time_finished timestamp without time zone,
      first_unit_dispatch timestamp without time zone,
      first_unit_enroute timestamp without time zone,
      first_unit_arrive timestamp without time zone,
      first_unit_transport timestamp without time zone,
      last_unit_clear timestamp without time zone,
      time_closed timestamp without time zone,
      close_code_id int,
      close_comments text,
      
      CONSTRAINT call_pk PRIMARY KEY (call_id),
      
      CONSTRAINT call_source_call_fk
        FOREIGN KEY (call_source_id) REFERENCES call_source (call_source_id),
      CONSTRAINT call_unit_call_primary_unit_fk
        FOREIGN KEY (primary_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT call_unit_call_first_dispatched_fk
        FOREIGN KEY (first_dispatched_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT call_unit_call_reporting_unit_fk
        FOREIGN KEY (reporting_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT city_call_fk
        FOREIGN KEY (city_id) REFERENCES city (city_id),
      CONSTRAINT close_code_call_fk
        FOREIGN KEY (close_code_id) REFERENCES close_code (close_code_id),
      --There is some mismatch here that might be valid; no constraint for now
      --CONSTRAINT incident_call_fk
      --  FOREIGN KEY (case_id) REFERENCES incident (case_id),
      CONSTRAINT nature_call_fk
        FOREIGN KEY (nature_id) REFERENCES nature (nature_id)
    );
    """)
    
    db.query("""
    CREATE TABLE note_author
    (
      note_author_id serial NOT NULL,
      descr text,
      CONSTRAINT note_author_pk PRIMARY KEY (note_author_id)
    );
    """)
    
    db.query("""
    CREATE TABLE note
    (
      note_id serial NOT NULL,
      body text,
      time_recorded timestamp without time zone,
      note_author_id int,
      call_id bigint,
      CONSTRAINT note_pk PRIMARY KEY (note_id),
      
      CONSTRAINT call_note_fk FOREIGN KEY (call_id) REFERENCES call (call_id),
      CONSTRAINT note_author_note_fk FOREIGN KEY (note_author_id) REFERENCES note_author (note_author_id)
    );
    """)
    
    db.query("""
    CREATE TABLE officer_name
    (
        officer_name_id serial NOT NULL,
        officer_id bigint,
        name text,
        
        CONSTRAINT officer_name_pk PRIMARY KEY (officer_name_id)
    );
    """)
    
    db.query("""
    CREATE TABLE shift
    (
        shift_id bigint NOT NULL,
        shift_unit_id bigint,
        call_unit_id int,
        officer_id int,
        time_in timestamp without time zone,
        time_out timestamp without time zone,
        unit text,
        division text,
        section text,
        
        CONSTRAINT shift_pk PRIMARY KEY (shift_id),
        -- shift_unit_id is referenced by call_log and out_of_service, but it's not unique, so it can't
        -- be the primary key
        CONSTRAINT call_unit_shift_fk FOREIGN KEY (call_unit_id) REFERENCES call_unit (call_unit_id)
        -- officer_id references officer_name, but it isn't unique in that table, so no FK constraint
    );
    """)

    db.query("""
    CREATE TABLE transaction
    (
      transaction_id serial NOT NULL,
      descr text,
      CONSTRAINT transaction_pk PRIMARY KEY (transaction_id)
    )
    """)
    
    db.query("""
    CREATE TABLE call_log
    (
      call_log_id bigint NOT NULL,
      transaction_id int,
      shift_unit_id int,
      time_recorded timestamp without time zone,
      call_id bigint,
      call_unit_id int,
      close_code_id int,
      
      CONSTRAINT call_log_pk PRIMARY KEY (call_log_id),
      
      -- shift_unit_id references shift.shift_unit_id, but the latter isn't unique, so no FK constraint
      CONSTRAINT call_unit_call_log_fk FOREIGN KEY (call_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT call_call_log_fk FOREIGN KEY (call_id) REFERENCES call (call_id),
      CONSTRAINT close_code_call_log_fk FOREIGN KEY (close_code_id) REFERENCES close_code (close_code_id),
      CONSTRAINT transaction_call_log_fk FOREIGN KEY (transaction_id) REFERENCES transaction (transaction_id)
    );
    """)
    
    db.query("""
    CREATE TABLE oos_code
    (
      oos_code_id serial NOT NULL,
      descr text,
      
      CONSTRAINT oos_code_pk PRIMARY KEY (oos_code_id)
    );
    """)
    
    db.query("""
    CREATE TABLE out_of_service
    (
      oos_id bigint NOT NULL,
      call_unit_id int,
      shift_unit_id int,
      oos_code_id int,
      location text,
      comments text,
      start_time timestamp without time zone,
      end_time timestamp without time zone,
      duration interval,
      
      CONSTRAINT oos_pk PRIMARY KEY (oos_id),
      
      -- shift_unit_id references shift.shift_unit_id, but the latter isn't unique, so no FK constraint
      CONSTRAINT call_unit_oos_fk FOREIGN KEY (call_unit_id) REFERENCES call_unit (call_unit_id),
      CONSTRAINT oos_code_oos_fk FOREIGN KEY (oos_code_id) REFERENCES oos_code (oos_code_id)
    );
    """)
      
    
reset_db()


# #Small lookup tables
# case_status, division, unit, bureau, investigation_status, call_source, and close_code
# 
# The nested lookup tables are weapon/weapon_group and premise/premise_group

# In[4]:

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


# In[5]:

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


# #cfs_2014_lwmain.csv

# ###Lookup tables
# city and ucr_descr

# In[6]:

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


# ###Main table
# incident

# In[7]:

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


# #cfs_2014_lwmodop.csv

# ###Lookup tables
# I would use pandas for this, as it's similar to the other lookup tables, but something about pandas' read_csv function creates weird escape characters with this file only.
# The only lookup table for this file is mo_item.

# In[8]:

chunksize=10000

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_
    
mo_item_pairs = set()

print("loading lookup tables")

import csv

with open('../csv_data/cfs_2014_lwmodop.csv', 'r') as f:
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

        mo_item_pairs.add((row[3], row[5]))
            
try:
    mo_item = db['mo_item']
    db.begin()
    for pair in mo_item_pairs:
        mo_item.insert({'group_descr': pair[0], 'item_descr': pair[1]})
    db.commit()
except Exception as e:
    db.rollback()
    raise e
    
print("lookup tables loaded")


# ###Main table
# modus_operandi

# In[9]:

import csv    

# We'll use this to ensure we either map to a value of the foreign key or null
def safe_map(m,d):
    return m[d] if d else d

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_

# Populate the mappings from the database
mo_item_code_mapping = {}

# the pairs of group/item_descr are unique, so that needs to be our key
for row in db.query("SELECT * FROM mo_item;"):
    mo_item_code_mapping[(row['group_descr'], row['item_descr'])] = (row['mo_group_id'], row['mo_item_id'])

start = dt.datetime.now()
j = 0

mo = db['modus_operandi']
db_rows = []
db.begin()

try:
    with open('../csv_data/cfs_2014_lwmodop.csv', 'r') as f:
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
            mo_pair = safe_map(mo_item_code_mapping, (row[3], row[5]))
            db_row = {
                'incident_id': row[0],
                'mo_id': row[1],
                'mo_group_id': mo_pair[0],
                'mo_item_id': mo_pair[1]
            }
            
            # have to insert one by one to properly handle the duplicate PKs in the data
            mo.insert(db_row, ensure=False) # we know the right columns are already there
            
            j+=1
            if j % 10000 == 0:
                print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j))    
            
    db.commit()
            
except Exception as e:
    db.rollback()
    raise e


# #cfs_2014_inmain.csv

# ###Lookup tables
# We did close_code and call_source earlier with the other tables that come directly from a .csv file.
# 
# We'll need to do a full load of nature and call_unit, and we need to update city with the new cities in this file even though we loaded it previously.  Also need to do a pass through all the notes to get the note_authors.

# In[10]:

import re

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_
    
timestamp_expr = re.compile("(.*?)\[(\d{2}/\d{2}/(?:\d{2}|\d{4}) \d{2}:\d{2}:\d{2}) (.*?)\]")

def split_notes(notes):
    """
    Return a list of tuples.  Each tuple represents a single note and contains the corresponding call_id,
    the timestamp, the note-taker, and the text of the note.
    """
    tuples = []
    regex_split = re.findall(timestamp_expr, notes)
    for tup in regex_split:
        text = tup[0].split()
        text = text if text else None  # turn blanks into null
        try:
            timestamp = dt.datetime.strptime(tup[1], "%m/%d/%y %H:%M:%S")
        except ValueError: # 4 digit year
            timestamp = dt.datetime.strptime(tup[1], "%m/%d/%Y %H:%M:%S")
        author = tup[2] if tup[2] else None
        tuples.append((text, timestamp, author))
    return tuples
    
natures = set()
call_units = set()
note_authors = set()

cities = set()
db_cities = set()
# we already have most of the cities from the incident data, but there are more
for row in db.query("SELECT * FROM city;"):
    db_cities.add(row['descr'])

print("loading lookup tables")

import csv

with open('../csv_data/cfs_2014_inmain.csv', 'r', encoding='ISO-8859-1') as f:
    reader = csv.reader(f)
    first_row = True
    for row in reader:
        if first_row:
            header = row
            first_row = False
            continue
            
        # Strip whitespace and convert empty strings to None
        row = list(map(lambda x: x if x else None, map(safe_strip, row)))

        if row[23]:
            natures.add(row[23])
        for d in (row[5], row[6], row[50]): # these all reference the call_unit table
            call_units.add(d)
        if row[27]:
            for note in split_notes(row[27]):
                if note[2] is not None:
                    note_authors.add(note[2])
        if row[10] and row[10] not in db_cities:
            cities.add(row[10])
            
try:
    nature = db['nature']
    db.begin()
    for n in natures:
        nature.insert({'descr': n})
    db.commit()
    
    call_unit = db['call_unit']
    db.begin()
    for c in call_units:
        call_unit.insert({'descr': c})
    db.commit()
    
    note_author = db['note_author']
    db.begin()
    for na in note_authors:
        note_author.insert({'descr': na})
    db.commit()
    
    city = db['city']
    db.begin()
    for c in cities:
        city.insert({'descr': c})
    db.commit()
except Exception as e:
    db.rollback()
    raise e
    
print("lookup tables loaded")


# ###Main table
# call

# In[11]:

import csv
import re

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


# #cfs_2014_unitper.csv
# 
# ##Lookup tables
# Need to update call_unit and load officer_name.

# In[12]:

import csv

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_
    
officer_name_pairs = set()

call_units = set()
db_call_units = set()
# we already have most of the call_units from the call data, but there are more
for row in db.query("SELECT * FROM call_unit;"):
    db_call_units.add(row['descr'])

print("loading lookup tables")

with open('../csv_data/cfs_2014_unitper.csv', 'r', encoding='ISO-8859-1') as f:
    reader = csv.reader(f)
    first_row = True
    for row in reader:
        if first_row:
            header = row
            first_row = False
            continue

        # Strip whitespace and convert empty strings to None
        row = list(map(lambda x: x if x else None, map(safe_strip, row)))

        if row[2] and row[2] not in db_call_units:
            call_units.add(row[2])
        if (row[3], row[4]) not in officer_name_pairs:
            officer_name_pairs.add((row[3], row[4]))

try:
    call_unit = db['call_unit']
    officer_name = db['officer_name']
    db.begin()
    for c in call_units:
        call_unit.insert({'descr': c})
    for id_, name in officer_name_pairs:
        officer_name.insert({'officer_id': id_, 'name': name})
    db.commit()
except Exception as e:
    db.rollback()
    raise e

print("lookup tables loaded")


# ###Main table
# shift

# In[13]:

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


# #cfs_xxx2014_incilog.csv

# ###Lookup tables
# Need to update call_unit and do a full load of transaction.

# In[14]:

import csv

months = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_

transactions = set()

call_units = set()
db_call_units = set()
# we already have most of the call_units from the call data, but there are more
for row in db.query("SELECT * FROM call_unit;"):
    db_call_units.add(row['descr'])

print("loading lookup tables")

for month in months:  

    with open('../csv_data/cfs_%s2014_incilog.csv' % (month), 'r', encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        first_row = True
        for row in reader:
            if first_row:
                header = row
                first_row = False
                continue

            # Strip whitespace and convert empty strings to None
            row = list(map(lambda x: x if x else None, map(safe_strip, row)))

            if row[2]:
                transactions.add(row[2])
            
            if row[6] and row[6] not in db_call_units:
                call_units.add(row[6])

try:
    call_unit = db['call_unit']
    db.begin()
    for c in call_units:
        call_unit.insert({'descr': c})
    db.commit()

    transaction = db['transaction']
    db.begin()
    for t in transactions:
        transaction.insert({'descr': t})
    db.commit()
except Exception as e:
    db.rollback()
    raise e

print("lookup tables loaded")


# ###Main table
# call_log

# In[15]:

import csv

months = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")

# We'll use this to ensure we either map to a value of the foreign key or null
def safe_map(m,d):
    return m[d] if d else d

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_
    
def safe_int(x):
    return int(x) if x else None

def safe_datetime(x):
    # to_datetime returns a pandas Timestamp object, and we want a vanilla datetime
    return pd.to_datetime(x).to_datetime() if x not in ('NULL', None) else None

# Populate the mappings from the database
call_unit_mapping = {}
transaction_code_mapping = {}

for row in db.query("SELECT * FROM call_unit;"):
    call_unit_mapping[row['descr']] = row['call_unit_id']
    
for row in db.query("SELECT * FROM transaction;"):
    transaction_code_mapping[row['descr']] = row['transaction_id']
    
# We have fire and EMS call_log data, which we don't have calls for.  We need to ignore this data.
valid_call_ids = set()
for row in db.query("SELECT call_id FROM call;"):
    valid_call_ids.add(row['call_id'])
    

start = dt.datetime.now()
j = 0

call_log = db['call_log']
db_rows = []
db.begin()

try:
    for month in months:
        print("loading data for %s" % (month))
        with open('../csv_data/cfs_%s2014_incilog.csv' % (month), 'r') as f:
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
                
                call_id = safe_int(row[5])
                if call_id in valid_call_ids:
                    db_rows.append({
                        'call_log_id': safe_int(row[0]),
                        'transaction_id': safe_map(transaction_code_mapping, row[2]),
                        'time_recorded': safe_datetime(row[3]),
                        'call_id': call_id,
                        'call_unit_id': safe_map(call_unit_mapping, row[6]),
                        'shift_unit_id': safe_int(row[8]),
                        'close_code_id': safe_map(close_code_mapping, row[9])
                    })
                    j+=1
                    if j % 10000 == 0:
                        call_log.insert_many(db_rows, chunk_size=10000, ensure=False)
                        db_rows=[]
                        print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j))    
    
    call_log.insert_many(db_rows, ensure=False)
    db.commit()
            
except Exception as e:
    db.rollback()
    raise e


# #cfs_2014_outserv.csv

# ##Lookup tables
# Need to update call_unit.

# In[16]:

import csv

call_units = set()
db_call_units = set()
for row in db.query("SELECT * FROM call_unit;"):
    db_call_units.add(row['descr'])
    
print("loading lookup tables")

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

        if row[1] and row[1] not in db_call_units:
            call_units.add(row[1])

try:
    call_unit = db['call_unit']
    db.begin()
    for c in call_units:
        call_unit.insert({'descr': c})
    db.commit()
except Exception as e:
    db.rollback()
    raise e

print("lookup tables loaded")


# ##Main table

# In[17]:

import csv

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


# #Enable GIS extensions (PostGIS)

# In[18]:

db.query("CREATE EXTENSION postgis;")
db.query("CREATE EXTENSION postgis_topology;")
db.query("CREATE EXTENSION fuzzystrmatch;")
db.query("CREATE EXTENSION postgis_tiger_geocoder;")


# Now use PostGIS to convert the NC state planar coordinates to latitude and longitude.

# In[19]:

db.query("""DROP TABLE IF EXISTS call_latlong;""")

db.query("""
CREATE TABLE call_latlong AS (
    SELECT call_id, st_x(point) AS longitude, st_y(point) AS latitude, point
    FROM (
        SELECT call_id, 
        st_Transform(ST_SetSRID(ST_MakePoint(geox, geoy), 2264), 4326)::geometry(Point, 4326) AS point
        FROM call
    ) AS a
);
""")

db.query("""DROP TABLE IF EXISTS incident_latlong;""")

db.query("""
CREATE TABLE incident_latlong AS (
    SELECT incident_id, st_x(point) AS longitude, st_y(point) AS latitude, point
    FROM (
        SELECT incident_id, 
        -- We have to divide incident x and y by 100 to get the proper numbers
        st_Transform(ST_SetSRID(ST_MakePoint(geox/100, geoy/100), 2264), 4326)::geometry(Point, 4326) AS point
        FROM incident
    ) AS a
);
""")


# Loading the beats shapefiles via PostGIS:

# In[3]:

with open("../shapefiles/beats_districts/shapefile.sql", 'r') as f:
    db.query(f.read())


# #Misc. Other Changes

# Adding the incident_id column to call:

# In[3]:

with open("../scripts/call_incident_id.sql", 'r') as f:
    db.query(f.read())

