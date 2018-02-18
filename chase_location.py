#!/usr/bin/python

__author__ = "Kristofer Tuftedal"

# Import needed modules.
import os
import time
import random
import math
import shelve
import datetime

# Specify constants that can shouldn't be reset prior to introduction if
# statements. Other constants are assigned later and may be changed.
home = os.path.expanduser('~')
fname = "%s/teamdat.db" % (home,)
teamfile_location = "/home/tuftedal/WWW/chase/loc/"

# For testing on my home computer.
#home_dir = home.replace('\\', '/')
#fname = "%s/Downloads/teamdat.db" % (home_dir,)
#teamfile_location = "%s/Desktop/" % (home_dir,)

sim_time        = 95    # in minutes
speedup         = 3.84  # how much faster the simulation is when compared to realtime (obtained when running radar script)
slp_time        = 60    # approximate time between radar scans (in real-time seconds)
spd_limit       = 65    # in mph.
fill_rate       = 15    # rate at which a fuel pump fills a gas tank (in seconds per gallon)
stuck_time      = 25    # how long after sim start that people can start getting stuck (in real-time minutes)
cc_time         = 10    # how long after sim start that people can start experiencing chaser convergence (in real-time minutes)
sunset_time     = 65    # how long after sim start that the sun sets in the simulation (in real-time minutes); this affects hazard chances
dr_chance       = .1    # chance of driving onto a dirt road
cc_chance       = .05   # chance of getting stuck in chaser convergence
tire_chance     = .001  # chance of popping a tire during the sim (same for all vehicle types)
dead_end_chance = .005  # chance of hitting a dead end during the sim (same for all vehicle types)
flood_chance    = .0025 # chance of hitting a flooded roadway during the sim (same for all vehicle types)

print "" # in the gui, any print statements should be converted to status messages
	 # (for example, text would go in the blank white box at the bottom of chase_main_screen.py)

# Check to see if the team already has a savefile with data.
if os.path.exists(fname) == True:
    # Open the team's unique data file, restore their data if program closed
    # accidentally, and calculate if there is any remaining sleep time.
    time_now     = datetime.datetime.utcnow()
    d            = shelve.open(fname)
    Team_Name    = d['team']
    C_Team_Name  = d['c_team']
    Car_Type     = d['car']
    top_speed    = d['top_speed']
    mpg          = d['mpg']
    fuel_cap     = d['fuel_cap']
    stuck_chance = d['stuck_chance']
    lat          = d['lat']
    lon          = d['lon']
    speed        = d['speed']
    mins         = d['mins']
    refuel_slp   = d['refuel_slp']
    cop_slp      = d['cop_slp']
    stuck_slp    = d['stuck_slp']
    tire_slp     = d['tire_slp']
    cc_turns     = d['cc_turns']
    init_time    = d['init_time']
    fuel_level   = d['fuel_level']
    time_step    = d['time_step']
    direct       = d['direct']
    dr_direct    = d['dr_direct']
    dist         = d['dist']
    cc_top_spd   = d['cc_top_spd']
    dr_top_spd   = d['dr_top_spd']
    aft_dark_inc = d['aft_dark_inc']
    sun_check    = d['sun_check']
    dead_check   = d['dead_check']
    dr_check     = d['dr_check']
    new_deg      = d['new_deg']
    old_direct   = d['old_direct']
    d.close()

    # Recreate the file header and footer texts for use in placefiles.
    file_headertext = 'RefreshSeconds: 10\
                       \nThreshold: 999\
                       \nTitle: Location of Team %s\
                       \nFont: 1, 11, 0, "Courier New"\
                       \nIconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\
                       \nIconFile: 2, 15, 25,  8, 25, "http://www.spotternetwork.org/icon/arrows.png"\
                       \nIconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\
                       \nIconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\
                       \nIconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\
                       \nIconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n' % (Team_Name,)
    file_footertext = '\nText: 15, 10, 1, "%s"\nEnd:\n' % (Team_Name,)

    # Ensure that teams can't restart the program to skip sleep times.
    reset_time  = (time_now - time_step)
    reset_secs  = reset_time.total_seconds()

    print "Be careful not to close the window."
    print "Resuming where your team left off..."
    print ""
    
    # General reset sleep time.
    if (reset_secs < slp_time):
        reset_slp = slp_time - reset_secs
        time.sleep(reset_slp)

    # Refuel reset sleep time.   
    while (refuel_slp != 0):
        if (reset_secs < refuel_slp + slp_time):
            print "Refueling..."
            reset_slp = refuel_slp + slp_time - reset_secs
            time.sleep(reset_slp)
            print "Refueling complete."
            print ""
            refuel_slp = 0
        else:
            refuel_slp = 0
        
    # Speeding reset sleep time.
    while (cop_slp != 0):
        if (reset_secs < cop_slp + slp_time):
            print "Pulled over for speeding..."
            reset_slp = cop_slp + slp_time - reset_secs
            time.sleep(reset_slp)
            print "You're now free to go."
            print ""
            cop_slp = 0
        else:
            cop_slp = 0

    # Stuck in mud reset time.   
    while (stuck_slp != 0):
        if (reset_secs < stuck_slp + slp_time):
            print "Stuck in the mud..."
            reset_slp = stuck_slp + slp_time - reset_secs
            time.sleep(reset_slp)
            print "Your vehicle has been freed from the mud."
            print ""
            stuck_slp = 0
        else:
            stuck_slp = 0

    # Flat tire reset time.    
    while (tire_slp != 0):
        if (reset_secs < tire_slp + slp_time):
            print "Replacing flat tire..."
            reset_slp = tire_slp + slp_time - reset_secs
            time.sleep(reset_slp)
            print "Your team has replaced the flat tire and is moving again."
            print ""
            tire_slp = 0
        else:
            tire_slp = 0

    # Calculate time passed.
    d = shelve.open(fname)
    delta_t = (time_step - init_time)
    secs = delta_t.total_seconds()
    mins = secs / 60.
    d['mins'] = mins
    d.close()

