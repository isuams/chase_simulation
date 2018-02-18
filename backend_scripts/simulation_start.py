#!/usr/local/miniconda3/bin/python

"""
Simulation Control - Start
--------------------------

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
import json, pytz, shutil
from datetime import datetime, timedelta
from dateutil import parser, tz
from ChaseLib.Timing import std_fmt

# Critical Files/Directories
master_file = "master.json"
rad_db_file = "radar.db"
lsr_endpoint_dir = '/home/jthielen/WWW/chase/endpoints/'

# Greetings!
print('\nISU AMS Chase Simulation\n------------------------\n')

# Get the user input
arc_start_time = parser.parse(input('When does the archived case start?\n\t(use UTC) : '))
cur_start_time = input('When does the current simulation of the case start?\n\t(enter now for now) : ')
if cur_start_time[0] in ['n', 'N']:
	cur_start_time = datetime.utcnow()
else:
	cur_start_time = parser.parse(cur_start_time)
speed_factor = float(input('What is the simulation speed-up factor? : '))

# Get radar scan interval for user confirmation prompt
rad_con = sql.connect(rad_db_file)
rad_cur = rad_con.cursor()
rad_cur.execute('SELECT time from scans ORDER BY time ASC')
scan_times = [scan[0] for scan in rad_cur.fetchall()]
arc_td = (parser.parse(scan_times[-1]) - parser.parse(scan_times[0])).seconds
cur_td = arc_td / speed_factor

arc_h = arc_td // 3600
arc_m = arc_td % 3600 // 60
arc_td_str = '{}h{}m'.format(arc_h, arc_m)
cur_h = cur_td // 3600
cur_m = cur_td % 3600 // 60
cur_td_str = '{}h{}m'.format(cur_h, cur_m)

# Confirmation
print("...To confirm...")
print("\tDo you wish to start the simulation of archived case")
print("\t{} (having {} of radar data)".format(arc_start_time.strftime(std_fmt), arc_td_str))
print("\tstarting at current time")
print("\t{} (having {} of radar data)?".format(cur_start_time.strftime(std_fmt), cur_td_str))
print()

confirm = input('[Y]es/[N]o: ')

if confirm[0] in ['Y', 'y']:

	# Create master file
	with open(master_file, 'w') as f:

		timings = {
			'arc_start_time': arc_start_time.strftime(std_fmt),
			'cur_start_time': cur_start_time.strftime(std_fmt),
			'speed_factor': speed_factor,
			'simulation_running': True
		}
		json.dump(timings, f)

	shutil.copyfile(master_file, lsr_endpoint_dir + master_file)
	
	print("Simulation timing started.")
	print("Nothing is actually happening yet...")
	print("To do that, run simulation_radar.py (radar scans) and simulation_warning.py (warning text).")
	print("To reset, run simulation_reset.py, and to pause, hack on the master file.")
	print("\nHave fun!")

else:
	print('Canceled...')