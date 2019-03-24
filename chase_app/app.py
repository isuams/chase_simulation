#!/usr/bin/env python

"""
Base Classes for Chase Applet

These are the base classes to make the chase applet work, regardless of interface.
"""

import pytz
from sqlite3 import dbapi2 as sql
from dateutil import parser
from datetime import datetime
from ChaseLib.functions import money_format


db_time_fmt = '%Y-%m-%dT%H:%M:%S'


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

    New Global Settings:
    --------------------
    speed_factor
    gas_price ($/gallon)
    fill_rate (gallon/sec)
    """

    def __init__(self, path):
        """Construct underlying sqlite connection."""
        self.con = sql.connect(path)
        self.cur = self.con.cursor()

    def get_config_value(self, config_setting):
        self.cur.execute('SELECT config_value FROM config WHERE config_setting = ?',
                         [config_setting])
        return self.cur.fetchall()[0][0]

    @property
    def speed_factor(self):
        return int(self.get_config_value('speed_factor'))

    @property
    def gas_price(self):
        return float(self.get_config_value('gas_price'))

    @property
    def fill_rate(self):
        return float(self.get_config_value('fill_rate'))


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
    status = {}
    active_hazard = None
    vehicle = None

    def __init__(self, path, hazards):
        """Construct underlying sqlite connection, and set initial state."""
        self.con = sql.connect(path)
        self.cur = self.con.cursor()

        self.cur.execute('SELECT team_setting, team_value FROM team_info')
        self.status = dict(self.cur.fetchall())

        if str(self.status['active_hazard']).lower() not in ['', 'none', 'false']:
            self.active_hazard = hazards[self.status['active_hazard']]
            self.active_hazard.expiry_time = parser.parse(self.status['hazard_exp_time'])

        # self.vehicle TODO

    @property
    def cannot_refuel(self):
        """Determine if the current team cannot refuel."""
        # TODO
        return False

    @property
    def stopped(self):
        """Determine if the current team is stopped."""
        return False or (self.active_hazard is not None and self.active_hazard.speed_lock)

    def current_max_speed(self):
        """Determine the current maximum speed."""
        if self.active_hazard is not None:
            if self.active_hazard.type == 'dirt_road':
                return self.vehicle.top_speed_on_dirt
            elif self.active_hazard.speed_limit is not None:
                return self.active_hazard.speed_limit
        else:
            return self.vehicle.top_speed

    @property
    def last_update_time(self):
        """Give the datetime of last update (in current time)."""
        return parser.parse(self.status['timestamp'])

    @property
    def lat(self):
        """Get the latitude."""
        return self.status['latitude']

    @lat.setter
    def lat(self, value):
        """Set the latitude."""
        self.status['latitude'] = value

    @property
    def lon(self):
        """Get the longitude."""
        return self.status['longitude']

    @lon.setter
    def lon(self, value):
        """Set the longitude."""
        self.status['longitude'] = value

    @property
    def speed(self):
        """Get the speed."""
        return self.status['speed']

    @speed.setter
    def speed(self, value):
        """Set the speed."""
        self.status['speed'] = value

    @property
    def direction(self):
        """Get the direction."""
        return self.status['direction']

    @direction.setter
    def direction(self, value):
        """Set the direction."""
        self.status['direction'] = value

    @property
    def fuel_level(self):
        """Get the fuel_level."""
        return self.status['fuel_level']

    @fuel_level.setter
    def fuel_level(self, value):
        """Set the fuel_level."""
        self.status['fuel_level'] = value

    @property
    def balance(self):
        """Get the balance."""
        return self.status['balance']

    @balance.setter
    def balance(self, value):
        """Set the balance."""
        self.status['balance'] = value

    def clear_active_hazard(self):
        """Clear the active hazard."""
        self.active_hazard = None
        self.status['status_color'] = 'green'
        self.status['status_text'] = 'Chase On'

    def has_action_queue_item(self):
        self.cur.execute('SELECT * FROM action_queue WHERE action_taken IS NULL')
        return (len(self.cur.fetchall()) > 0)

    def get_action_queue(self, hazards):
        self.cur.execute('SELECT * FROM action_queue WHERE action_taken IS NULL')
        for action_tuple in self.cur.fetchall():
            if action_tuple[2] == 'hazard':
                hazard = hazards[action_tuple[3]]
                hazard.action_id = action_tuple[0]
                yield hazard
            else:
                yield Action(action_tuple=action_tuple)

    def apply_action(self, action):
        """Apply the action to this team."""
        self.status = action.alter_status(self.status)

    def dismiss_action(self, action):
        """Dismiss action from the action queue."""
        if action.action_id is not None:
            self.cur.execute('UPDATE action_queue SET action_taken = ? WHERE action_id = ?',
                             [datetime.now(tz=pytz.UTC).strftime(db_time_fmt),
                              action.action_id])

    def apply_hazard(self, hazard):
        """Apply the hazard to this team."""
        self.status = hazard.alter_status(self.status)
        self.active_hazard = hazard

    def write_status(self):
        """Save the current status of this team in DB."""
        if self.active_hazard is None:
            self.status['active_hazard'] = ''
            self.status['hazard_exp_time'] = ''
        else:
            self.status['active_hazard'] = self.active_hazard.type
            self.status['hazard_exp_time'] = (
                self.active_hazard.expiry_time.strftime(db_time_fmt))

        self.status['timestamp'] = datetime.now(tz=pytz.UTC).strftime(db_time_fmt)

        for key, value in self.status.items():
            self.cur.execute('UPDATE team_info SET team_value = ? WHERE team_setting = ?',
                             [value, key])

        self.cur.execute(('INSERT INTO team_history (timestamp, latitude, longitude, '
                          'speed, direction, status_color, status_text, balance, '
                          'points, fuel_level, active_hazard) VALUES '
                          '(?,?,?,?,?,?,?,?,?,?,?)'),
                         [self.status[key] for key in ('timestamp', 'latitude',
                                                       'longitude', 'speed',
                                                       'direction', 'status_color',
                                                       'status_text', 'balance',
                                                       'points', 'fuel_level',
                                                       'active_hazard')])
        self.con.commit()

    def output_status_dict(self):
        """Output the dict for JSON to web app."""
        color = {'green': 'success', 'yellow': 'warning', 'red': 'danger'}[
            self.status['status_color']]
        direction_lock = False or (self.active_hazard is not None and
                                   self.active_hazard.direction_lock)
        speed_lock = False or (self.active_hazard is not None and
                               self.active_hazard.speed_lock)
        output = {
            'team_id': self.status['team_id'],
            'location': '42.089, -93.768 (5 Mi E Boone, IA)',  # TODO
            'status_text': self.status['status_text'],
            'status_color': color,
            'fuel_text': '5 gallons (40%) remaining',  # TODO
            'fuel_color': None,  # TODO
            'can_refuel': not self.cannot_refuel,
            'balance': money_format(self.balance),
            'balance_color': None,  # TODO
            'points': self.status['points'],
            'speed': self.speed,
            'current_max_speed': self.current_max_speed(),
            'direction': self.direction,
            'direction_lock': direction_lock,
            'can_move': not speed_lock
        }
        return output


class Vehicle:
    """
    ...TODO...
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
    ...TODO...
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

    """
    API to define:

    __init__(action_tuple=(id, message, type, amount, _))

    generate_message()
    action_id
    alter_status()
    """


class Hazard(Action):
    """
    ...
    """
    is_adjustment = False
    is_hazard = True

    def __init__(self, data):
        self.data = data

    """
    API to define:

    expiry_time
    generate_expiry_message()
    overridden_by()
    speed_limit
    type
    direction_lock  # bool
    speed_lock  # bool
    """
