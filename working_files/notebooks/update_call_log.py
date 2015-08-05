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
