import pandas as pd
from sqlalchemy import create_engine # database connection
import datetime as dt

engine = create_engine('postgresql://<USER_NAME>:<PASSWORD>@freyja.rtp.rti.org:5432/cfs')

def reset_db():
    """
    Remove and recreate tables to prepare for reloading the db
    """
    engine.execute("DROP TABLE IF EXISTS note CASCADE;")
    engine.execute("DROP TABLE IF EXISTS call CASCADE;")
    engine.execute("DROP TABLE IF EXISTS call_log CASCADE;")
    engine.execute("DROP TABLE IF EXISTS ucr_desc CASCADE;")
    engine.execute("DROP TABLE IF EXISTS incident CASCADE;")
    engine.execute("DROP TABLE IF EXISTS modus_operandi CASCADE;")
    engine.execute("DROP TABLE IF EXISTS mo_item CASCADE;")
    engine.execute("DROP TABLE IF EXISTS bureau CASCADE;")
    engine.execute("DROP TABLE IF EXISTS case_status CASCADE;")
    engine.execute("DROP TABLE IF EXISTS division CASCADE;")
    engine.execute("DROP TABLE IF EXISTS unit CASCADE;")
    engine.execute("DROP TABLE IF EXISTS investigation_status CASCADE;")
    engine.execute("DROP TABLE IF EXISTS weapon CASCADE;")
    engine.execute("DROP TABLE IF EXISTS weapon_group CASCADE;")
    engine.execute("DROP TABLE IF EXISTS premise CASCADE;")
    engine.execute("DROP TABLE IF EXISTS premise_group CASCADE;")
    
    engine.execute("""
    CREATE TABLE call
    (
      call_id bigint NOT NULL,
      call_time timestamp without time zone,
      call_dow bigint,
      case_id text,
      call_source text,
      primary_unit text,
      first_dispatched text,
      street_num text,
      street_name text,
      city_desc text,
      zip text,
      crossroad1 text,
      crossroad2 text,
      geox double precision,
      geoy double precision,
      service text,
      agency text,
      beat text,
      district text,
      sector text,
      business text,
      nature_code text,
      nature_desc text,
      priority text,
      report_only bigint,
      cancelled bigint,
      time_enroute timestamp without time zone,
      time_finished timestamp without time zone,
      first_unit_dispatch timestamp without time zone,
      first_unit_enroute timestamp without time zone,
      first_unit_arrive timestamp without time zone,
      first_unit_transport timestamp without time zone,
      last_unit_clear timestamp without time zone,
      time_closed timestamp without time zone,
      reporting_unit text,
      close_code text,
      close_comm text,
      CONSTRAINT call_id_pkey PRIMARY KEY (call_id)
    );
    """)
    
    engine.execute("""
    CREATE TABLE note
    (
      note_id serial NOT NULL,
      text text,
      "timestamp" timestamp without time zone,
      author text,
      call_id bigint,
      CONSTRAINT note_pkey PRIMARY KEY (note_id),
      CONSTRAINT note_call_id_fkey FOREIGN KEY (call_id) REFERENCES call (call_id)
    );
    """)
    
    engine.execute("""
    CREATE TABLE call_log
    (
      call_log_id bigint NOT NULL,
      transaction_code text,
      transaction_desc text,
      "timestamp" timestamp without time zone,
      call_id bigint,
      unit_code text,
      radio_or_event text,
      unitper_id bigint,
      close_code text,
      --CONSTRAINT call_log_call_id_fkey FOREIGN KEY (call_id) REFERENCES call (call_id) --nullable
      CONSTRAINT call_log_pkey PRIMARY KEY (call_log_id)
    );
    """)
    
    engine.execute("""
    CREATE TABLE ucr_desc
    (
      ucr_long_desc text,
      ucr_short_desc text NOT NULL,
      CONSTRAINT ucr_desc_pkey PRIMARY KEY (ucr_short_desc)
    );
    """)
    
    engine.execute("""
    CREATE TABLE bureau
    (
      bureau_code text,
      bureau_desc text,
      CONSTRAINT bureau_pkey PRIMARY KEY (bureau_code)
    );
    """)
    
    engine.execute("""
    CREATE TABLE division
    (
      division_code text,
      division_desc text,
      CONSTRAINT division_pkey PRIMARY KEY (division_code)
    );
    """)
    
    engine.execute("""
    CREATE TABLE investigation_status
    (
      investigation_status_code text,
      investigation_status_desc text,
      CONSTRAINT investigation_status_pkey PRIMARY KEY (investigation_status_code)
    );
    """)
    
    engine.execute("""
    CREATE TABLE case_status
    (
      case_status_code text,
      case_status_desc text,
      CONSTRAINT case_status_pkey PRIMARY KEY (case_status_code)
    );
    """)
    
    engine.execute("""
    CREATE TABLE unit
    (
      unit_code text,
      unit_desc text,
      CONSTRAINT unit_pkey PRIMARY KEY (unit_code)
    );
    """)
    
    engine.execute("""
    CREATE TABLE weapon_group
    (
      weapon_group text,
      weapon_desc text,
      CONSTRAINT weapon_group_pkey PRIMARY KEY (weapon_desc)
    );
    """)
    
    engine.execute("""
    CREATE TABLE premise_group
    (
      premise_group text,
      premise_desc text,
      CONSTRAINT premise_group_pkey PRIMARY KEY (premise_desc)
    );
    """)
    
    engine.execute("""
    CREATE TABLE weapon
    (
      weapon_code text,
      weapon_desc text,
      CONSTRAINT weapon_pkey PRIMARY KEY (weapon_code)
    );
    """)
    
    engine.execute("""
    CREATE TABLE premise
    (
      premise_code text,
      premise_desc text,
      CONSTRAINT premise_pkey PRIMARY KEY (premise_code)
    );
    """)
    
    
    engine.execute("""
    CREATE TABLE incident
    (
      incident_id bigint NOT NULL,
      call_id bigint,
      time_filed timestamp without time zone,
      street_num text,
      street_name text,
      city text,
      zip text,
      geox bigint,
      geoy bigint,
      beat text,
      district text,
      sector text,
      premise_code text,
      weapon_code text,
      domestic text,
      juvenile text,
      gang_related text,
      emp_bureau_code text,
      emp_division_code text,
      emp_unit_code text,
      num_officers integer,
      investigation_status_code text,
      investigator_unit_code text,
      case_status_code text,
      lwchrgid bigint,
      charge_seq bigint,
      ucr_code bigint,
      ucr_short_desc text,
      attempted_or_committed text,
      CONSTRAINT incident_pkey PRIMARY KEY (incident_id)
      
      --EVERYTHING IS NULLABLE AAAAAAGH
      --CONSTRAINT incident_case_status_code_fkey --nullable
      --  FOREIGN KEY (case_status_code) REFERENCES case_status (case_status_code),
      --CONSTRAINT incident_emp_bureau_code_fkey
      --  FOREIGN KEY (emp_bureau_code) REFERENCES bureau (bureau_code),
      --CONSTRAINT incident_emp_division_code_fkey
      --  FOREIGN KEY (emp_division_code) REFERENCES division (division_code),
      --CONSTRAINT incident_emp_unit_code_fkey
      --  FOREIGN KEY (emp_unit_code) REFERENCES unit (unit_code),
      --CONSTRAINT incident_investigator_unit_code_fkey -- nullable
      --  FOREIGN KEY (investigator_unit_code) REFERENCES unit (unit_code),
      --CONSTRAINT incident_investigation_status_code_fkey
      --  FOREIGN KEY (investigation_status_code) REFERENCES investigation_status (investigation_status_code),
      --CONSTRAINT incident_premise_code_fkey
      --  FOREIGN KEY (premise_code) REFERENCES premise (premise_code),
      --CONSTRAINT incident_weapon_code_fkey
      --  FOREIGN KEY (weapon_code) REFERENCES weapon (weapon_code),
      --CONSTRAINT incident_call_id_fkey
      --  FOREIGN KEY (call_id) REFERENCES call (call_id)
    );
    """)
    
    engine.execute("""
    CREATE TABLE mo_item
    (
      mo_item_code text,
      mo_item_desc text,
      mo_group_code text,
      mo_group_desc text,
      CONSTRAINT mo_item_pkey PRIMARY KEY (mo_item_code, mo_group_code)
    );
    """)
    
    engine.execute("""
    CREATE TABLE modus_operandi
    (
      incident_id bigint,
      mo_id bigint,
      mo_group_code text,
      mo_item_code text,
      CONSTRAINT mo_pkey PRIMARY KEY (mo_id)
    );
    """)
    
