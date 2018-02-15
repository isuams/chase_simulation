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
stuck_time      = 25    # how long after sim start that people can start getting stuck (in real-time minutes)
cc_time         = 10    # how long after sim start that people can start experiencing chaser convergence (in real-time minutes)
cc_chance       = .1    # chance of getting stuck in chaser convergence
tire_chance     = .001  # chance of popping a tire during the sim (same for all vehicle types)
dead_end_chance = .005  # chance of hitting a dead end during the sim (same for all vehicle types)
flood_chance    = .0025 # chance of hitting a flooded roadway during the sim (same for all vehicle types)

print ""

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
    dist         = d['dist']
    cc_top_spd   = d['cc_top_spd']
    dead_check   = d['dead_check']
    new_deg      = d['new_deg']
    old_direct   = d['old_direct']
    d.close()

    # Ensure that teams can't restart the program to skip sleep times.
    reset_time  = (time_now - time_step)
    reset_secs  = reset_time.total_seconds()

    print "Be careful not to close the window."
    print "Resuming where we left off..."
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
         
else:
    # Create team database file then ask for team name and create a separate
    # variable for use as a file name.
    Team_Name = raw_input("Enter a team name: ")
    C_Team_Name = Team_Name.replace(" ", "_")
    print ""
    print "You may choose from the following car types:"
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
        mpg          = 38.
        fuel_cap     = 13.
        stuck_chance = .01
    elif (Car_Type == "Sedan") or (Car_Type == "sedan"):
        #Pre-sets for sedan (4 door type car).
        car_number   = 2
        top_speed    = 150.
        mpg          = 35.
        fuel_cap     = 17.
        stuck_chance = .008
    elif (Car_Type == "Hybrid") or (Car_Type == "hybrid"):
        #Pre-sets for hybrid sedan (4 door type car).
        car_number   = 3
        top_speed    = 115.
        mpg          = 47.
        fuel_cap     = 16.
        stuck_chance = .008
    elif (Car_Type == "Pickup") or (Car_Type == "pickup"):
        #Pre-sets for pickup.
        car_number   = 4
        top_speed    = 130.
        mpg          = 18.
        fuel_cap     = 20.
        stuck_chance = .004
    elif (Car_Type == "SUV") or (Car_Type == "suv"):
        #Pre-sets for suv.
        car_number   = 5
        top_speed    = 125.
        mpg          = 24.
        fuel_cap     = 20.
        stuck_chance = .006
    else:
        car_number = 6

    while (car_number == 6):
        Car_Type = raw_input("Your entry is not a valid option, please re-enter your car type: ")

        # If statement to set vehicle specific variables or request new vehicle        
        if (Car_Type == "Compact") or (Car_Type == "compact"):
            #Pre-sets for compact car.
            car_number   = 1
            top_speed    = 125.
            mpg          = 38.
            fuel_cap     = 13.
            stuck_chance = .01
        elif (Car_Type == "Sedan") or (Car_Type == "sedan"):
            #Pre-sets for sedan (4 door type car).
            car_number   = 2
            top_speed    = 150.
            mpg          = 35.
            fuel_cap     = 17.
            stuck_chance = .008
        elif (Car_Type == "Hybrid") or (Car_Type == "hybrid"):
            #Pre-sets for hybrid sedan (4 door type car).
            car_number   = 3
            top_speed    = 115.
            mpg          = 47.
            fuel_cap     = 16.
            stuck_chance = .008
        elif (Car_Type == "Pickup") or (Car_Type == "pickup"):
            #Pre-sets for pickup.
            car_number   = 4
            top_speed    = 130.
            mpg          = 18.
            fuel_cap     = 20.
            stuck_chance = .004
        elif (Car_Type == "SUV") or (Car_Type == "suv"):
            #Pre-sets for suv.
            car_number   = 5
            top_speed    = 125.
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
    dist         = 0
    new_deg      = 0
    direct       = 0
    old_direct   = 0
    cc_top_spd   = 0
    init_time    = datetime.datetime.utcnow()

    #Starting fuel level for the team.
    fuel_level = fuel_cap - random.randint(2,(fuel_cap-1))
    
    # Create the team specific placefile using the entered team name.
    file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
    file1.write('RefreshSeconds: 10\n')
    file1.write('Threshold: 999\n')
    file1.write('Title: Location of Team %s\n' % (Team_Name,))
    file1.write('Font: 1, 11, 0, "Courier New"\n')
    file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
    file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
    file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
    file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
    file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
    file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
    file1.write('Object: %s,%s\n' % (lat, lon))
    file1.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                (Team_Name,init_time.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level,))
    file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
    file1.write('End:\n')
    file1.close()

    # Create the team specific placefile to save all times (for use in end chase recap).
    file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "w" )
    file2.write('RefreshSeconds: 10\n')
    file2.write('Threshold: 999\n')
    file2.write('Title: Location of Team %s\n' % (Team_Name,))
    file2.write('Font: 1, 11, 0, "Courier New"\n')
    file2.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
    file2.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
    file2.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
    file2.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
    file2.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
    file2.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
    file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (init_time.strftime("%Y-%m-%d"),init_time.strftime("%H:%M:%S"), \
                                              init_time.strftime("%Y-%m-%d"), \
                                              (init_time+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
    file2.write('Object: %s,%s\n' % (lat, lon))
    file2.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                (Team_Name,init_time.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level,))
    file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
    file2.write('End:\n')
    file2.close()

    # Create the team's specific data file and save their entered variables.
    d                 = shelve.open(fname)
    d['team']         = Team_Name
    d['c_team']       = C_Team_Name
    d['car']          = Car_Type
    d['top_speed']    = top_speed
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
    d['dist']         = dist
    d['new_deg']      = new_deg
    d['direct']       = direct
    d['old_direct']   = old_direct
    d['cc_top_spd']   = cc_top_spd
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
        print "You are back tracking to the %s." % (direct,)
    elif (dead_check == 2):
        direct = raw_input("Please input direction of travel (e.g. N, WSW, NE, W, etc) as shown in example: ")
        direct = direct.upper()
        while (direct == old_direct):
            print "You can't go that way because there's no way through."
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
    else:
        if (speed > top_speed):
            speed = top_speed
            dist  = (speed * slp_time * speedup) / 3600.
            print "Due to your vehicle's top speed, you can't go that far between scans."
            print "The farthest you can go at your top speed is %.1f miles." % (dist,)
            print ""

    d['speed']  = speed
    d['direct'] = direct
    d['dist']   = dist
    
    # Checking the speed of the team and letting them know if their speed is too high.
    print "Your speed is %s mph, moving to the %s." % (speed, direct)
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
            print "Direction entered incorrectly. You entered %s. A direction was randomly chosen for you." % (direct,)
            deg = random.randint(0,16) * 22.5
   
    print ""
        
    # Update placefile for new location. (This is a very crude way to calculate a new lat-lon, but works within
    # a few meters for anywhere in the plains.)
    rad_deg = math.radians(deg)
    lat = (lat + ((math.cos(rad_deg) * dist) * 0.016740))
    lon = (lon + ((math.sin(rad_deg) * dist) * 0.022180))
    d['lat']    = lat
    d['lon']    = lon
    
    int_deg = int(deg)
    time_step         = datetime.datetime.utcnow()
    d['time_step'] = time_step

    # Calculating real-time mpg from speed and calculating gas used.
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
    file1.write('RefreshSeconds: 10\n')
    file1.write('Threshold: 999\n')
    file1.write('Title: Location of Team %s\n' % (Team_Name,))
    file1.write('Font: 1, 11, 0, "Courier New"\n')
    file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
    file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
    file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
    file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
    file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
    file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
    file1.write('Object: %s,%s\n' % (lat, lon))
    if (speed != 0):
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
	file1.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
    else:
	file1.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level))
    file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
    file1.write('End:\n')
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
    file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
    file2.write('End:\n')
    file2.close()

    # Chance of getting pulled over.
    # 1 to 5 mph over the speed limit.
    if (spd_limit < speed <= (spd_limit + 5)):
        cop_chance = random.randint(0,200)
        d = shelve.open(fname)        
        if (cop_chance == 100):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)            
            cop_slp = 60
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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
        cop_chance = random.randint(0,100)
        d = shelve.open(fname)
        if (cop_chance == 50):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            print ""
            cop_slp = 65
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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
        cop_chance = random.randint(0,50)
        d = shelve.open(fname)
        if (cop_chance == 25):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = 70
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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
        cop_chance = random.randint(0,25)
        d = shelve.open(fname)
        if (cop_chance == 12):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = 80
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()

            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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
        cop_chance = random.randint(0,10)
        d = shelve.open(fname)
        if (cop_chance == 5):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = 100
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            d.close()
            
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
        cop_chance = random.randint(0,5)
        d = shelve.open(fname)
        if (cop_chance == 2):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = 120
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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
        cop_chance = random.randint(0,3)
        d = shelve.open(fname)
        if (cop_chance == 1):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = 140
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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
        cop_chance = random.randint(0,2)
        d = shelve.open(fname)
        if (cop_chance == 1):
            print "You have been pulled over for driving %s mph over the speed limit." % (spd_diff,)
            cop_slp = 160
            d['cop_slp'] = cop_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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

    # Setting up likelihood to get stuck in the mud.
    if (mins >= stuck_time) and (cc_turns == 0):
        d = shelve.open(fname)
        stuck = random.random()
        if stuck < stuck_chance:
            print ""
            print "You are stuck in the mud and are attempting to free your vehicle."
            stuck_slp = random.randint(15, 90)
            d['stuck_slp'] = stuck_slp
            d.close()

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nSTUCK IN THE MUD"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+stuck_slp))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nSTUCK IN THE MUD"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
            file2.close()
            d.close()
            
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
    if (mins >= cc_time) and (cc_turns == 0):
        d = shelve.open(fname)
        cc = random.random()
        if cc < cc_chance:
            print ""
            print "You are stuck in chaser convergence."
            cc_turns = random.randint(1, 8)
            d['cc_turns'] = cc_turns

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
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
        file1.write('RefreshSeconds: 10\n')
        file1.write('Threshold: 999\n')
        file1.write('Title: Location of Team %s\n' % (Team_Name,))
        file1.write('Font: 1, 11, 0, "Courier New"\n')
        file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
        file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
        file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
        file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
        file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
        file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file1.write('End:\n')
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file2.write('End:\n')
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
    tire = random.random()
    d = shelve.open(fname)
    if (tire < tire_chance):
        print ""
        print "Your vehicle has a flat tire that needs to be replaced."
        print ""
        tire_slp = random.randint(60, 120)
        d['tire_slp'] = tire_slp
        d.close()

        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write('RefreshSeconds: 10\n')
        file1.write('Threshold: 999\n')
        file1.write('Title: Location of Team %s\n' % (Team_Name,))
        file1.write('Font: 1, 11, 0, "Courier New"\n')
        file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
        file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
        file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
        file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
        file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
        file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nFLAT TIRE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file1.write('End:\n')
        file1.close()

        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                    time_step.strftime("%Y-%m-%d"), \
                                                    (time_step+datetime.timedelta(seconds=(slp_time+tire_slp))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nFLAT TIRE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file2.write('End:\n')
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
    dead_end = random.random()
    if (dead_end < dead_end_chance) and (dead_check == 0) and (cc_turns == 0):
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
        file1.write('RefreshSeconds: 10\n')
        file1.write('Threshold: 999\n')
        file1.write('Title: Location of Team %s\n' % (Team_Name,))
        file1.write('Font: 1, 11, 0, "Courier New"\n')
        file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
        file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
        file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
        file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
        file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
        file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A DEAD END"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file1.write('End:\n')
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A DEAD END"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file2.write('End:\n')
        file2.close()
        

    # Setting up the likelihood of a flooded road hazard
    dead_end = random.random()
    if (dead_end < flood_chance) and (dead_check == 0) and (mins >= stuck_time):
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
        file1.write('RefreshSeconds: 10\n')
        file1.write('Threshold: 999\n')
        file1.write('Title: Location of Team %s\n' % (Team_Name,))
        file1.write('Font: 1, 11, 0, "Courier New"\n')
        file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
        file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
        file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
        file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
        file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
        file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A FLOODED ROADWAY"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file1.write('End:\n')
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A FLOODED ROADWAY"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file2.write('End:\n')
        file2.close()


    # Checking if team wants to refuel.
    if (0.00 < fuel_level <= (fuel_cap * 0.15)):
        print "You have %.2f gallons of gas left." % (fuel_level,)
        refuel = raw_input("Would you like to refuel?: ")
        print ""
        if (refuel[:1] == "y") or (refuel[:1] == "Y"):
            d = shelve.open(fname)
            refuel_slp      = (fuel_cap - fuel_level) * 5
            fuel_level      = fuel_cap
            d['refuel_slp'] = refuel_slp
            d['fuel_level'] = fuel_level

            file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
            file1.write('RefreshSeconds: 10\n')
            file1.write('Threshold: 999\n')
            file1.write('Title: Location of Team %s\n' % (Team_Name,))
            file1.write('Font: 1, 11, 0, "Courier New"\n')
            file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
            file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
            file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
            file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
            file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
            file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
            file1.write('Object: %s,%s\n' % (lat, lon))
            file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file1.write('End:\n')
            file1.close()


            file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+refuel_slp))).strftime("%H:%M:%S")))            
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
            file2.write('End:\n')
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
        refuel_slp = fuel_cap * 5
        fuel_level = fuel_cap
        d['refuel_slp'] = refuel_slp
        d['fuel_level'] = fuel_level
        
        print "You are out of gas and are required to refuel."
        
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write('RefreshSeconds: 10\n')
        file1.write('Threshold: 999\n')
        file1.write('Title: Location of Team %s\n' % (Team_Name,))
        file1.write('Font: 1, 11, 0, "Courier New"\n')
        file1.write('IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"\n')
        file1.write('IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"\n')
        file1.write('IconFile: 3, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports.png"\n')
        file1.write('IconFile: 4, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_30.png"\n')
        file1.write('IconFile: 5, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/sn_reports_60.png"\n')
        file1.write('IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n')
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file1.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file1.write('End:\n')
        file1.close()


        file2 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+refuel_slp))).strftime("%H:%M:%S")))        
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write('\nText: 15, 10, 1, "%s"\n' % (Team_Name,))
        file2.write('End:\n')
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
    mins = secs / 60
    d['mins'] = mins
    d.close()
    time.sleep(slp_time)
    
os.remove(fname)
print "The simulation is now over and your team's placefile will now be removed."
os.remove("%s%s.php" % (teamfile_location ,C_Team_Name,))

time.sleep(60)
