#!/usr/bin/env python

"""
Simulation Looper - Radar
-------------------------

The radar simulation script

Basically, merges the simulation_warning.py script with the old *_fake_realtime.py
script to have radar munging and updating, but in the database oriented style of
the new warnings script.

! Make sure that the l2munger is in ./munge/l2munger relative to this file

Also, handles site folder creation.
"""

# Imports
import glob, json, os, pytz, re, requests, textwrap, time, shutil
from sqlite3 import dbapi2 as sql
from datetime import datetime, timedelta
from dateutil import parser, tz
from ChaseLib.Timing import arc_time_from_cur, cur_time_from_arc, std_fmt


# Critical Files/Directories
rad_db_file = "radar.db"
master_file = "master.json"
radar_staging_dir = '/chinook2/jthielen/chase_2018/radar/'
radar_deploy_dir = '/home/jthielen/WWW/chase/l2data/'

# Minimum amount of time to wait between loops
min_sleep = 10
max_sleep = 20

# Establish DB connection
rad_con = sql.connect(rad_db_file)
rad_cur = rad_con.cursor()

# Get the master settings
with open(master_file) as master_data:
    settings = json.load(master_data)

if settings['simulation_running']:

    # Report Status
    print("\nSimulation Looper - Radar\n-------------------------\n")
    print("Archive Start Time: {}".format(settings['arc_start_time']))
    print("Current Start Time: {}".format(settings['cur_start_time']))
    print("Speed Factor: {}\n\n\n".format(settings['speed_factor']))

    running = True
    while running:

        # Check if still running
        with open(master_file) as master_data:
            settings = json.load(master_data)
        if not settings['simulation_running']:
            running = False
            continue


        # Do processing
        

        # Get the now times
        cur_now = datetime.now(tz=pytz.UTC)
        arc_now = arc_time_from_cur(cur_now, settings)

        # Check if any scans to release
        rad_cur.execute('SELECT * FROM scans WHERE time <= ? AND (munged = 0 or munged IS NULL)', [arc_now.strftime(std_fmt)])
        scans_to_release = rad_cur.fetchall()

        if len(scans_to_release) > 0:

            print('Processing {} scans for {}...'.format(len(scans_to_release), cur_now.strftime(std_fmt)))

            # Loop over the scans
            for scan_row in scans_to_release:

                # Release the scan!

                # Get scan vars
                site = scan_row[1]
                arc_scan_time = scan_row[0]
                cur_scan_time = cur_time_from_arc(arc_scan_time, settings)
                arc_file = scan_row[2]

                # Status
                print('\t{}\t{} --> {}'.format(site, arc_scan_time, cur_scan_time))

                # Verify that the site directory exists (if not, create it)
                site_deploy_dir = radar_deploy_dir + site + '/'
                if not os.path.isdir(site_deploy_dir):
                    os.makedirs(site_deploy_dir)


                # Munge and move
                munge_cmd = './munge/l2munger {} {} {}'.format(
                    site,
                    parser.parse(cur_scan_time).strftime('%Y/%m/%d %H:%M:%S'),
                    arc_file
                )
                list_cmd = "ls -l {site}* | awk '{{print $5 \" \" $9}}' > dir.list".format(site=site)
                cur_file = parser.parse(cur_scan_time).strftime(site + '%Y%m%d_%H%M%S')

                os.system(munge_cmd)
                shutil.copyfile(cur_file, site_deploy_dir + cur_file)
                os.remove(cur_file)
                proper_dir = os.path.dirname(os.path.realpath(__file__))
                os.chdir(site_deploy_dir)
                os.system(list_cmd)
                os.chdir(proper_dir)


                # Finally, log it as processed
                rad_cur.execute('UPDATE scans SET munged = 1 WHERE file = ?', [arc_file])
                rad_con.commit()

            print('\tScans processed.')

        else:
            print('No scans to release for {}.'.format(cur_now.strftime(std_fmt)))


        # Find the next scan to release
        rad_cur.execute('SELECT * FROM scans WHERE (munged = 0 or munged IS NULL) ORDER BY time ASC LIMIT 1')
        scans_in_waiting = rad_cur.fetchall()


        if len(scans_in_waiting) > 0:

            # We have a next scan, sleep until it comes
            arc_next = parser.parse(scans_in_waiting[0][0])
            cur_next = cur_time_from_arc(arc_next, settings)

            print('\tNext scan incoming at {}...'.format(cur_next.strftime(std_fmt)))

            sleep = (cur_next - datetime.now(tz=pytz.UTC)).seconds + 1
            if sleep < min_sleep:
                sleep = min_sleep # Don't need to be going too rapid fire...
            elif sleep > max_sleep:
                sleep = max_sleep # Don't wait for any bugs in timing
            print('\tSleeping for {} seconds {}'.format(sleep, json.dumps([cur_next.strftime(std_fmt), datetime.now(tz=pytz.UTC).strftime(std_fmt)])))
            time.sleep(sleep)

        else:

            # No more scans! We're done!
            running = False


    print('\n\n\nRadar scans for simulation completed.\nHope it was fun!\n')
else:
    print('\nSimulation not currently running.\nPlease rerun once simulation is started.\n')