reset_db()

import re

timestamp_expr = re.compile("\[(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) (.+?)\]")

def split_notes_dict(notes,call_id):
    """
    Return a list of dicts.  Each dict represents a single note and contains the corresponding call_id,
    the timestamp, the note-taker, and the text of the note.
    """
    dicts = []
    regex_split = timestamp_expr.split(notes)[:-1]  # get rid of the last empty string created by the split
    for i in range(0,len(regex_split),3):
        text = regex_split[i].strip()
        timestamp = dt.datetime.strptime(regex_split[i+1], "%m/%d/%y %H:%M:%S")
        author = regex_split[i+2]
        dicts.append({"text": text, "timestamp": timestamp, "author": author, "call_id": call_id})
    return dicts

def split_notes(notes):
    """
    Return a list of tuples.  Each tuple represents a single note and contains the corresponding call_id,
    the timestamp, the note-taker, and the text of the note.
    """
    notes = str(notes)
    tuples = []
    regex_split = timestamp_expr.split(notes)[:-1]  # get rid of the last empty string created by the split
    for i in range(0,len(regex_split),3):
        text = regex_split[i].strip()
        timestamp = dt.datetime.strptime(regex_split[i+1], "%m/%d/%y %H:%M:%S")
        author = regex_split[i+2]
        tuples.append((text, timestamp, author))
    return tuples

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_

