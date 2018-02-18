#!/usr/local/miniconda3/bin/python

"""
LSR Placefile Endpoint
----------------------

Provides the LSR placefile during the simulation.

...

! IMPORTANT !
Update the constants to their proper values, and update the shebang above to your conda environment.

What this script does when run:

- Gets the LSRs during the valid time

"""

# Imports
import glob, json, os, pytz, re, requests, textwrap, time
from sqlite3 import dbapi2 as sql
from datetime import datetime, timedelta
from dateutil import parser, tz
from ChaseLib.LSR import type_to_icon


# Constants

# Critical Files
lsr_db_file = "lsr.db"
master_file = "../backend_scripts/master.json"

# Text Control
remark_wrap_length = 40

# Assets
lsr_asset_url = 'http://www.meteor.iastate.edu/~tuftedal/chase/LSR/'


# Processing

# Open database
lsr_con = sql.connect(lsr_db_file)
lsr_cur = lsr_con.cursor()


# Output HTTP Header
print("Content-type: application/json\r\n\r\n")

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

# @todo actually do the rest