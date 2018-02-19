#!/usr/bin/env python

"""
@todo clear the master.json file, clear the output warning and radar folders, and reset warning.db and radar.db to be unprocessed

fields to set:

arc_start_time
cur_start_time
speed_factor
simulation_running


what to do:

get the archive start time and speed factor by prompt
verify the info
save the master.json info
prompt to start simulation_radar.py and simulation_warning.py, and exit
"""

# Imports
import json, os, pytz, shutil
from sqlite3 import dbapi2 as sql
from datetime import datetime, timedelta
from dateutil import parser, tz
from ChaseLib.Timing import std_fmt

# Critical Files/Directories
master_file = "master.json"
rad_db_file = "radar.db"
warn_db_file = "warning.db"
radar_deploy_dir = '/home/jthielen/WWW/chase/l2data/'
warning_dir = "/home/jthielen/WWW/chase/warnings/"
lsr_endpoint_dir = '/home/jthielen/WWW/chase/endpoints/'

# Greetings!
print('\nRESET!\n------\n')

# Establish DB connection
warn_con = sql.connect(warn_db_file)
warn_cur = warn_con.cursor()
rad_con = sql.connect(rad_db_file)
rad_cur = rad_con.cursor()

# Get sites
rad_cur.execute('SELECT site from scans GROUP BY site')
sites = [site[0] for site in rad_cur.fetchall()]

# Confirm
confirm = input('[Y]es/[N]o: ')

if confirm[0] in ['Y', 'y']:

	# Clear master file
	with open(master_file, 'w') as f:
		json.dump({}, f)

	shutil.copyfile(master_file, lsr_endpoint_dir + master_file)

	# Clear folders
	folders = [warning_dir]
	for site in sites:
		folders.append(radar_deploy_dir + site + '/')

	for folder in folders:
		for the_file in os.listdir(folder):
		    file_path = os.path.join(folder, the_file)
		    try:
		        if os.path.isfile(file_path):
		            os.unlink(file_path)
		    except Exception as e:
		        print(e)

	# Add back the blank dir lists
	for site in sites:
		os.system("touch {dir}dir.list".format(dir=radar_deploy_dir+ site + '/'))

	# Mark the databases as unprocessed/unmunged
	warn_cur.execute('UPDATE warnings_raw SET processed = 0')
	warn_con.commit()
	rad_cur.execute('UPDATE scans SET munged = 0')
	rad_con.commit()

	print('Chase case reset.')

else:
	print('Canceled...')
