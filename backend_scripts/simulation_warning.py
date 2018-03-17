#!/usr/bin/env python

"""
Simulation Looper - Warnings
----------------------------

This script handles warning deployment during the simulation.

...

! IMPORTANT !
Update the constants to their proper values, and update the shebang above to
your conda environment.

What this script does:

- ...

"""

# Imports
import json
import pytz
import time
from sqlite3 import dbapi2 as sql
from datetime import datetime
from dateutil import parser
from ChaseLib.Timing import arc_time_from_cur, cur_time_from_arc, std_fmt
from ChaseLib.Warning import process_warning_text


# Critical Files/Directories
warn_db_file = "warning.db"
master_file = "master.json"
warning_dir = "/home/jthielen/WWW/chase/warnings/"

# Minimum amount of time to wait between loops
min_sleep = 10

# Establish DB connection
warn_con = sql.connect(warn_db_file)
warn_cur = warn_con.cursor()

# Get the master settings
with open(master_file) as master_data:
    settings = json.load(master_data)

if settings['simulation_running']:

    # Report Status
    print("\nSimulation Looper - Warnings\n----------------------------\n")
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

        # Check if any warnings to release
        warn_cur.execute(
            'SELECT * FROM warnings_raw WHERE valid <= ? AND ' +
            '(processed = 0 OR processed IS NULL)', [arc_now.strftime(std_fmt)]
        )
        warnings_to_release = warn_cur.fetchall()

        if len(warnings_to_release) > 0:

            print('Processing {} warning(s) for {}...'.format(
                len(warnings_to_release),
                cur_now.strftime(std_fmt))
            )

            # Loop over the warnings
            for warning_row in warnings_to_release:

                # Release the warning!

                # First, process the text
                warning = warning_row[1]
                warning, warning_cur_time = process_warning_text(
                    warning,
                    timings=settings
                )

                # Then, determine the proper warning txt file, and append this
                # warning
                warning_file = warning_dir + warning_cur_time.strftime(
                    'warnings_%Y%m%d_%H.txt'
                )
                with open(warning_file, 'a') as f:
                    f.write(warning)

                # Finally, log it as processed
                warn_cur.execute(
                    'UPDATE warnings_raw SET processed = 1 WHERE text = ?',
                    [warning_row[1]]
                )
                warn_con.commit()

            print('\tWarnings processed.')

        else:
            print('No warnings to release for {}.'.format(
                cur_now.strftime(std_fmt))
            )

        # Find the next warning to release
        warn_cur.execute(
            'SELECT * FROM warnings_raw WHERE ' +
            '(processed = 0 OR processed IS NULL) ORDER BY valid ASC LIMIT 1'
        )
        warnings_in_waiting = warn_cur.fetchall()

        if len(warnings_in_waiting) > 0:

            # We have a next warning, sleep until it comes
            arc_next = parser.parse(warnings_in_waiting[0][0])
            cur_next = cur_time_from_arc(arc_next, settings)

            print('\tNext warning incoming at {}...'.format(
                cur_next.strftime(std_fmt))
            )

            sleep = (cur_next - datetime.now(tz=pytz.UTC)).seconds + 1
            if sleep < min_sleep:
                sleep = min_sleep  # Don't need to be going too rapid fire...
            time.sleep(sleep)

        else:

            # No more warnings! We're done!
            running = False

    print('\n\n\nWarnings for simulation completed.\nHope it was fun!\n')
else:
    print('\nSimulation not currently running.\n' +
          'Please rerun once simulation is started.\n')
