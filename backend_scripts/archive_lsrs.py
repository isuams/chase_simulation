#!/usr/bin/env python

"""
Archive LSRs
------------

This script archives LSRs for use in the simulation.

Data provided by the IEM's wonderful JSON APIs.

Once you run this script to get all the lsr.db database, copy it over to wherever you have your placefile CGI endpoint

! IMPORTANT !
Update the constants to their proper values, and update the shebang above to your conda environment.

What this script does:

- Gets the LSRs from IEM
- Saves them into a database for use by the `placefile_lsr.py` CGI endpoint

"""

# Imports
import glob, json, os, pytz, re, requests, textwrap, time
from sqlite3 import dbapi2 as sql
from datetime import datetime, timedelta
from dateutil import parser, tz
from ChaseLib.LSR import type_to_icon

# Constants

# Archive Times
arc_start_time = datetime(2010, 6, 1, 0, 0, 0, tzinfo=pytz.UTC)
arc_end_time = datetime(2010, 6, 1, 6, 0, 0, tzinfo=pytz.UTC)

# Sites
wfos = ('MAF', 'LUB', 'OUN')

# Processing

# Build the endpoint URL to access the IEM archive
endpoint_args = {
    'start': arc_start_time.strftime('%Y%m%d%H%M'),
    'end': arc_end_time.strftime('%Y%m%d%H%M'),
    'wfos': ",".join(wfos)
}
lsr_endpoint = 'http://mesonet.agron.iastate.edu/geojson/lsr.php?sts={start}&ets={end}&wfos={wfos}'.format(**endpoint_args)

# Actually get the data
print('Requesting data from IEM...')

lsr_request = requests.get(lsr_endpoint)
lsrs = lsr_request.json()['features']

# Make the LSR database
print('Creating local database...')

lsr_con = sql.connect("lsr.db")
lsr_cur = lsr_con.cursor()
lsr_cur.execute("CREATE TABLE lsrs_raw (city char, county char, lat decimal, lon decimal, magnitude char, remark char, source char, st char, type char, typetext char, valid datetime, wfo char)")
lsr_con.commit()

# Save the data
print('Loading into local database...')

query = "INSERT INTO lsrs_raw (city, county, lat, lon, magnitude, remark, source, st, type, typetext, valid, wfo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
for lsr_row in lsrs:
    lsr = lsr_row['properties']
    if type_to_icon(lsr['type']):
        lsr_cur.execute(query, [lsr['city'], lsr['county'], lsr['lat'], lsr['lon'], lsr['magnitude'], lsr['remark'], lsr['source'], lsr['st'], lsr['type'], lsr['typetext'], lsr['valid'], lsr['wfo']])
lsr_con.commit()

print('Done!')