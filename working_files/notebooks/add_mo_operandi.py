
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
