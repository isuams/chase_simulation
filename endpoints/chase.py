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
from ChaseLib.functions import *


# Constants
master_db_file = 'main.db'
team_db_dir = 'teams/'

# Wrap full process to safely catch errors
config = team = None
try:
    # Establish core config
    config = Config(master_db_file)
    
    # Establish the list of hazards TODO TODO
    hazard_list = []
    
    # Input Handling
    form = cgi.FieldStorage()
    team_id = form.getvalue('team_id')
    speed = float(form.getvalue('speed'))
    direction = float(form.getvalue('direction'))
    refuel = bool(form.getvalue('refuel'))
    
    # Set Up Team
    team = Team(team_db_dir + team_id + '.db')
    message_list = []
    
    # Sanitize input values
    if team.cannot_refuel:
        refuel = False

    if refuel or speed <= 0 or team.stopped:
        speed = 0
        direction = 0
        
    if speed > team.current_max_speed():
        speed = team.current_max_speed()
        
    # Movement Updates
    current_time = datetime.now(tz=pytz.UTC)
    diff_time = current_time - team.last_update_time
    distance = speed * config.speed_factor * diff_time.seconds / 3600
    diff_lat, diff_lon = lat_lon_diff(distance, direction)
    team.lat += diff_lat
    team.lon += diff_lon
    team.speed = speed
    team.direction = direction

    # Gas management
    if refuel:
        fuel_amt = min(diff_time.seconds * config.fill_rate,
                       team.vehicle.fuel_cap - team.fuel_level)
        team.fuel_level += fuel_amt
        team.balance -= fuel_amt * gas_price
        done_refueling = (team.fuel_level >= team.vehicle.fuel_cap - .01)
    else:
        fuel_amt = distance / team.vehicle.calculate_mpg(speed)
        team.fuel_level -= fuel_amt
        
    # Current hazard/hazard expiry
    if (team.active_hazard is not None and 
        team.active_hazard.expiry_time <= datetime.now(tz=pytz.UTC)):
            message_list.append(team.active_hazard.generate_expiry_message())
            team.clear_active_hazard()
            
    # Check queue for action items (either instant action or a hazard to queue)
    queued_hazard = None
    if team.has_action_queue_items():
        for action in team.get_action_queue():
            if not action.is_hazard:
                if action.is_adjustment:
                    team.apply_action(action)
                message_list.append(action.generate_message())
                team.dismiss_action(action)
            elif action.is_hazard and queued_hazard is None:
                queued_hazard = action
                
    # If no hazard queued, shuffle in a chance of a random hazard
    if queued_hazard is None:
        queued_hazard = shuffle_new_hazard(team, diff_time.seconds, hazard_list)
        
    # Apply the queued hazard if it overrides a current hazard (otherwise ignore)
    if team.active_hazard is None or team.active_hazard.overridden_by(queued_hazard):
        team.apply_hazard(queued_hazard)  # actually make it take effect
        message_list.append(queued_hazard.generate_message())
        team.dismiss_action(queued_hazard)  # in case it was from DB
    
    # Prepare for output
    team.write_status()
    output = {**team.output_status_dict(), 'messages': message_list}
except Exception as exc:
    # Error Handling
    output = {'error': True, 'error_message': str(exc)}
finally:
    # Return output
    print('Content-type: application/json\r\n')
    print(json.dumps(output))