start = dt.datetime.now()
# load the data in chunks so we don't use too much memory
chunksize = 20000
j = 0

# We need to map the inmain columns to the renamed columns in the call table
# if an inmain column isn't in this dict, it means we need to drop it
call_mappings = {
    "inci_id": "call_id",
    "calltime": "call_time",
    "calldow": "call_dow",
    "case_id": "case_id",
    "callsource": "call_source",
    "primeunit": "primary_unit",
    "firstdisp": "first_dispatched",
    "streetno": "street_num",
    "streetonly": "street_name",
    "citydesc": "city_desc",
    "zip": "zip",
    "crossroad1": "crossroad1",
    "crossroad2": "crossroad2",
    "geox": "geox",
    "geoy": "geoy",
    "service": "service",
    "agency": "agency",
    "statbeat": "beat",
    "district": "district",
    "ra": "sector",
    "business": "business",
    "naturecode": "nature_code",
    "nature": "nature_desc",
    "priority": "priority",
    "rptonly": "report_only",
    "cancelled": "cancelled",
    "timeroute": "time_enroute",
    "timefini": "time_finished",
    "firstdtm": "first_unit_dispatch",
    "firstenr": "first_unit_enroute",
    "firstarrv": "first_unit_arrive",
    "firsttran": "first_unit_transport",
    "lastclr": "last_unit_clear",
    "timeclose": "time_closed",
    "reptaken": "reporting_unit",
    "closecode": "close_code",
    "closecomm": "close_comm"
}

keep_columns = set(call_mappings.keys())

