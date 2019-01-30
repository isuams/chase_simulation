#!/home/jthielen/miniconda3/envs/chase/bin/python

"""
Chase Applet Endpoint
---------------------

Remote python backend for the chase web applet

...

! IMPORTANT !
Update the constants to their proper values, and update the shebang above to
your conda environment.

What this script does when run:

- Validates setup and POSTed team ID, speed, and direction, and if refueling
- Integrate forward position (or refuel)
- Check queue for triggered actions
- "Roll the dice" for random hazards
- Save status to database
- Return status JSON

"""

# Imports
import cgi
from datetime import datetime
from dateutil import parser
import json
import numpy as np
from ChaseLib import *  # fake for now


# Constants

# Critical Files
master_db_file = 'master.db'
team_db_dir = 'teams/'


# Functions
# TODO: Move outside of this file
def lat_lon_diff(distance_miles, angle_degrees):
    """Calculate difference in lat/lon crudely (but good enough for the plains)."""
    angle = np.deg2rad(angle_degrees)
    diff_lat = ((math.cos(angle) * distance_miles) * 0.016740)
    diff_lon = ((math.sin(angle) * distance_miles) * 0.022180)
    return diff_lat, diff_lon


def heading_str_from_angle(angle_degrees):
    # TODO: text for heading from angle
    return


def money_format(money):
    # TODO: Make a nice money string from a float
    return


# Input Handling

form = cgi.FieldStorage()
team_id = form.getvalue('team_id')
speed = form.getvalue('speed')
direction = form.getvalue('direction')
refuel = bool(form.getvalue('refuel'))

# TODO: Core config
speed_factor = 4.0
gas_price = 2.25  # dollars per gallon

"""
TODO: Error Conditions

Error out if
- {team_id}.db is not found
- ...
"""

team = Team(team_db_dir + team_id + '.db')
past_status = team.get_last_status()
current_hazard = team.get_current_hazard()
message_list = []


"""
TODO: Sanitization

If refuel, then set speed = 0 and direction = 0
If speed <= 0, then set speed = 0 and direction = 0
If speed > current max speed, then set speed = current max speed
If direction not parseable to angle (if not number or from metpy.calc.parse_angle), then
    set to random angle
"""

# Movement Updates

# Prep
current_time = datetime.now(tz=pytz.UTC)
diff_time = current_time - parser.parse(past_status['timestamp'])
distance = speed * speed_factor * diff_time.seconds / 3600
diff_lat, diff_lon = lat_lon_diff(distance, direction)

# Position and movement
team.lat += diff_lat
team.lon += diff_lon
team.speed = speed
team.direction = heading_str_from_angle(direction)

# Gas
if refuel:
    fuel_amt = team.vehicle.fuel_cap - team.fuel_level
    team.fuel_level += fuel_amt
    team.balance -= fuel_amt * gas_price
    # TODO: make sure they are stuck for the designated time period
else:
    fuel_amt = distance * team.vehicle.calculate_mpg(speed)
    team.fuel_level -= fuel_amt

# TODO check current_hazard expiry

# Check queue for action items
if team.has_action_queue_items():
    hazard_queued = False
    for action in team.get_action_queue():
        if not action.is_hazard:
            if action.is_adjustment:
                action.apply_to(team)
            message_list.append(action.message)
            action.dismiss()
        elif action.is_hazard and not hazard_queued:
            current_hazard = action
            hazard_queued = True
            action.dismiss()
        # Note that hazards other than the first are ignored...and they automatically
        # overwrite any existing hazard.

# Handle hazards

# See if adding a new one!
if current_hazard is not None:
    # TODO: roll the dice for new hazard
    new_hazard = shuffle_new_hazard(team, diff_time)

# TODO: actually handle a current hazard

# Save results and output

if current_hazard is not None:
    message_list.append(current_hazard.message)
    team.set_current_hazard(current_hazard)
team.write_status()

output = {
    'team_id': team_id,
    'location': '42.089, -93.768 (5 Mi E Boone, IA)',
    'status_text': 'In Chaser Convergence',
    'status_color': 'warning',
    'fuel_text': '5 gallons (40%) remaining',
    'fuel_color': None,
    'can_refuel': False,
    'balance': money_format(team.balance),
    'balance_color': None,
    'points': team.points,
    'speed': team.speed,
    'current_max_speed': team.current_max_speed,
    'direction': team.direction,
    'can_move': True,
    'messages': '0300Z: You are still stuck in chaser convergence'
}  # TODO: real, not this sample

# Return output
print('Content-type: application/json\r\n')
print(json.dumps(output))
