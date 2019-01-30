#!/usr/bin/env python

"""
Base Classes for Chase Applet

These are the base classes to make the chase applet work, regardless of interface.
"""

# from sqlite3 import dbapi2 as sql


class Config:
    """Base class for application configuration.

    Used for global settings.

    Old Global Settings:
    --------------------

    sim_time
    speedup
    slp_time (approx between radar scans)
    spd_limit
    fill_rate
    stuck_time
    cc_time (chaser convergence start time)
    sunset_time (affects hazard chances)
    dr_chance (dirt road prob)
    cc_chance (chaser convergence chance)
    tire_chance (flat tire chance)
    dead_end_chance
    flood_chance
    extra_all_time (extra time to add to _all placefile)
    """

    # Data dictionary for storing config
    data = {}

    def __init__(self, data):
        self.data = data


class Team:
    """...

    Old Details
    -----------
    time_now
    d
    Team_Name
    C_Team_Name
    Car_Type
    top_speed
    mpg
    fuel_cap
    stuck_chance
    lat
    lon
    speed
    mins
    refuel_slp
    cop_slp
    stuck_slp
    tire_slp
    cc_turns
    init_time
    fuel_level
    time_step
    direct
    dr_direct
    dr_deg
    dist
    dr_dist
    cc_top_spd
    dr_top_spd
    aft_dark_inc
    sun_check
    dead_check
    dr_check
    new_deg
    old_direct

    """
    data = {}

    def __init__(self, data):
        self.data = data

    """
    API to define:

    has_action_queue_items()
    get_action_queue()
    get_current_hazard()
    points
    speed
    current_max_speed
    direction

    """


class Vehicle:
    """
    ...
    """
    # Configuration Variables
    vehicle_type = None
    print_name = '(None)'
    top_speed = 135  # mph
    top_speed_on_dirt = 45  # mph
    efficient_speed = 60  # mph
    mpg = 38  # mpg
    fuel_cap = 13  # gallons
    stuck_probability = 0.01  # chance per current minute
    cost = 0.0  # dollars

    def __init__(self, cursor, vehicle_type):
        self._cursor = cursor
        data = self._query(('SELECT print_name, top_speed, top_speed_on_dirt, '
                            'efficient_speed, mpg, fuel_cap, stuck_probability, cost FROM'
                            'vehicles WHERE vehicle_type = ?'), [vehicle_type])
        if len(data) != 1:
            raise ValueError('Vehicle type' + str(vehicle_type) + ' not found.')
        else:
            self.vehicle_type = vehicle_type
            self.print_name = data[0][0]
            self.top_speed = float(data[0][1])
            self.top_speed_on_dirt = float(data[0][2])
            self.efficient_speed = float(data[0][3])
            self.mpg = float(data[0][4])
            self.fuel_cap = float(data[0][5])
            self.stuck_probability = float(data[0][6])
            self.cost = float(data[0][7])

    def _query(self, *args):
        # Run a DB query on the DB cursor given
        self._cursor.execute(*args)
        return self._cursor.fetchall()

    def calculate_mpg(self, current_speed):
        # Calculate mpg based on current speed and vehicle specs
        if current_speed <= self.efficient_speed:
            multiplier = 1 + ((current_speed - self.efficient_speed)**4 *
                              (3 / self.efficient_speed**4))
        else:
            multiplier = 1 + ((current_speed - self.efficient_speed)**2 *
                              (3 / (self.top_speed - self.efficient_speed)**2))

        return self.mpg / multiplier


class Action:
    """
    ...
    """
    is_adjustment = False
    is_hazard = False
    message = ''

    def __init__(self, data):
        self._data = data

    def dismiss():
        # TODO: Dismiss this action in the db
        return

    def apply_to(self, team):
        # TODO: Apply this action to this team
        return


class Hazard(Action):
    """
    ...
    """
    is_adjustment = False
    is_hazard = True

    def __init__(self, data):
        self.data = data