for call in pd.read_csv('../csv_data/cfs_2014_inmain.csv', chunksize=chunksize, iterator=True, encoding='ISO-8859-1',
                       low_memory=False):
    
    """
    nice, clean iterative algorithm for separating out the notes data -- unfortunately, it's prohibitively slow
    (~3 mins per 25k record or thereabouts)
    """
    #for index, row in call.iterrows():
    #    note = note.append(pd.DataFrame(split_notes_dict(str(row['notes']), row['inci_id'])))
        #if call.iloc[i]['naturecode'] not in nature_set:
        #    nature_set.add(call.iloc[i]['naturecode'])
        #    nature = nature.append(pd.DataFrame({"nature_code": [call.iloc[i]['naturecode']],
        #                                "nature_desc": [call.iloc[i]['nature']]}))
   
    """
    Horrid ugly algorithm for separating out the notes data -- it's faster by about 10x though
    Pandas is really slow when iterating on rows, so we have to do all the transformations to a whole series/list
    at a time
    """
    # Create a new series, which is (for each call) a list of tuples containing the text, author, and timestamp
    # of that call:
    # ex. Series(["one long string with text, author, timestamp for all remarks"]) -> 
    #     Series([(text, author, timestamp), (text2, author2, timestamp2)])
    call['collected_notes'] = call['notes'].apply(split_notes)
    
    # Combine the previous series with the inci_id of each row, preserving the relationship between inci_id
    # and each individual remark, then convert it to a list so we can reduce and map
    # ex. Series([(text, author, timestamp), (text2, author2, timestamp2)]) ->
    #     [((text, author, timestamp), inci_id), ((text2, author2, timestamp2), inci_id2)]
    combined_notes = call['collected_notes'].combine(call['inci_id'],
                                                          lambda x,y: [(e,y) for e in x]).tolist()
    
    # Reduce the list of lists using extend; instead of a list of lists of tuples, we have one long list of
    # nested tuples
    # ex. [[((text, author, timestamp), inci_id)], [((text2, author2, timestamp2), inci_id2)]] ->
    #     [((text, author, timestamp), inci_id), ((text2, author2, timestamp2), inci_id2)]
    extended_notes = []
    for l in combined_notes:
        extended_notes.extend(l)
    
    # Flatten the tuples, so we have a list of non-nested tuples
    # ex. [((text, author, timestamp), inci_id), ((text2, author2, timestamp2), inci_id2)] ->
    #     [(text, author, timestamp, inci_id), (text2, author2, timestamp2, inci_id2)]
    extended_notes = map(lambda x: (x[0][0],x[0][1],x[0][2],x[1]), extended_notes)
    
    # Create a dataframe from the list of tuples (whew)
    note = pd.DataFrame.from_records(extended_notes, columns=['text','timestamp','author','call_id'])
    
    # drop unnecessary columns
    for c in call.columns:
        if c not in keep_columns:
            call = call.drop(c, axis=1)   
    
    # rename to the CFS Analytics column names
    call.rename(columns=call_mappings, inplace=True)
    
    ##### USING DPD COLUMN NAMES ABOVE #########
    ##### USING CFS ANALYTICS COLUMN NAMES BELOW ######
    
    # Perform datetime conversions
    call['call_time'] = pd.to_datetime(call['call_time'])
    call['time_enroute'] = pd.to_datetime(call['time_enroute'])
    call['time_finished'] = pd.to_datetime(call['time_finished'])
    call['first_unit_dispatch'] = pd.to_datetime(call['first_unit_dispatch'])
    call['first_unit_enroute'] = pd.to_datetime(call['first_unit_enroute'])
    call['first_unit_arrive'] = pd.to_datetime(call['first_unit_arrive'])
    call['first_unit_transport'] = pd.to_datetime(call['first_unit_transport'])
    call['last_unit_clear'] = pd.to_datetime(call['last_unit_clear'])
    call['time_closed'] = pd.to_datetime(call['time_closed'])

    # progress update
    j+=1
    print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j*chunksize))
    
    # get rid of excess whitespace
    call = call.applymap(safe_strip)
    note = note.applymap(safe_strip)
    
    # store in the database
    call.to_sql('call', engine, index=False, if_exists='append')
    note.to_sql('note', engine, index=False, if_exists='append')

months = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_

for month in months:
    start = dt.datetime.now()
    print("Starting load for month: %s" % (month))
    # load the data in chunks so we don't use too much memory
    chunksize = 20000
    j = 0

    # We need to map the incilog columns to the renamed columns in the call_log table
    # if an incilog column isn't in this dict, it means we need to drop it
    call_log_mappings = {
        "incilogid": "call_log_id",
        "transtype": "transaction_code",
        "descript": "transaction_desc",
        "timestamp": "timestamp",
        "inci_id": "call_id",
        "unitcode": "unit_code",
        "radorev": "radio_or_event",
        "unitperid": "unitper_id",
        "closecode": "close_code"
    }
    
    keep_columns = set(call_log_mappings.keys())

    for call_log in pd.read_csv('../csv_data/cfs_%s2014_incilog.csv' % (month), chunksize=chunksize, 
                           iterator=True, encoding='ISO-8859-1', low_memory=False):
        for c in call_log.columns:
            if c not in keep_columns:
                call_log = call_log.drop(c, axis=1)

        # rename to the CFS Analytics column names
        call_log.rename(columns=call_log_mappings, inplace=True)

        ##### USING DPD COLUMN NAMES ABOVE #########
        ##### USING CFS ANALYTICS COLUMN NAMES BELOW ######
            
        # Perform datetime conversions
        call_log['timestamp'] = pd.to_datetime(call_log['timestamp'])
        
        # progress update
        j+=1
        print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j*chunksize))

        # strip excess whitespace
        call_log = call_log.applymap(safe_strip)
        
        # store in the database
        call_log.to_sql('call_log', engine, index=False, if_exists='append')

# There are a million of these, so let's make life easier and reuse all that code
lookup_jobs = [
    {
        "file": "LWMAIN.CSSTATUS.csv",
        "table": "case_status",
        "mapping": {"code_agcy": "case_status_code", "descriptn": "case_status_desc"}
    },
    {
        "file": "LWMAIN.EMDIVISION.csv",
        "table": "division",
        "mapping": {"code_agcy": "division_code", "descriptn": "division_desc"}
    },
    {
        "file": "LWMAIN.EMSECTION.csv",
        "table": "unit",
        "mapping": {"code_agcy": "unit_code", "descriptn": "unit_desc"}
    },
    {
        "file": "LWMAIN.EMUNIT.csv",
        "table": "bureau",
        "mapping": {"code_agcy": "bureau_code", "descriptn": "bureau_desc"}
    },
    {
        "file": "LWMAIN.INVSTSTATS.csv",
        "table": "investigation_status",
        "mapping": {"code_agcy": "investigation_status_code", "descriptn": "investigation_status_desc"}
    }
]

for job in lookup_jobs:
    print("loading %s into %s" % (job['file'], job['table']))
    data = pd.read_csv("../csv_data/%s" % (job['file']))
    
    keep_columns = set(job['mapping'].keys())
    for c in data.columns:
        if c not in keep_columns:
            data = data.drop(c, axis=1)
            
    data.rename(columns=job['mapping'], inplace=True)
    data.to_sql(job['table'], engine, index=False, if_exists='append')

#These have to create "nested" tables and are a little tougher, but we can still reuse the code

nested_lookup_jobs = [
    {
        "file": "LWMAIN.PREMISE.csv",
        "outer_table": "premise",
        "inner_table": "premise_group",
        "outer_cols": ["premise_code", "premise_desc"],
        "inner_cols": ["premise_group", "premise_desc"]
    },
    {
        "file": "LWMAIN.WEAPON.csv",
        "outer_table": "weapon",
        "inner_table": "weapon_group",
        "outer_cols": ["weapon_code", "weapon_desc"],
        "inner_cols": ["weapon_group", "weapon_desc"]
    }
]

