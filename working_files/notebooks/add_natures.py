
import dataset
import datetime as dt
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

# CHANGE CREDENTIALS AS APPROPRIATE
sqlalchemy_uri = 'postgresql://datascientist:1234thumbwar@localhost:5432/cfs'


db = dataset.connect(sqlalchemy_uri)
engine = create_engine(sqlalchemy_uri)


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
