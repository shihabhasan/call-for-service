
import dataset
import datetime as dt
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

# CHANGE CREDENTIALS AS APPROPRIATE
sqlalchemy_uri = 'postgresql://datascientist:1234thumbwar@localhost:5432/cfs'


db = dataset.connect(sqlalchemy_uri)
engine = create_engine(sqlalchemy_uri)


db.query("CREATE EXTENSION postgis;")
db.query("CREATE EXTENSION postgis_topology;")
db.query("CREATE EXTENSION fuzzystrmatch;")
db.query("CREATE EXTENSION postgis_tiger_geocoder;")