for job in nested_lookup_jobs:
    print("loading %s into %s and %s" % (job['file'], job['outer_table'], job['inner_table']))
    data = pd.read_csv("../csv_data/%s" % (job['file']))
    
    outer_data = pd.concat([data['code_agcy'], data['descriptn_b']], axis=1, keys=job['outer_cols'])
    inner_data = pd.concat([data['descriptn_a'], data['descriptn_b']], axis=1, keys=job['inner_cols'])
    
    outer_data = outer_data.drop_duplicates()
    
    outer_data.to_sql(job['outer_table'], engine, index=False, if_exists='append')
    inner_data.to_sql(job['inner_table'], engine, index=False, if_exists='append')

def combine_date_time(str_date, str_time):
    date = dt.datetime.strptime(str_date, "%m/%d/%y")
    time = dt.datetime.strptime(str_time, "%I:%M %p")
    return dt.datetime(date.year, date.month, date.day, time.hour, time.minute)

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_

start = dt.datetime.now()
# load the data in chunks so we don't use too much memory
chunksize = 20000
j = 0

# We need to map the incilog columns to the renamed columns in the call_log table
# if an incilog column isn't in this dict, it means we need to drop it
incident_mappings = {
    "lwmainid": "incident_id",
    "inci_id": "call_id",
    "time": "time_filed",
    "streetnbr": "street_num",
    "street": "street_name",
    "city": "city",
    "zip": "zip",
    "geox": "geox",
    "geoy": "geoy",
    "tract": "beat",
    "district": "district",
    "reportarea": "sector",
    "premise": "premise_code",
    "weapon": "weapon_code",
    "domestic": "domestic",
    "juvenile": "juvenile",
    "gangrelat": "gang_related",
    "emunit": "emp_bureau_code",
    "emdivision": "emp_division_code",
    "emsection": "emp_unit_code",
    "asst_offcr": "num_officers",
    "invststats": "investigation_status_code",
    "investunit": "investigator_unit_code",
    "csstatus": "case_status_code",
    "lwchrgid": "lwchrgid",
    "chrgcnt": "charge_seq",
    "ucr_code": "ucr_code",
    "arr_chrg": "ucr_short_desc",
    "attm_comp": "attempted_or_committed"
}

keep_columns = set(incident_mappings.keys())

ucr_desc = pd.DataFrame({"ucr_short_desc": [], "ucr_long_desc": []})

for incident in pd.read_csv('../csv_data/cfs_2014_lwmain.csv', chunksize=chunksize, 
                       iterator=True, encoding='ISO-8859-1', low_memory=False):
    
    ucr_desc = ucr_desc.append(pd.concat([ incident['arr_chrg'],
                                           incident['chrgdesc'] ],
                                        axis=1, keys=['ucr_short_desc', 'ucr_long_desc']))
    
    # Perform datetime conversions
    incident['time'] = incident['date_rept'].combine(incident['time'], combine_date_time)
    
    for c in incident.columns:
        if c not in keep_columns:
            incident = incident.drop(c, axis=1)

    # rename to the CFS Analytics column names
    incident.rename(columns=incident_mappings, inplace=True)

    ##### USING DPD COLUMN NAMES ABOVE #########
    ##### USING CFS ANALYTICS COLUMN NAMES BELOW ######
    
    # strip whitespace
    incident = incident.applymap(safe_strip)
    ucr_desc = ucr_desc.applymap(safe_strip)
    
    # convert empty strings in num_officers to nulls so we can insert as an int column
    incident['num_officers'] = incident['num_officers'].map(lambda x: None if x == '' else x)
    
    # These "primary key" values have two records and I don't want to deal with it
    incident = incident[~(incident.incident_id.isin((498659, 503578, 521324)))]
    
    # incident call_ids don't have the same '20' prefix that the others do, so here we add it
    # also get rid of anything pre-2014 because we don't have those in the calls table
    incident['call_id'] = incident['call_id'].map(lambda x: x + 2000000000)
    incident = incident[incident.call_id > 2014000001]
    
    # Drop duplicate ucr_descs
    ucr_desc = ucr_desc.drop_duplicates()
    
    # progress update
    j+=1
    print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j*chunksize))

    incident = incident.applymap(safe_strip)
    
    # store in the database
    incident.to_sql('incident', engine, index=False, if_exists='append')

