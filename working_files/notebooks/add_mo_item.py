import dataset
import datetime as dt
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

# CHANGE CREDENTIALS AS APPROPRIATE
sqlalchemy_uri = 'postgresql://datascientist:1234thumbwar@localhost:5432/cfs'


db = dataset.connect(sqlalchemy_uri)
engine = create_engine(sqlalchemy_uri)




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