# If no savefile is present, start a new savefile for the team (used at the beginning of
# the simulation for team name, vehicle, and location selection.)
else:
    # Create team database file then ask for team name and create a separate
    # variable for use as a file name.
    Team_Name = raw_input("Enter a team name: ")
    if (Team_Name.title() == "Cow") or (Team_Name.title() == "Cows"):
        print ""
        print "I gotta go Julia, we got cows!"
    elif (Team_Name.title() == "Bill Paxton") or (Team_Name.title() == "Bill Harding"):
        print ""
        print 'Why do you call Billy "The Extreme?"'
        print 'Because Billy *is* "The Extreme."'
        Team_Name = "The Extreme"
    elif (Team_Name.title() == "Helen Hunt") or (Team_Name.title() == "Jo Harding"):
        print ""
        print "Hang on a second, boss lady, hold your horses."
        Team_Name = "Boss Lady"
    elif (Team_Name.title() == "Philip Seymour Hoffman") or (Team_Name.title() == "Dusty"):
        print ""
        print "It's the wonder of nature, baby!"
        Team_Name = "Dusty"
    elif (Team_Name.title() == "Rabbit"):
        print ""
        print "Uh... yeah, trust me. Rabbit is good, Rabbit is wise."
    elif (Team_Name.upper() == "F5") or (Team_Name.title() == "EF5"):
        print ""
        print "Is there an F5? What would that be like?"
        Team_Name = "The Finger of God"
    elif (Team_Name.title() == "The Suck Zone") or (Team_Name.title() == "Suck Zone"):
        print ""
        print "... and it NEVER hits the ground!"
        Team_Name = "The Suck Zone"
    elif (Team_Name.title() == "Columbus"):
        print ""
        print "Susan, get my pants!"
    
    C_Team_Name = Team_Name.replace(" ", "_")

    if (Team_Name == "The Extreme") or (Team_Name == "Boss Lady"):
        Car_Type = "Pickup"
        print ""
        print "Your team gets a pickup truck by default."
    else:
        print ""
        print "Your team may choose from the following car types:"
        print "Compact"
        print "Sedan"
        print "Hybrid"
        print "Pickup"
        print "SUV"
        print ""
        Car_Type  = raw_input("Enter your team's car type of choice (as specified above): ")
    
    # If statement to set vehicle specific variables or request new vehicle
    # (Consider making these in to def() for easier modification and calling.)
    if (Car_Type == "Compact") or (Car_Type == "compact"):
        #Pre-sets for compact car.
        car_number   = 1
        top_speed    = 135.
        dr_top_spd   = 45.
        mpg          = 38.
        fuel_cap     = 13.
        stuck_chance = .01
    elif (Car_Type == "Sedan") or (Car_Type ==  "sedan"):
        #Pre-sets for sedan (4 door type car).
        car_number   = 2
        top_speed    = 150.
        dr_top_spd   = 55.
        mpg          = 35.
        fuel_cap     = 17.
        stuck_chance = .008
    elif (Car_Type == "Hybrid") or (Car_Type ==  "hybrid"):
        #Pre-sets for hybrid sedan (4 door type car).
        car_number   = 3
        top_speed    = 115.
        dr_top_spd   = 55.
        mpg          = 47.
        fuel_cap     = 16.
        stuck_chance = .008
    elif (Car_Type == "Pickup") or (Car_Type ==  "pickup"):
        #Pre-sets for pickup.
        car_number   = 4
        top_speed    = 130.
        dr_top_spd   = 70.
        mpg          = 18.
        fuel_cap     = 20.
        stuck_chance = .004
    elif (Car_Type == "SUV") or (Car_Type ==  "suv"):
        #Pre-sets for suv.
        car_number   = 5
        top_speed    = 125.
        dr_top_spd   = 65.
        mpg          = 24.
        fuel_cap     = 20.
        stuck_chance = .006
    else:
        car_number = 6 # If a GUI is created with a dropdown list, this part of the if statement
                       # and the following while statement can be removed.

    while (car_number == 6):
        Car_Type = raw_input("Your entry is not a valid option, please re-enter your car type: ")

        # If statement to set vehicle specific variables or request new vehicle        
        if (Car_Type == "Compact") or (Car_Type ==  "compact"):
            #Pre-sets for compact car.
            car_number   = 1
            top_speed    = 135.
            dr_top_spd   = 45.
            mpg          = 38.
            fuel_cap     = 13.
            stuck_chance = .01
        elif (Car_Type == "Sedan") or (Car_Type ==  "sedan"):
            #Pre-sets for sedan (4 door type car).
            car_number   = 2
            top_speed    = 150.
            dr_top_spd   = 55.
            mpg          = 35.
            fuel_cap     = 17.
            stuck_chance = .008
        elif (Car_Type == "Hybrid") or (Car_Type ==  "hybrid"):
            #Pre-sets for hybrid sedan (4 door type car).
            car_number   = 3
            top_speed    = 115.
            dr_top_spd   = 55.
            mpg          = 47.
            fuel_cap     = 16.
            stuck_chance = .008
        elif (Car_Type == "Pickup") or (Car_Type ==  "pickup"):
            #Pre-sets for pickup.
            car_number   = 4
            top_speed    = 130.
            dr_top_spd   = 70.
            mpg          = 18.
            fuel_cap     = 20.
            stuck_chance = .004
        elif (Car_Type == "SUV") or (Car_Type ==  "suv"):
            #Pre-sets for suv.
            car_number   = 5
            top_speed    = 125.
            dr_top_spd   = 65.
            mpg          = 24.
            fuel_cap     = 20.
            stuck_chance = .006
        else:
            car_number = 6

    # Ask team to enter their starting coordinates and check for non-sense entries.
    print ""
    print "Enter latitude (the 1st number) of your target city from GR."
    print "(make sure it's exactly the same)"
    lat = raw_input("Latitude: ")
    while isinstance(lat, basestring):
        try:
            lat = float(lat)
        except ValueError:
            lat = raw_input("Incorrect latitude entered, please re-enter latitude: ")
    print ""
    print "Enter longitude (the 2nd number) of your target city from GR."
    print "(make sure it's exactly the same and include the negative)"
    lon = raw_input("Longitude: ")
    while isinstance(lon, basestring):
        try:
            lon = float(lon)
        except ValueError:
            lon = raw_input("Incorrect longitude entered, please re-enter longitude: ")

    # Initialize variables which are modified as the program runs
    speed        = 0
    mins         = 0
    refuel_slp   = 0
    cop_slp      = 0
    stuck_slp    = 0
    tire_slp     = 0
    cc_turns     = 0
    dead_check   = 0
    dr_check     = 0
    dist         = 0
    new_deg      = 0
    direct       = 0
    old_direct   = 0
    dr_direct    = 0
    cc_top_spd   = 0
    aft_dark_inc = 0
    sun_check    = 0
    init_time    = datetime.datetime.utcnow()

    # Starting fuel level for the team. Randomized to simulate how much fuel you might have when
    # convection initiates and the chase begins
    fuel_level = fuel_cap - random.randint(1,(fuel_cap-2))
    
    # Create the team specific placefile using the entered team name.
    file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
    file_headertext = 'RefreshSeconds: 10\
                       \nThreshold: 999\
                       \nTitle: Location of Team %s\
                       \nFont: 1, 11, 0, "Courier New"\
                       \nIconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\
                       \nIconFile: 2, 15, 25,  8, 25, "http://www.spotternetwork.org/icon/arrows.png"\
                       \nIconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\
                       \nIconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\
                       \nIconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\
                       \nIconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n' % (Team_Name,)
    file_footertext = '\nText: 15, 10, 1, "%s"\nEnd:\n' % (Team_Name,)
    file1.write(file_headertext)
    file1.write('Object: %s,%s\n' % (lat, lon))
    file1.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                (Team_Name,init_time.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level,))
    file1.write(file_footertext)
    file1.close()

    # Create the team specific placefile to save all times (for use in end chase recap).
    file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "w" )
    file2.write(file_headertext)
    file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (init_time.strftime("%Y-%m-%d"),init_time.strftime("%H:%M:%S"), \
                                              init_time.strftime("%Y-%m-%d"), \
                                              (init_time+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
    file2.write('Object: %s,%s\n' % (lat, lon))
    file2.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                (Team_Name,init_time.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level,))
    file2.write(file_footertext)
    file2.close()

    # Create the team's specific data file and save their entered variables.
    d                 = shelve.open(fname)
    d['team']         = Team_Name
    d['c_team']       = C_Team_Name
    d['car']          = Car_Type
    d['top_speed']    = top_speed
    d['dr_top_spd']   = dr_top_spd
    d['mpg']          = mpg
    d['fuel_cap']     = fuel_cap
    d['stuck_chance'] = stuck_chance
    d['lat']          = lat
    d['lon']          = lon
    d['speed']        = speed
    d['mins']         = mins
    d['refuel_slp']   = refuel_slp
    d['cop_slp']      = cop_slp
    d['stuck_slp']    = stuck_slp
    d['tire_slp']     = tire_slp
    d['cc_turns']     = cc_turns
    d['dead_check']   = dead_check
    d['dr_check']     = dr_check
    d['dist']         = dist
    d['new_deg']      = new_deg
    d['direct']       = direct
    d['old_direct']   = old_direct
    d['dr_direct']    = dr_direct
    d['cc_top_spd']   = cc_top_spd
    d['aft_dark_inc'] = aft_dark_inc
    d['sun_check']    = sun_check
    d['init_time']    = init_time
    d['fuel_level']   = fuel_level
 

    # Print the file name to add to placefile. MODIFY THE NET-ID TO WHOEVER IS RUNNING THE RADAR CODE
    print ""
    print ""
    print "Please type the following into your placefile window in GR.:"
    print ""
    print "http://www.meteor.iastate.edu/~tuftedal/chase/loc/%s.php" % (C_Team_Name,)
    print ""
    print ""

    # Save current time, close the save file, and put the program to sleep until the next movement.
    time_step = datetime.datetime.utcnow()
    d['time_step'] = time_step
    d.close()
    time.sleep(slp_time)

# A "while" loop that controls team movement during the simulation.
while (mins <= sim_time):
    d = shelve.open(fname)

    # Calculate mins at the beginning of the loop.
    time_step      = datetime.datetime.utcnow()
    delta_t = (time_step - init_time)
    secs = delta_t.total_seconds()
    mins = secs / 60.
    d['time_step'] = time_step
    d['mins'] = mins

    if (mins >= sunset_time) and (sun_check == 0):
        print "The sun has now set. Your team can continue chasing, but be especially careful..."
        print ""
        aft_dark_inc = .05
        sun_check = 1
        d['aft_dark_inc'] = aft_dark_inc
        d['sun_check'] = sun_check      
        
    # Ask for team's direction and distance of travel.
    if (dead_check == 0):
        direct = raw_input("Please input direction of travel (e.g. N, WSW, NE, W, etc) as shown in example: ")
        direct = direct.upper()
    elif (dead_check == 1):
        deg = new_deg
        if (deg == 0.0):
            direct = "N"               
        elif (deg == 22.5):
            direct = "NNE"
        elif (deg == 45.0):
            direct = "NE"
        elif (deg == 67.5):
            direct = "ENE"
        elif (deg == 90.0):
            direct = "E"
        elif (deg == 112.5):
            direct = "ESE"
        elif (deg == 135.0):
            direct = "SE"
        elif (deg == 157.5):
            direct = "SSE"
        elif (deg == 180.0):
            direct = "S"
        elif (deg == 202.5):
            direct = "SSW"
        elif (deg == 225.0):
            direct = "SW"
        elif (deg == 247.5):
            direct = "WSW"
        elif (deg == 270.0):
            direct = "W"
        elif (deg == 292.5):
            direct = "WNW"
        elif (deg == 315.0):
            direct = "NW"
        elif (deg == 337.5):
            direct = "NNW"
        dead_check = 2
        print ""
        print "Your team is back tracking to the %s." % (direct,)
    elif (dead_check == 2):
        direct = raw_input("Please input direction of travel (e.g. N, WSW, NE, W, etc) as shown in example: ")
        direct = direct.upper()
        while (direct == old_direct):
            print "Your team can't go that way because there's no way through."
            print ""
            direct = raw_input("Please input direction of travel (e.g. N, WSW, NE, W, etc) as shown in example: ")
            direct = direct.upper()
        dead_check = 0
    d['dead_check'] = dead_check  
    dist = raw_input("Please input distance of travel (in miles, eg. 1, 3.5, etc): ")

    # Ensure that the team put in a numerical distance that is non-negative
    while isinstance(dist, basestring):
        try:
            dist = float(dist)
            dist = abs(dist)
        except ValueError:
            dist = raw_input("Incorrect distance. Please re-enter distance: ")
            
    print ""

    # Determine direction of travel in degrees.
    if (dead_check != 2):
        if (direct == "N"):
            deg = 0.0
        elif (direct == "NNE"):
            deg = 22.5
        elif (direct == "NE"):
            deg = 45.0
        elif (direct == "ENE"):
            deg = 67.5
        elif (direct == "E"):
            deg = 90.0
        elif (direct == "ESE"):
            deg = 112.5
        elif (direct == "SE"):
            deg = 135.0
        elif (direct == "SSE"):
            deg = 157.5
        elif (direct == "S"):
            deg = 180.0
        elif (direct == "SSW"):
            deg = 202.5
        elif (direct == "SW"):
            deg = 225.0
        elif (direct == "WSW"):
            deg = 247.5
        elif (direct == "W"):
            deg = 270.0
        elif (direct == "WNW"):
            deg = 292.5
        elif (direct == "NW"):
            deg = 315.0
        elif (direct == "NNW"):
            deg = 337.5
        else:
            wrong_direct = direct
            
            deg = random.randint(0,15) * 22.5

            if (deg == 0.0):
                direct = "N"               
            elif (deg == 22.5):
                direct = "NNE"
            elif (deg == 45.0):
                direct = "NE"
            elif (deg == 67.5):
                direct = "ENE"
            elif (deg == 90.0):
                direct = "E"
            elif (deg == 112.5):
                direct = "ESE"
            elif (deg == 135.0):
                direct = "SE"
            elif (deg == 157.5):
                direct = "SSE"
            elif (deg == 180.0):
                direct = "S"
            elif (deg == 202.5):
                direct = "SSW"
            elif (deg == 225.0):
                direct = "SW"
            elif (deg == 247.5):
                direct = "WSW"
            elif (deg == 270.0):
                direct = "W"
            elif (deg == 292.5):
                direct = "WNW"
            elif (deg == 315.0):
                direct = "NW"
            elif (deg == 337.5):
                direct = "NNW"
            print "You're arguing with your driver. You wanted to go %s, but your driver went %s instead." % (wrong_direct, direct)

    # Calculating the speed using distance traveled and actual time between radar scans (in hours)"
    # For example, if 90 seconds elapse between radar scans, that would be 0.025 hours.
    speed = (3600. * dist) / (slp_time * speedup)
    speed = int(speed)
    
    if (cc_turns !=0) and (speed > cc_top_spd):
        speed = cc_top_spd
        dist  = (speed * slp_time * speedup) / 3600.
        print "Due to chaser convergence, you can't go that far between scans."
        print "The farthest you can go at your current top speed is %.1f miles." % (dist,)
        print ""
            
    if (dr_check == 1) and (speed > dr_top_spd) and (direct == dr_direct):
        speed = dr_top_spd
        dist  = (speed * slp_time * speedup) / 3600.
        print "You can't go that fast on a dirt road."
        print "The farthest you can go at your current top speed is %.2f miles." % (dist,)
        print "Your team continues on the dirt road."
        print ""

    elif (dr_check == 1) and (speed <= dr_top_spd) and (direct == dr_direct):
        print "Your team continues on the dirt road."
        print ""
        
    elif (dr_check == 1) and (direct != dr_direct):
        print "You've turned off of the dirt road and can reach your top speed again."
        print ""
        dr_check = 2
        if (speed > top_speed):
            speed = top_speed
            dist  = (speed * slp_time * speedup) / 3600.
            print "Due to your vehicle's top speed, you can't go that far between scans."
            print "The farthest you can go at your top speed is %.1f miles." % (dist,)
            print ""
    else:
        if (speed > top_speed):
            speed = top_speed
            dist  = (speed * slp_time * speedup) / 3600.
            print "Due to your vehicle's top speed, you can't go that far between scans."
            print "The farthest you can go at your top speed is %.1f miles." % (dist,)
            print ""

    d['speed']    = speed
    d['direct']   = direct
    d['dist']     = dist
    d['dr_check'] = dr_check
    
    # Checking the speed of the team and letting them know if their speed is too high.
    print "Your speed is %s mph, moving to the %s." % (int(speed), direct)
    spd_diff = speed - spd_limit
    spd_diff = int(spd_diff)
    if (speed < 65):
        print "You're %s mph under the speed limit." % (abs(spd_diff),)
    elif (65 < speed <= 75):
        print "You're %s mph over the speed limit." % (spd_diff,)
    elif (75 < speed <= 85):
        print "You're %s mph over the speed limit." % (spd_diff,)
    elif (85 < speed <= 95):
        print "You're %s mph over the speed limit." % (spd_diff,)
    else:
        print "You're %s mph over the speed limit." % (spd_diff,)        
 
    print ""
        
    # Update placefile for new location. (This is a very crude way to calculate a new lat-lon, but works within
    # a few meters for anywhere in the plains.)
    rad_deg        = math.radians(deg)
    lat            = (lat + ((math.cos(rad_deg) * dist) * 0.016740))
    lon            = (lon + ((math.sin(rad_deg) * dist) * 0.022180))
    d['lat']       = lat
    d['lon']       = lon
    int_deg        = int(deg)
    time_step      = datetime.datetime.utcnow()
    d['time_step'] = time_step

    # Calculating real-time mpg from speed and calculating gas used since estimated fuel economy and actual
    # fuel economy can vary greatly depending on speed.
    if (speed == 0):
        real_mpg = mpg
    elif (speed <= 5):
        real_mpg = mpg / 4.30
    elif (speed <= 10):
        real_mpg = mpg / 3.50
    elif (speed <= 15):
        real_mpg = mpg / 2.20
    elif (speed <= 20):
        real_mpg = mpg / 1.75
    elif (speed <= 25):
        real_mpg = mpg / 1.51
    elif (speed <= 30):
        real_mpg = mpg / 1.32
    elif (speed <= 35):
        real_mpg = mpg / 1.23
    elif (speed <= 40):
        real_mpg = mpg / 1.17
    elif (speed <= 45):
        real_mpg = mpg / 1.08
    elif (speed <= 50):
        real_mpg = mpg / 1.03    
    elif (speed == 55):
        real_mpg = mpg
    elif (speed <= 60):
        real_mpg = mpg / 1.03    
    elif (speed <= 65):
        real_mpg = mpg / 1.08
    elif (speed <= 70):
        real_mpg = mpg / 1.17
    elif (speed <= 75):
        real_mpg = mpg / 1.23
    elif (speed <= 80):
        real_mpg = mpg / 1.28
    elif (speed <= 85):
        real_mpg = mpg / 1.32
    elif (speed <= 90):
        real_mpg = mpg / 1.36
    elif (speed <= 95):
        real_mpg = mpg / 1.43
    elif (speed <= 100):
        real_mpg = mpg / 1.51
    elif (speed <= 105):
        real_mpg = mpg / 1.57
    elif (speed <= 110):
        real_mpg = mpg / 1.68
    elif (speed <= 115):
        real_mpg = mpg / 1.75
    elif (speed <= 120):
        real_mpg = mpg / 1.90
    elif (speed <= 125):
        real_mpg = mpg / 2.20
    elif (speed <= 130):
        real_mpg = mpg / 3.00
    elif (speed <= 135):
        real_mpg = mpg / 4.50
    elif (speed <= 150):
        real_mpg = mpg / 10
    fuel_level = fuel_level - (dist / real_mpg)
    d['fuel_level'] = fuel_level 
    d.close()

    # Update team placefile.
    file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
    file1.write(file_headertext)
    file1.write('Object: %s,%s\n' % (lat, lon))
    if (speed != 0):
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
	file1.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
    else:
	file1.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level))
    file1.write(file_footertext)
    file1.close()

    # Update all times placefile.
    file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
    file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                              time_step.strftime("%Y-%m-%d"), \
                                              (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
    file2.write('Object: %s,%s\n' % (lat, lon))
    if (speed != 0):
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
	file2.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
    else:
	file2.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level))
    file2.write(file_footertext)
    file2.close()

    # Chance of getting pulled over.
    # 1 to 5 mph over the speed limit.
    if (spd_limit < speed <= (spd_limit + 5)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)        
        if (cop_chance <= (0.005 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)            
            cop_slp = slp_time
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            
    # 6 to 10 mph over the speed limit.
    if ((spd_limit + 5) < speed <= (spd_limit + 10)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)
        if (cop_chance <= (0.01 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            print ""
            cop_slp = slp_time * math.exp(0.1)
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()

    # 11 to 15 mph over the speed limit.    
    if ((spd_limit + 10) < speed <= (spd_limit + 15)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)
        if (cop_chance <= (0.02 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = slp_time * math.exp(0.2)
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()

    # 16 to 20 mph over the speed limit
    if ((spd_limit + 15) < speed <= (spd_limit + 20)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)
        if (cop_chance <= (0.04 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = slp_time * math.exp(0.3)
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()

            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()

    # 21 to 25 mph over the speed limit.
    if ((spd_limit + 20) < speed <= (spd_limit + 25)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)
        if (cop_chance <= (0.08 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = slp_time * math.exp(0.5)
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()

    # 26 to 30 mph over the speed limit.
    if ((spd_limit + 25) < speed <= (spd_limit + 30)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)
        if (cop_chance <= (0.16 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = slp_time * math.exp(0.7)
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()

    # 31 to 50 mph over the speed limit.
    if ((spd_limit + 30) < speed <= (spd_limit + 50)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)
        if (cop_chance <= (0.32 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = slp_time * math.exp(0.9)
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()

    # 50+ mph over the speed limit.
    if (speed > (spd_limit + 50)):
        cop_chance = random.uniform(0.0001,1.0)
        d = shelve.open(fname)
        if (cop_chance <= (0.64 + aft_dark_inc)):
            print "Your team has been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = slp_time * math.exp(1)
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(cop_slp)
            d = shelve.open(fname)
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()
            print "You're now free to go."
            print ""
        else:
            cop_slp = 0
            d['cop_slp'] = cop_slp
            d.close()

    # Setting up likelihood of being on a dirt road.
    dirt_road = random.uniform(0.0001,1.0)
    if (cc_turns == 0) and (dirt_road <= dr_chance) and (dr_check == 0):
        print "You've driven onto a dirt road."
        print "Your top speed will be decreased to %s mph until you change roads." % (int(dr_top_spd),)
        print ""
        
        d = shelve.open(fname)
        dr_check = 1
        dr_direct = direct
        d['dr_check'] = dr_check
        d['dr_direct'] = dr_direct
        d.close()
        
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()
    elif (dr_check == 1):
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()
    elif (dr_check == 2):
        d = shelve.open(fname)
        dr_check = 0
        d['dr_check'] = dr_check
        d.close()        

    # Setting up likelihood to get stuck in the mud.
    if (mins >= stuck_time) and (dr_check == 1):
        d = shelve.open(fname)
        stuck = random.uniform(0.0001,1.0)
        if (stuck < (stuck_chance + aft_dark_inc)):
            print ""
            print "Your team is stuck in the mud and is attempting to free your vehicle."
            stuck_slp = random.randint(slp_time/4, slp_time*1.5)
            d['stuck_slp'] = stuck_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD\nSTUCK IN THE MUD"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+stuck_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD\nSTUCK IN THE MUD"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
            
            time.sleep(stuck_slp)
            d = shelve.open(fname)
            stuck_slp = 0
            d['stuck_slp'] = stuck_slp
            d.close()            
            print "Your vehicle has been freed from the mud."
            print ""
        else:
            stuck_slp = 0
            d['stuck_slp'] = stuck_slp
            d.close()


    # Setting up likelihood to get stuck in chaser convergence.
    if (mins >= cc_time) and (cc_turns == 0) and (dr_check == 0):
        d = shelve.open(fname)
        cc = random.uniform(0.0001,1.0)
        if (cc < (cc_chance - aft_dark_inc)):
            print ""
            print "Your team is stuck in chaser convergence."
            cc_turns = random.randint(1, 8)
            d['cc_turns'] = cc_turns

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()

            cc_top_spd = random.randint(15,45)   # speed limit if a team gets stuck in chaser convergence.
            d['cc_top_spd'] = cc_top_spd
            d.close()
            
            print "Your top speed has been reduced to %s mph." % (cc_top_spd)
            print ""
        else:
            cc_turns = 0
            d['cc_turns'] = cc_turns
            d.close()
    elif (mins >= cc_time) and (cc_turns != 0):
        d = shelve.open(fname)
        cc_new_spd = random.randint(15,45)   # speed limit if a team gets stuck in chaser convergence.
        cc_turns -= 1
        d['cc_turns'] = cc_turns
        d['cc_top_spd'] = cc_top_spd

        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()

        if (cc_turns == 0):           
            print "You are now out of chaser convergence."
            print "Your top speed is now the vehicle's top speed."
            print ""
            
        else:
            if (cc_new_spd < cc_top_spd):                
                print "Chaser convergence is getting worse."
                print "Your top speed has been reduced to %s mph." % (cc_new_spd)
                print ""

                cc_top_spd = cc_new_spd
                d['cc_top_spd'] = cc_top_spd
    
            elif (cc_new_spd > cc_top_spd):                
                print "Chaser convergence is improving."
                print "Your top speed has increased to %s mph." % (cc_new_spd)
                print ""
                cc_top_spd = cc_new_spd
                d['cc_top_spd'] = cc_top_spd

            else:                
                print "Chaser convergence remains the same."
                print "Your top speed remains at %s mph." % (cc_new_spd)
                print ""
                cc_top_spd = cc_new_spd
                d['cc_top_spd'] = cc_top_spd
        d.close()


    # Setting up likelihood of getting a flat tire.
    tire = random.uniform(0.0001,1.0)
    d = shelve.open(fname)
    if (tire < tire_chance):
        print ""
        print "Your vehicle has a flat tire that needs to be replaced."
        print ""
        tire_slp = random.randint(slp_time, slp_time*2)
        d['tire_slp'] = tire_slp
        d.close()

        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nFLAT TIRE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()

        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                    time_step.strftime("%Y-%m-%d"), \
                                                    (time_step+datetime.timedelta(seconds=(slp_time+tire_slp))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nFLAT TIRE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()
        d.close()

        time.sleep(tire_slp)
        d = shelve.open(fname)
        tire_slp = 0
        d['tire_slp'] = tire_slp
        d.close()
        print "Your team has replaced the flat tire and is moving again."
        print ""
    else:
        tire_slp = 0
        d['tire_slp'] = tire_slp
        d.close()

    # Setting up the likelihood of a dead end hazard
    dead_end = random.uniform(0.0001,1.0)
    if (dead_end < (dead_end_chance + aft_dark_inc)) and (dead_check == 0) and (cc_turns == 0):
        dead_check = 1
        new_deg = deg + 180
        old_direct = direct
        if (new_deg >= 360):
            new_deg -= 360
        d = shelve.open(fname)
        d['dead_check'] = dead_check
        d['new_deg'] = new_deg
        d['old_direct'] = old_direct
        d.close()     
        print ""
        print "Your team has hit a dead end and must go back in the opposite direction."
        print "Your direction will be set in the opposite direction on your next turn."
        print ""

        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A DEAD END"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A DEAD END"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()
        

    # Setting up the likelihood of a flooded road hazard
    dead_end = random.uniform(0.0001,1.0)
    if (dead_end < (flood_chance + aft_dark_inc)) and (dead_check == 0) and (mins >= stuck_time):
        d = shelve.open(fname)
        dead_check = 1
        new_deg = deg + 180
        old_direct = direct
        if (new_deg >= 360):
            new_deg -= 360
        d = shelve.open(fname)
        d['dead_check'] = dead_check
        d['new_deg'] = new_deg
        d['old_direct'] = old_direct
        d.close()
        print ""
        print "Your team has hit a flooded roadway and must go back in the opposite direction."
        print "Your direction will be set in the opposite direction on your next turn."
        print ""

        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A FLOODED ROADWAY"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A FLOODED ROADWAY"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


    # Checking if team wants to refuel.
    if (0.00 < fuel_level <= (fuel_cap * 0.15)):
        print "You have %.2f gallons of gas left." % (fuel_level,)
        refuel = raw_input("Would your team like to refuel?: ")
        print ""
        if (refuel[:1] == "y") or (refuel[:1] == "Y"):
            d = shelve.open(fname)
            refuel_slp      = ((fuel_cap - fuel_level) * fill_rate)/speedup
            fuel_level      = fuel_cap
            d['refuel_slp'] = refuel_slp
            d['fuel_level'] = fuel_level

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write(file_headertext)
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file1.write(file_footertext)
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+refuel_slp))).strftime("%H:%M:%S")))            
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()
    
            print "Refueling now."
            print ""    
            d.close()

            time.sleep(refuel_slp)
            d = shelve.open(fname)
            refuel_slp = 0
            d['refuel_slp'] = refuel_slp
            d.close()          
            print "Refueling complete."
            print ""
        else:
            d = shelve.open(fname)
            refuel_slp = 0
            d['refuel_slp'] = refuel_slp
            d.close()

    # Forcing team to refill when they run out of gas.
    if (fuel_level <= 0):
        d = shelve.open(fname)       
        refuel_slp = ((fuel_cap - fuel_level) * fill_rate)/speedup + slp_time # slp_time amount added to the refill time to account for having to push the car.
        fuel_level = fuel_cap
        d['refuel_slp'] = refuel_slp
        d['fuel_level'] = fuel_level
        
        print "Your team is out of gas and are required to refuel."
        
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+refuel_slp))).strftime("%H:%M:%S")))        
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()

        print "Refueling now."
        print ""
        d.close()
        
        time.sleep(refuel_slp)
        d = shelve.open(fname)
        refuel_slp = 0
        d['refuel_slp'] = refuel_slp
        d.close()
        print "Refueling complete."
        print ""
    else:
        d = shelve.open(fname)
        refuel_slp = 0
        d['refuel_slp'] = refuel_slp
        d.close()

    # Suspend the while statement for a specified amount of time.
    d = shelve.open(fname)
    delta_t = (time_step - init_time)
    secs = delta_t.total_seconds()
    mins = secs / 60.
    d['mins'] = mins
    d.close()
    time.sleep(slp_time)
    
os.remove(fname)
print "The simulation is now over and your team's placefile will now be removed."
os.remove("%s%s.php" % (teamfile_location ,C_Team_Name,))

time.sleep(60)