ucr_desc.to_sql('ucr_desc', engine, index=False, if_exists='append')

def safe_strip(str_):
    try:
        return str_.strip()
    except AttributeError:
        return str_

start = dt.datetime.now()
# load the data in chunks so we don't use too much memory
# strange unexplainable crash using the usual 20k chunk size (and 10k sometimes? and 5k sometimes? this makes no sense)
# so go with 20k (no) 10k (no) 5k (no)
# actually just put your favorite number here and hope it doesn't crash
chunksize = 2500
j = 0

# We need to map the incilog columns to the renamed columns in the call_log table
# if an incilog column isn't in this dict, it means we need to drop it
modop_mappings = {
    "lwmainid": "incident_id",
    "lwmodopid": "mo_id",
    "mogroup": "mo_group_code",
    "moitem": "mo_item_code"
}

keep_columns = set(modop_mappings.keys())

mo_item = pd.DataFrame({"mo_item_code": [], "mo_item_desc": [], "mo_group_code": [], "mo_group_desc": []})

for modop in pd.read_csv('../csv_data/cfs_2014_lwmodop.csv', chunksize=chunksize, 
                       iterator=True, low_memory=False):
    
    mo_item = mo_item.append(pd.concat([ modop['moitem'],
                                         modop['itemdesc'],
                                         modop['mogroup'],
                                         modop['groupdesc'] ],
                                        axis=1, keys=['mo_item_code', 'mo_item_desc',
                                                      'mo_group_code', 'mo_group_desc']))

    for c in modop.columns:
        if c not in keep_columns:
            modop = modop.drop(c, axis=1)

    # rename to the CFS Analytics column names
    modop.rename(columns=modop_mappings, inplace=True)

    ##### USING DPD COLUMN NAMES ABOVE #########
    ##### USING CFS ANALYTICS COLUMN NAMES BELOW ######
    
    modop = modop.applymap(safe_strip)
    mo_item = mo_item.applymap(safe_strip)
    
    # The group codes are getting a decimal place for some reason.  convert them to ints
    mo_item['mo_group_code'] = mo_item['mo_group_code'].map(lambda x: str(int(x)))
    
    # Drop duplicate mo_items
    mo_item = mo_item.drop_duplicates()
    
    # Gotta get rid of any of the incident records we had to drop due to duplicate "primary keys"
    modop = modop[~(modop.incident_id.isin((498659, 503578, 521324)))]
    
    # progress update
    j+=1
    print('{} seconds: completed {} rows'.format((dt.datetime.now() - start).seconds, j*chunksize))
    
    # store in the database
    modop.to_sql('modus_operandi', engine, index=False, if_exists='append')

# Fix weird exception row causing a key error)
mo_item['mo_item_desc'] = mo_item['mo_item_desc'].map(lambda x: "Discharged" if x == "Discharged34" else x)
mo_item.to_sql('mo_item', engine, index=False, if_exists='append')

engine.execute("""
ALTER TABLE incident
ADD CONSTRAINT incident_ucr_short_desc_fkey FOREIGN KEY (ucr_short_desc) REFERENCES ucr_desc (ucr_short_desc);
""")

engine.execute("""
ALTER TABLE modus_operandi
ADD CONSTRAINT mo_mo_item_code_fkey
FOREIGN KEY (mo_item_code, mo_group_code) REFERENCES mo_item (mo_item_code, mo_group_code);
""")

engine.execute("""
ALTER TABLE weapon
ADD CONSTRAINT weapon_weapon_desc_fk FOREIGN KEY (weapon_desc) REFERENCES weapon_group (weapon_desc);
""")

engine.execute("""
ALTER TABLE premise
ADD CONSTRAINT premise_premise_desc_fk FOREIGN KEY (premise_desc) REFERENCES premise_group (premise_desc);
""")
