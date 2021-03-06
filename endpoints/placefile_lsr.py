#!/home/jthielen/miniconda3/envs/chase/bin/python

"""
LSR Placefile Endpoint
----------------------

Provides the LSR placefile during the simulation.

...

! IMPORTANT !
Update the constants to their proper values, and update the shebang above to
your conda environment.

What this script does when run:

- Gets the LSRs during the valid time

"""

# Imports
import json
import pytz
import sys
from sqlite3 import dbapi2 as sql
from datetime import datetime, timedelta
from ChaseLib.LSR import (scale_raw_lsr_to_cur_time,
                          gr_lsr_placefile_entry_from_tuple)
from ChaseLib.Timing import arc_time_from_cur, std_fmt


# Constants

# Critical Files
lsr_db_file = "lsr.db"
master_file = "master.json"

# LSR Validity (archive time)
hours_valid = 1

# Text Control
remark_wrap_length = 40

# Assets
lsr_asset_url = 'http://www.meteor.iastate.edu/~jthielen/chase/LSR/'


# Processing

# Get the master settings
with open(master_file) as master_data:
    settings = json.load(master_data)

# Output

# Output HTTP Header
print("Content-type: text/plain\r\n")

# Header
print("""\n
RefreshSeconds: 5
Threshold: 999
Title: Live Storm Reports (LSRs)
Font: 1, 11, 0, "Courier New"
IconFile: 1, 25, 25, 11, 11, "{url}Lsr_FunnelCloud_Icon.png"
IconFile: 2, 25, 32, 11, 11, "{url}Lsr_Hail_Icons.png"
IconFile: 3, 25, 25, 11, 11, "{url}Lsr_Tornado_Icon.png"
IconFile: 4, 25, 25, 11, 11, "{url}Lsr_TstmWndDmg_Icon.png"
""".format(url=lsr_asset_url))

if len(settings) == 0:
    # Exit early
    sys.exit()

# Open database
lsr_con = sql.connect(lsr_db_file)
lsr_cur = lsr_con.cursor()

# Prep the time interval (arc time)
t1 = arc_time_from_cur(datetime.now(tz=pytz.UTC), timings=settings)
t0 = t1 - timedelta(hours=hours_valid)
t0, t1 = (t.strftime(std_fmt) for t in [t0, t1])

# Get the data
lsr_cur.execute("SELECT * FROM lsrs_raw WHERE valid BETWEEN ? AND ?", [t0, t1])
lsrs_raw = lsr_cur.fetchall()

# Scale the data to cur time
lsrs_scaled = scale_raw_lsr_to_cur_time(lsrs_raw, timings=settings)

# Output the LSRs
for lsr_tuple in lsrs_scaled:
    print(gr_lsr_placefile_entry_from_tuple(
        lsr_tuple,
        wrap_length=remark_wrap_length
    ))
    print()
