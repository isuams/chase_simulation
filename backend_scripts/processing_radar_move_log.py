#!/usr/local/miniconda3/bin/python

"""
Radar Move and Log
------------------

This script stages the radar files for use in the simulation.

To prepare the radar data for processing via the script, complete the following steps first:

1. Download the radar data from [NCDC](https://www.ncdc.noaa.gov/has/HAS.DsSelect) after placing an order
2. You will have a large number of `.tar` files. Untar them all with the command
    ```
    for f in NWS_NEXRAD_NXL2DP_*.tar; do tar -xvf $f; done
    ```
    (this should take under a minute on chinook)
3. From that, you'll now have (an even larger) number of `.gz` files. Unzip them all with the command
    ```
    for f in K*.gz; do gzip -d $f; done
    ```
    (this should take under an hour on chinook)
4. Now you're ready to use this script! Make sure you have your current raw data directory, staging directory, and start and end times ready, and update the constants values below.

! IMPORTANT !
Update the constants to their proper values, and update the shebang above to your conda environment.

What this script does:

- Finds all *_V06 files in `radar_raw_dir`
- Assembles a list of dicts with scan info (site, datetime, file name) while filtering to just include scans during simulation timeframe
- Updates filenames of simulation scans and moves them to staging directory
- Creates a database of the basic scan info for use by the `simulation_radar.py` script during the simulation

"""

# Imports
import glob, os, pytz, time
from sqlite3 import dbapi2 as sql
from datetime import datetime, timedelta
from dateutil import parser, tz
from ChaseLib.Timing import std_fmt

# Constants

# Archive Times
arc_start_time = datetime(2010, 6, 1, 0, 0, 0, tzinfo=pytz.UTC)
arc_end_time = datetime(2010, 6, 1, 6, 0, 0, tzinfo=pytz.UTC)

# Critical Directories
radar_raw_dir = '/chinook2/jthielen/chase_2018/HAS011062487/'
radar_staging_dir = '/chinook2/jthielen/chase_2018/radar/'

# Processing

# Get the files
print('Getting files...')
glob_list = glob.glob(radar_raw_dir + '*_V06')

# Assemble the list of scans we want with nice dictionaries
scan_list = []
for i in range(len(glob_list)):
    filename_full = glob_list[i]
    filename_part = filename_full.split("/")[-1]
    
    site = filename_part[0:4]
    year = int(filename_part[4:8])
    month = int(filename_part[8:10])
    day = int(filename_part[10:12])
    hour = int(filename_part[13:15])
    minute = int(filename_part[15:17])
    second = int(filename_part[17:19])
    
    scan_datetime = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)
    
    if arc_start_time <= scan_datetime <= arc_end_time:
        scan_list.append({
            'file': filename_full,
            'file_part': filename_part,
            'site': site,
            'datetime': datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)
        })

# Move the files
for scan in scan_list:
    print('Moving {} {}'.format(scan['site'], scan['datetime'].strftime(std_fmt)))
    new_file = radar_staging_dir + scan['file_part'][:-4]
    os.rename(scan['file'], new_file)
    scan['file'] = new_file 

# Create the scan database
print('Exporting to DB...')
rad_con = sql.connect("radar.db")
rad_cur = rad_con.cursor()
rad_cur.execute("CREATE TABLE scans (time datetime, site char, file char, munged tinyint)")
rad_con.commit()

# Insert all the records
for scan in scan_list:
    rad_cur.execute("INSERT INTO scans (time, site, file) VALUES (?,?,?)", [scan['datetime'].strftime(std_fmt), scan['site'], scan['file']])
    
rad_con.commit()

print('Done!')
