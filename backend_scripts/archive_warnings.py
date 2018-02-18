#!/usr/local/miniconda3/bin/python

"""
Archive Warnings
------------

This script archives Warnings for use in the simulation.

Data provided by the IEM's wonderful JSON APIs.

Once you run this script to get all the warning.db database, copy it over to wherever you have your simulation scripts.

! IMPORTANT !
Update the constants to their proper values, and update the shebang above to your conda environment.

What this script does:

- Gets the Warnings from IEM
- Adds on GR's \x03 termination character
- Saves them into a database for use by the `simulation_warning.py` script during the simulation

"""

# Imports
import glob, json, os, pytz, re, requests, textwrap, time
from sqlite3 import dbapi2 as sql
from datetime import datetime, timedelta
from dateutil import parser, tz

# Constants

# Archive Times
arc_start_time = datetime(2010, 6, 1, 0, 0, 0, tzinfo=pytz.UTC)
arc_end_time = datetime(2010, 6, 1, 6, 0, 0, tzinfo=pytz.UTC)

# Sites
wfos = ('MAF', 'LUB', 'OUN')

# Processing

# Build the endpoint URL to access the IEM archive
warnings_endpoint = 'http://mesonet.agron.iastate.edu/json/nwstext_search.py?sts={start}&ets={end}&awipsid={hazard}{wfo}'

# Loop over all the warning products
warnings = []
for hazard in ['TOR', 'SVR', 'FFW']:
    for wfo in wfos:
    	print('Downloading {}{}...'.format(hazard, wfo))
        r = requests.get(warnings_endpoint.format(
            start=arc_start_time.strftime('%Y-%m-%dT%H:%MZ'),
            end=arc_end_time.strftime('%Y-%m-%dT%H:%MZ'),
            hazard=hazard,
            wfo=wfo
        ))
        warnings += [record['data'] for record in r.json()['results']]

# And let's just add the record close character so we don't have to later
warnings = [warning + '\x03' for warning in warnings]

# Make the warning database
print('Creating local database...')

warn_con = sql.connect("warning.db")
warn_cur = warn_con.cursor()
warn_cur.execute("CREATE TABLE warnings_raw (valid datetime, text char)")
warn_con.commit()

# Save the data
print('Loading into local database...')

query = "INSERT INTO warnings_raw (valid, text) VALUES (?,?)"
for warning in warnings:

    # Find the valid time
    match = re.search(r'(?P<timestamp>[0-9]{2}(0[1-9]|1[0-2])([0-2][1-9]|3[0-1])T(([0-1][0-9])|(2[0-3]))([0-5][0-9])Z)', warning)
    valid = parser.parse(match.group('timestamp'), yearfirst=True).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Save the row
    warn_cur.execute(query, [valid, warning])

warn_con.commit()

print('Done!')