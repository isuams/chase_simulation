#!/usr/bin/env python

"""
Helper Functions for Chase Applet

These are the functions to make the chase applet work.
"""

import numpy as np


def lat_lon_diff(distance_miles, angle_degrees):
    """Calculate difference in lat/lon crudely (but good enough for the plains)."""
    angle = np.deg2rad(angle_degrees)
    diff_lat = ((np.cos(angle) * distance_miles) * 0.016740)
    diff_lon = ((np.sin(angle) * distance_miles) * 0.022180)
    return diff_lat, diff_lon


def money_format(money):
    # TODO: Make a nice money string from a float
    return money


def shuffle_new_hazard(team, seconds, hazards):
    """Given a time interval, use registered hazards to shuffle a chance of a new hazard."""
    # TODO Something
    return None