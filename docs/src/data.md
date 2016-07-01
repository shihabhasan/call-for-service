# Loading data

## Data format

CFS Analytics loads data from CSV files with one call per line. These files
must have the following headers:

- Internal ID
- Time Received
- Time Dispatched
- Time Arrived
- Time Closed

Each internal ID should be unique. If one is encountered that has been seen
before, it is ignored.

(There is a current bug around this. If the same ID is in the same file more
than once, an error can occur.)

The files should have some or all of the following headers. Note that headers
that end in "Code" and "Text" come in pairs and must be matched.

- Street Address
- City
- Zip
- Latitude
- Longitude
- Priority
- District
- Nature Code
- Nature Text
- Close Code
- Close Text

Having additional headers is fine.

## Running the load command

From the command line, in the top level directory of this repository, run:

    ./cfs/manage.py load_call_csv <name of your CSV file>

This will load not only the individual calls in your CSV file but will also
create the priorities, districts, natures, and close codes from your source
file.
