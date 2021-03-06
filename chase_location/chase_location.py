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
netid = "jthielen"
#fname = "%s/teamdat.db" % (home,)
#teamfile_location = "/home/%s/WWW/chase/loc/" % (netid)

# For testing on my home computer.
home_dir = home.replace('\\', '/')
fname = "%s/Downloads/teamdat.db" % (home_dir,)
teamfile_location = "%s/Desktop/" % (home_dir,)

sim_time        = 103    # in minutes
speedup         = 4.00  # how much faster the simulation is when compared to realtime (obtained when running radar script)
slp_time        = 55    # approximate time between radar scans (in real-time seconds)
spd_limit       = 65    # in mph.
fill_rate       = 15    # rate at which a fuel pump fills a gas tank (in seconds per gallon)
stuck_time      = 40    # how long after sim start that people can start getting stuck (in real-time minutes)
cc_time         = 20    # how long after sim start that people can start experiencing chaser convergence (in real-time minutes)
sunset_time     = 75    # how long after sim start that the sun sets in the simulation (in real-time minutes); this affects hazard chances
dr_chance       = .075  # chance of driving onto a dirt road
cc_chance       = .025  # chance of getting stuck in chaser convergence
tire_chance     = .001  # chance of popping a tire during the sim (same for all vehicle types)
dead_end_chance = .005  # chance of hitting a dead end during the sim (same for all vehicle types)
flood_chance    = .0025 # chance of hitting a flooded roadway during the sim (same for all vehicle types)
extra_all_time  = 30    # adding extra time to the _all placefile to avoid disappearing (in seconds)

# Check for old save files that might cause issues with teams starting if they've participated in previous years.
if os.path.exists(fname) == True:
    d         = shelve.open(fname)
    init_time = d['init_time']
    end_time  = init_time + datetime.timedelta(minutes=sim_time)
    time_now  = datetime.datetime.utcnow()
    C_Team_Name  = d['c_team']
    d.close()
    if time_now > end_time:
        os.remove(fname)
        if os.path.exists("%s%s.php" % (teamfile_location ,C_Team_Name,)):
            os.remove("%s%s.php" % (teamfile_location ,C_Team_Name,))

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
    dr_deg       = d['dr_deg']
    dist         = d['dist']
    dr_dist      = d['dr_dist']
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
    file_footerend  = '\nEnd:\n'

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
    print " ------------------------------------------------------------------------"
    print "|--_-_-_-_---                 Welcome to the                 --_-_-_-_---|"
    print "|   -_-_-_     _____  _____ _    _            __  __  _____     -_-_-_   |"
    print "|    -_-_-    |_   _|/ ____| |  | |     /\   |  \/  |/ ____|     -_-_-   |"
    print "|     -__-      | | | (___ | |  | |    /  \  | \  / | (___        -__-   |"
    print "|    _-_        | |  \___ \| |  | |   / /\ \ | |\/| |\___ \      _-_     |"
    print "|   _-         _| |_ ____) | |__| |  / ____ \| |  | |____) |    _-       |"
    print "|   -_        |_____|_____/ \____/  /_/    \_\_|  |_|_____/     -_       |"
    print "|     -_                                                          -_     |"
    print "|   ``_-_//              Storm Chasing Simulation               ``_-_//  |"
    print " ------------------------------------------------------------------------"
    print ""
    time.sleep(1)
    print "A few things before we get started..."
    print ""
    print ""
    time.sleep(1)
    print "Change your radar polling location to:"
    print "http://server.iawx.info/chase/l2data/"
    print ""
    time.sleep(0.25)
    print "Change your warning server to:"
    print "http://www.meteor.iastate.edu/~%s/chase/warnings/" % (netid,)
    print ""
    time.sleep(0.25)
    print "Add a placefile for Live Storm Reports (LSRs):"
    print "http://www.meteor.iastate.edu/~%s/chase/endpoints/placefile_lsr.py" % (netid,)
    print ""
    print ""
    time.sleep(0.5)
    raw_input("Once you have that all taken care of, type and let me \nknow you're ready to continue. ")
    time.sleep(1)
    print ""
    print "Alright, let's do this.\n"
    time.sleep(4)
    print "Oh, and roll the maps. Don't fold the maps."
    print ""
    time.sleep(1)
    print "------------------------------------------------------------------------"
    print ""
    time.sleep(3)

    # Create team database file then ask for team name and create a separate
    # variable for use as a file name.
    Team_Name = raw_input("Enter a team name: ")
    C_Team_Name = Team_Name.replace(" ", "_")

    # While statement to check and see if the selected team name already exists.
    while os.path.exists("%s%s.php" % (teamfile_location, C_Team_Name,)) == True:
        print ""
	print "That team name is already in use."
	Team_Name = raw_input("Please enter another team name: ")
	C_Team_Name = Team_Name.replace(" ", "_")
    else:
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
	file1.close()
        if (Team_Name.title() == "Cow") or (Team_Name.title() == "Cows"):
            print ""
            time.sleep(1)
            print "I gotta go Julia, we got cows!"
            time.sleep(1)
            Team_Name = "I Am Cow"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Bill Paxton") or (Team_Name.title() == "Bill Harding"):
            print ""
            time.sleep(1)
            print 'Why do you call Billy "The Extreme?"'
            time.sleep(1)
            print 'Because Billy *is* "The Extreme."'
            time.sleep(1)
            Team_Name = "The Extreme"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Helen Hunt") or (Team_Name.title() == "Jo Harding"):
            print ""
            time.sleep(1)
            print "Hang on a second, boss lady, hold your horses."
            time.sleep(1)
            Team_Name = "Boss Lady"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Dusty"):
            print ""
            time.sleep(1)
            print "It's the wonder of nature, baby!"
            time.sleep(1)
            Team_Name = "Dusty"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Rabbit"):
            print ""
            time.sleep(1)
            print "Uh... yeah, trust me. Rabbit is good, Rabbit is wise."
            time.sleep(1)
            Team_Name = "Rabbit"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Preacher"):
            print ""
            time.sleep(1)
            print "The twister caught it, and sucked it right up!"
            time.sleep(1)
            Team_Name = "Preacher"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Beltzer"):
            print ""
            time.sleep(1)
            print "That's no moon, that's a space station!"
            time.sleep(1)
            Team_Name = "Beltzer"
            C_Team_Name = Team_Name.replace(" ", "_")              
        elif (Team_Name.upper() == "F5") or (Team_Name.upper() == "EF5"):
            print ""
            time.sleep(1)
            print "Is there an F5? What would that be like?"
            time.sleep(1)
            Team_Name = "The Finger of God"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "The Suck Zone") or (Team_Name.title() == "Suck Zone"):
            print ""
            time.sleep(1)
            print "... and it NEVER hits the ground!"
            time.sleep(1)
            Team_Name = "The Suck Zone"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Columbus"):
            print ""
            time.sleep(1)
            print "Susan, get my pants!"
            time.sleep(1)
            Team_Name = "Columbus"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Oscar Mayer") or (Team_Name.title() == "Wienermobile") or (Team_Name.title() == "Oscar Mayer Wienermobile"):
            print ""
            time.sleep(1)
            print "I wish I were an Oscar Mayer Wiener... except while chasing, good luck."
            time.sleep(1)
            Team_Name = "Oscar Mayer Wienermobile"
            C_Team_Name = Team_Name.replace(" ", "_")            
        elif (Team_Name.title() == "Jarrell"):
            print ""
            time.sleep(1)
            print "Unlike this tornado, you should avoid sitting in one spot for a half hour."
            time.sleep(1)
            Team_Name = "The Grinders"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "El Reno"):
            print ""
            time.sleep(1)
            print "Let's be real, El Reno was an EF5"
            time.sleep(1)
            Team_Name = "The EF3s"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Moore 1999") or (Team_Name.title() == "Moore 99"):
            print ""
            time.sleep(1)
            print "Think your vehicle can drive faster than the winds in this tornado?"
            time.sleep(1)
            Team_Name = "The Speed Demons"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Moore 2013") or (Team_Name.title() == "Moore 13"):
            print ""
            time.sleep(1)
            print "Seriously, can't Moore get a break?"
            time.sleep(1)
            Team_Name = "The Repeats"
            C_Team_Name = Team_Name.replace(" ", "_")            
        elif (Team_Name.title() == "Pampa"):
            print ""
            time.sleep(1)
            print "One small and seriously angry tornado."
            time.sleep(1)
            Team_Name = "The Drill Bits"
            C_Team_Name = Team_Name.replace(" ", "_")          
        elif (Team_Name.title() == "Andover"):
            print ""
            time.sleep(1)
            print "Where shouldn't you take shelter from a tornado?"
            time.sleep(1)
            Team_Name = "The Overpasses"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Tri-State"):
            print ""
            time.sleep(1)
            print "Will you cover three states during your chase? I hope not."
            time.sleep(1)
            Team_Name = "The Tri-State Tornado"
            C_Team_Name = Team_Name.replace(" ", "_")            
        elif (Team_Name.title() == "Dave") or (Team_Name.title() == "Dave Flory"):
            print ""
            time.sleep(1)
            print "Never skip a Dave class to go chasing. Never."
            time.sleep(1)
            Team_Name = "Dave Flory"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Dr. Gallus") or (Team_Name.title() == "Dr Gallus") or (Team_Name.title() == "Bill Gallus"):
            print ""
            time.sleep(1)
            print "If you haven't taken MTEOR 407, what are you even doing with your life?"
            time.sleep(1)
            Team_Name = "Bill Gallus"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Kyle") or (Team_Name.title() == "Kyle Hugeback"):
            print ""
            time.sleep(1)
            print "You'd think being AMS Pres would guarantee you tornadoes... You'd be wrong."
            time.sleep(1)
            Team_Name = "President Material"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Jon") or (Team_Name.title() == "Jon Thielen"):
            print ""
            time.sleep(1)
            print "You're pretty much guaranteed to see a tornado now."
            time.sleep(1)
            Team_Name = "Genius Level Chasing"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Melissa") or (Team_Name.title() == "Melissa Piper"):
            print ""
            time.sleep(1)
            print "Well, you'll definitely have your money well managed for your chase."
            time.sleep(1)
            Team_Name = "The Treasurers"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Ben") or (Team_Name.title() == "Ben Smith"):
            print ""
            time.sleep(1)
            print "Gotta start somewhere, I suppose."
            time.sleep(1)
            Team_Name = "Team Noob"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Joey") or (Team_Name.title() == "Joey Krastel"):
            print ""
            time.sleep(1)
            print "Drill bit tornadoes are best tornadoes."
            time.sleep(1)
            Team_Name = "Team Pampa"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Jake") or (Team_Name.title() == "Jake Smith"):
            print ""
            time.sleep(1)
            print "I see you didn't choose to be Ben. For shame."
            time.sleep(1)
            Team_Name = "The Older Smith Brother"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Kris") or (Team_Name.title() == "Kris Tuftedal"):
            print ""
            time.sleep(1)
            print "Why on earth would you choose some random alum? Oh well, here goes nothing!"
            time.sleep(1)
            Team_Name = "Kris driving a radar"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.title() == "Sean Stelten"):
            print ""
            time.sleep(1)
            print "I see you decided to leave the Marshall Islands to come chase."
            time.sleep(1)
            Team_Name = "Team Rozel"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.upper() == "TIV"):
            print ""
            time.sleep(1)
            print "Gonna intercept some naders today."
            time.sleep(1)
            Team_Name = "Tornado Intercept Vehicle"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.upper() == "DOW6") or (Team_Name.upper() == "DOW 6"):
            print ""
            time.sleep(1)
            print "Josh Wurman would be proud."
            time.sleep(1)
            Team_Name = "Doppler On Wheels 6"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.upper() == "DOW7") or (Team_Name.upper() == "DOW 7"):
            print ""
            time.sleep(1)
            print "Karen Kosiba would be proud."
            time.sleep(1)
            Team_Name = "Doppler On Wheels 7"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.upper() == "DOW8") or (Team_Name.upper() == "DOW 8"):
            print ""
            time.sleep(1)
            print "Josh Wurman and Karen Kosiba would be proud."
            time.sleep(1)
            Team_Name = "Rapid-Scan DOW"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.upper() == "OU"):
            print ""
            time.sleep(1)
            print "Howie Bluestein would be proud."
            time.sleep(1)
            Team_Name = "OU RaXPol Radar"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.upper() == "TTU"):
            print ""
            time.sleep(1)
            print "Chris Weiss would be proud."
            time.sleep(1)
            Team_Name = "Texas Tech Ka-Band Radar"
            C_Team_Name = Team_Name.replace(" ", "_")
        elif (Team_Name.upper() == "SBU"):
            print ""
            time.sleep(1)
            print "Mike French would be proud."
            time.sleep(1)
            Team_Name = "SBU Phased Array Radar"
            C_Team_Name = Team_Name.replace(" ", "_")            
        elif (Team_Name.title() == "Mesonet"):
            print ""
            time.sleep(1)
            print "Researching tornadoes is life."
            time.sleep(1)
            Team_Name = "Mobile Mesonet Vehicle"
            C_Team_Name = Team_Name.replace(" ", "_")          
            
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
	file1.close()
    
    if (Team_Name == "The Extreme"):
        Car_Type = "Bill's Truck"
        print ""
        print "Your team gets Bill's pickup truck."
        time.sleep(1)
    elif (Team_Name == "Boss Lady"):
        Car_Type = "Jo's Jeep"
        print ""
        print "Your team gets Jo's jeep."
        time.sleep(1)
    elif (Team_Name == "Dusty"):
        Car_Type = "Barn Burner"
        print ""
        print "Your team gets Dusty's Barn Burner."
        time.sleep(1)
    elif (Team_Name == "Rabbit"):
        Car_Type = "Rabbit's Truck"
        print ""
        print "Your team gets Rabbit's pickup truck."
        time.sleep(1)
    elif (Team_Name == "Preacher"):
        Car_Type = "Preacher's Car"
        print ""
        print "Your team gets Preacher's car."
        time.sleep(1)
    elif (Team_Name == "Beltzer"):
        Car_Type = "Beltzer's Van"
        print ""
        print "Your team gets Beltzer's van."
        time.sleep(1)
    elif (Team_Name == "Oscar Mayer Wienermobile"):
        Car_Type = "Wienermobile"
        print ""
        print "Oh boy, your team gets the Wienermobile."
        time.sleep(1)
    elif (Team_Name == "Dave Flory"):
        Car_Type = "SUV"
        print ""
        print "Your team gets an SUV."
        time.sleep(1)
    elif (Team_Name == "Dr Gallus"):
        Car_Type = "Sedan"
        print ""
        print "Your team gets a sedan."
        time.sleep(1)
    elif (Team_Name == "President Material"):
        Car_Type = "Compact"
        print ""
        print "Your team gets a compact car."
        time.sleep(1)
    elif (Team_Name == "Genius Level Chasing"):
        Car_Type = "Sedan"
        print ""
        print "Your team gets a sedan."
        time.sleep(1)
    elif (Team_Name == "The Treasurers"):
        Car_Type = "Compact"
        print ""
        print "Your team gets a compact car."
        time.sleep(1)
    elif (Team_Name == "Team Noob"):
        Car_Type = "Sedan"
        print ""
        print "Your team gets a sedan."
        time.sleep(1)
    elif (Team_Name == "Team Pampa"):
        Car_Type = "Compact"
        print ""
        print "Your team gets a compact car."
        time.sleep(1)
    elif (Team_Name == "The Older Smith Brother"):
        Car_Type = "Sedan"
        print ""
        print "Your team gets a sedan."
        time.sleep(1)
    elif (Team_Name == "Kris driving a radar") or (Team_Name == "SBU Phased Array Radar"):
        Car_Type = "SBU LPAR"
        print ""
        print "Your team gets Stony Brook's low-powered phased array radar."
        time.sleep(1)
    elif (Team_Name == "Team Rozel"):
        Car_Type = "Sedan"
        print ""
        print "Your team gets a sedan."
        time.sleep(1)
    elif (Team_Name == "Tornado Intercept Vehicle"):
        Car_Type = "TIV 2"
        print ""
        print "Your team gets the TIV 2."
        time.sleep(1)
    elif (Team_Name == "Doppler On Wheels 6"):
        Car_Type = "DOW 6"
        print ""
        print "Your team gets DOW 6."
        time.sleep(1)
    elif (Team_Name == "Doppler On Wheels 7"):
        Car_Type = "DOW 7"
        print ""
        print "Your team gets DOW 7."
        time.sleep(1)
    elif (Team_Name == "Rapid-Scan DOW"):
        Car_Type = "DOW 8"
        print ""
        print "Your team gets DOW 8."
        time.sleep(1)
    elif (Team_Name == "OU RaXPol Radar"):
        Car_Type = "OU RaXPol"
        print ""
        print "Your team gets OU's RaXPol radar."
        time.sleep(1)
    elif (Team_Name == "Texas Tech Ka-Band Radar"):
        Car_Type = "TTU Ka-Band"
        print ""
        print "Your team gets Texas Tech's Ka-Band radar."
        time.sleep(1)
    elif (Team_Name == "Mobile Mesonet Vehicle"):
        Car_Type = "Mobile Mesonet"
        print ""
        print "Your team gets a mobile mesonet vehicle."
        time.sleep(1)
        
    else:
        time.sleep(1)
        print ""
        print "Your team may choose from the following car types:"
        time.sleep(1)
        print "Compact"
        time.sleep(0.1)
        print "Sedan"
        time.sleep(0.1)
        print "Hybrid"
        time.sleep(0.1)
        print "Pickup"
        time.sleep(0.1)
        print "SUV"
        print ""
        time.sleep(1)
        Car_Type  = raw_input("Enter your team's car type of choice (as specified above): ")
        time.sleep(1)
    
    # If statement to set vehicle specific variables or request new vehicle
    # (Consider making these in to def() for easier modification and calling.)
    if (Car_Type == "Compact") or (Car_Type == "compact"):
        #Pre-sets for compact car.
        Car_Type = "Compact"
        car_number   = 1
        top_speed    = 135.
        dr_top_spd   = 40.
        mpg          = 38.
        fuel_cap     = 13.
        stuck_chance = .01
    elif (Car_Type == "Sedan") or (Car_Type ==  "sedan"):
        #Pre-sets for sedan (4 door type car).
        Car_Type = "Sedan"
        car_number   = 2
        top_speed    = 150.
        dr_top_spd   = 50.
        mpg          = 35.
        fuel_cap     = 17.
        stuck_chance = .008
    elif (Car_Type == "Hybrid") or (Car_Type ==  "hybrid"):
        #Pre-sets for hybrid sedan (4 door type car).
        Car_Type = "Hybrid"
        car_number   = 3
        top_speed    = 115.
        dr_top_spd   = 50.
        mpg          = 47.
        fuel_cap     = 16.
        stuck_chance = .008
    elif (Car_Type == "Pickup") or (Car_Type ==  "pickup"):
        #Pre-sets for pickup.
        Car_Type = "Pickup"
        car_number   = 4
        top_speed    = 130.
        dr_top_spd   = 60.
        mpg          = 16.
        fuel_cap     = 30.
        stuck_chance = .002
    elif (Car_Type == "SUV") or (Car_Type ==  "suv"):
        #Pre-sets for suv.
        Car_Type = "SUV"
        car_number   = 5
        top_speed    = 125.
        dr_top_spd   = 55.
        mpg          = 24.
        fuel_cap     = 20.
        stuck_chance = .006
    elif (Car_Type == "Bill's Truck"):
        #Pre-sets for Bill's truck.
        car_number   = 6
        top_speed    = 110.
        dr_top_spd   = 55.
        mpg          = 7.
        fuel_cap     = 26.
        stuck_chance = .001
    elif (Car_Type == "Jo's Jeep"):
        #Pre-sets for Jo's jeep.
        car_number   = 6
        top_speed    = 90.
        dr_top_spd   = 45.
        mpg          = 13.
        fuel_cap     = 20.
        stuck_chance = .002
    elif (Car_Type == "Barn Burner"):
        #Pre-sets for the Barn Burner.
        car_number   = 6
        top_speed    = 85.
        dr_top_spd   = 35.
        mpg          = 6.
        fuel_cap     = 60.
        stuck_chance = .004
    elif (Car_Type == "Rabbit's Truck"):
        #Pre-sets for Rabbit's truck.
        car_number   = 6
        top_speed    = 95.
        dr_top_spd   = 40.
        mpg          = 9.
        fuel_cap     = 18.
        stuck_chance = .002
    elif (Car_Type == "Preacher's Car"):
        #Pre-sets for Preacher's car.
        car_number   = 6
        top_speed    = 100.
        dr_top_spd   = 40.
        mpg          = 20.
        fuel_cap     = 19.
        stuck_chance = .006
    elif (Car_Type == "Beltzer's Van"):
        #Pre-sets for Beltzer's van.
        car_number   = 6
        top_speed    = 90.
        dr_top_spd   = 35.
        mpg          = 17.
        fuel_cap     = 22.
        stuck_chance = .005
    elif (Car_Type == "Wienermobile"):
        #Pre-sets for the Wienermobile.
        car_number   = 6
        top_speed    = 110.
        dr_top_spd   = 35.
        mpg          = 20.
        fuel_cap     = 30.
        stuck_chance = .05
    elif (Car_Type == "TIV 2"):
        #Pre-sets for the TIV.
        car_number   = 7
        top_speed    = 105.
        dr_top_spd   = 55.
        mpg          = 8.
        fuel_cap     = 95.
        stuck_chance = .002
    elif (Car_Type == "DOW 6") or (Car_Type == "DOW 7"):
        #Pre-sets for DOW 6 and 7.
        car_number   = 7
        top_speed    = 100.
        dr_top_spd   = 35.
        mpg          = 5.
        fuel_cap     = 200.
        stuck_chance = .006
    elif (Car_Type == "DOW 8"):
        #Pre-sets for DOW 8.
        car_number   = 7
        top_speed    = 95.
        dr_top_spd   = 35.
        mpg          = 4.
        fuel_cap     = 200.
        stuck_chance = .006
    elif (Car_Type == "OU RaXPol"):
        #Pre-sets for the OU RaXPol radar.
        car_number   = 7
        top_speed    = 105.
        dr_top_spd   = 35.
        mpg          = 12.
        fuel_cap     = 40.
        stuck_chance = .003
    elif (Car_Type == "TTU Ka-Band"):
        #Pre-sets for the Texas Tech Ka-Band radar.
        car_number   = 7
        top_speed    = 120.
        dr_top_spd   = 40.
        mpg          = 14.
        fuel_cap     = 35.
        stuck_chance = .003
    elif (Car_Type == "SBU LPAR"):
        #Pre-sets for Stony Brook's LPAR radar.
        car_number   = 7
        top_speed    = 115.
        dr_top_spd   = 40.
        mpg          = 12.
        fuel_cap     = 35.
        stuck_chance = .003
    elif (Car_Type == "Mobile Mesonet"):
        #Pre-sets for mobile mesonet vehicles.
        car_number   = 7
        top_speed    = 150.
        dr_top_spd   = 50.
        mpg          = 35.
        fuel_cap     = 17.
        stuck_chance = .006        
    else:
        car_number = 8 # If a GUI is created with a dropdown list, this part of the if statement
                       # and the following while statement can be removed.

    while (car_number == 8):
        Car_Type = raw_input("Your entry is not a valid option, please re-enter your car type: ")
        time.sleep(1)

        # If statement to set vehicle specific variables or request new vehicle        
        if (Car_Type == "Compact") or (Car_Type ==  "compact"):
            #Pre-sets for compact car.
            Car_Type = "Compact"
            car_number   = 1
            top_speed    = 135.
            dr_top_spd   = 40.
            mpg          = 38.
            fuel_cap     = 13.
            stuck_chance = .01
        elif (Car_Type == "Sedan") or (Car_Type ==  "sedan"):
            #Pre-sets for sedan (4 door type car).
            Car_Type = "Sedan"
            car_number   = 2
            top_speed    = 150.
            dr_top_spd   = 50.
            mpg          = 35.
            fuel_cap     = 17.
            stuck_chance = .008
        elif (Car_Type == "Hybrid") or (Car_Type ==  "hybrid"):
            #Pre-sets for hybrid sedan (4 door type car).
            Car_Type = "Hybrid"
            car_number   = 3
            top_speed    = 115.
            dr_top_spd   = 50.
            mpg          = 47.
            fuel_cap     = 16.
            stuck_chance = .008
        elif (Car_Type == "Pickup") or (Car_Type ==  "pickup"):
            #Pre-sets for pickup.
            Car_Type = "Pickup"
            car_number   = 4
            top_speed    = 130.
            dr_top_spd   = 60.
            mpg          = 16.
            fuel_cap     = 30.
            stuck_chance = .002
        elif (Car_Type == "SUV") or (Car_Type ==  "suv"):
            #Pre-sets for suv.
            Car_Type = "SUV"
            car_number   = 5
            top_speed    = 125.
            dr_top_spd   = 55.
            mpg          = 24.
            fuel_cap     = 20.
            stuck_chance = .006
        else:
            car_number = 8

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
    time.sleep(1)
    print ""
    print "Enter longitude (the 2nd number) of your target city from GR."
    print "(make sure it's exactly the same and include the negative)"
    lon = raw_input("Longitude: ")
    while isinstance(lon, basestring):
        try:
            lon = float(lon)
        except ValueError:
            lon = raw_input("Incorrect longitude entered, please re-enter longitude: ")
    time.sleep(1)

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
    dr_dist      = 0
    dist         = 0
    deg          = 0
    dr_deg       = 0
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
    if car_number == 7:
        # Allows scientific vehicles to start with a full tank.
        fuel_level = fuel_cap
    else:
        fuel_level = fuel_cap - random.randint(1,(fuel_cap-2))
    
    # Create the team specific placefile using the entered team name.
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
    file_footerend  = '\nEnd:\n'
    file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
    file1.write(file_headertext)
    file1.write('Object: %s,%s\n' % (lat, lon))
    file1.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                (Team_Name,init_time.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level,))
    file1.write(file_footertext)
    file1.close()

    # Create the team specific placefile to save a moving placefile.
    file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "w" )
    file2.write(file_headertext)
    file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (init_time.strftime("%Y-%m-%d"),init_time.strftime("%H:%M:%S"), \
                                              init_time.strftime("%Y-%m-%d"), \
                                              (init_time+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
    file2.write('Object: %s,%s\n' % (lat, lon))
    file2.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                (Team_Name,init_time.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level,))
    file2.write(file_footertext)
    file2.close()

    # Create the team specific placefile to save a placefile with all points.
    file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "w" )
    file3.write(file_headertext)
    file3.write('Object: %s,%s\n' % (lat, lon))
    file3.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                (Team_Name,init_time.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level,))
    file3.write(file_footertext)
    file3.close()

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
    d['dr_dist']      = dr_dist
    d['new_deg']      = new_deg
    d['direct']       = direct
    d['old_direct']   = old_direct
    d['dr_direct']    = dr_direct
    d['dr_deg']       = dr_deg
    d['cc_top_spd']   = cc_top_spd
    d['aft_dark_inc'] = aft_dark_inc
    d['sun_check']    = sun_check
    d['init_time']    = init_time
    d['fuel_level']   = fuel_level
 

    # Print the file name to add to placefile. MODIFY THE netid VAR TO WHOEVER IS RUNNING THE RADAR CODE
    time.sleep(1)
    print ""
    print "------------------------------------------------------------------------"
    print ""
    print "Please type or copy both of the following links into your placefile \nwindow in GR.:"
    print ""
    time.sleep(0.5)
    print "Single time step placefile:"
    print "http://www.meteor.iastate.edu/~%s/chase/loc/%s.php" % (netid,C_Team_Name,)
    print ""
    time.sleep(0.5)
    print "Moving with animated radar placefile:"
    print "http://www.meteor.iastate.edu/~%s/chase/loc/%s_moving.php" % (netid,C_Team_Name,)
    print ""
    print "------------------------------------------------------------------------"
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
    delta_t        = (time_step - init_time)
    secs           = delta_t.total_seconds()
    mins           = secs / 60.
    d['time_step'] = time_step
    d['mins']      = mins

    if (mins >= sunset_time) and (sun_check == 0):
        print "The sun has now set. Your team can continue chasing, but be especially careful..."
        print ""
        aft_dark_inc = .05
        sun_check    = 1
        d['aft_dark_inc'] = aft_dark_inc
        d['sun_check']    = sun_check      
        
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
    time.sleep(0.5)
    print "Please input distance of travel (in miles, e.g. 1, 3.5, etc)"
    if dr_check != 0:
        spd_lim_dist = (slp_time * speedup * dr_top_spd)/3600.
        dist = raw_input("At your dirt road top speed, the farthest you can go is %.2f miles: " % (spd_lim_dist))
    elif cc_turns != 0:
        spd_lim_dist = (slp_time * speedup * cc_top_spd)/3600.
        dist = raw_input("Because of chaser convergence, the farthest you can go is %.2f miles: " % (spd_lim_dist))
    else:
        spd_lim_dist = (slp_time * speedup * spd_limit)/3600.
        dist = raw_input("Traveling more than %.2f miles will exceed the speed limit: " % (spd_lim_dist+0.01))

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

    # Check to see if a team is going the opposite direction on a dirt road.
    op_deg = deg + 180
    if op_deg >= 360:
        op_deg -= 360

    if (dr_check == 1) and (dr_deg == op_deg):
        dr_dist -= dist
    elif (dr_check == 1) and (direct == dr_direct):
        dr_dist += dist

    if (cc_turns !=0) and (speed > cc_top_spd):
        speed = cc_top_spd
        dist  = (speed * slp_time * speedup) / 3600.
        print "Due to chaser convergence, you can't go that far between scans."
        print "The farthest you can go at your current top speed is %.2f miles." % (dist)
        print ""
            
    if (dr_check == 1) and (speed > dr_top_spd) and (dr_dist > 0) and ((direct == dr_direct) or (dr_deg == op_deg)):
        speed = dr_top_spd
        dist  = (speed * slp_time * speedup) / 3600.
        print "You can't go that fast on a dirt road."
        print "The farthest you can go at your current top speed is %.2f miles." % (dist)
        print "Your team continues on the dirt road."
        print ""

    elif (dr_check == 1) and (speed <= dr_top_spd) and (dr_dist > 0) and ((direct == dr_direct) or (dr_deg == op_deg)):
        print "Your team continues on the dirt road."
        print ""
        
    elif ((dr_check == 1) and (direct != dr_direct) and (dr_deg != op_deg)) or ((dr_check == 1) and (dr_dist <= 0) and (dr_deg == op_deg)):
        print "You've driven off of the dirt road and can reach your top speed again."
        print ""
        dr_check = 2
        if (speed > top_speed):
            speed = top_speed
            dist  = (speed * slp_time * speedup) / 3600.
            print "Due to your vehicle's top speed, you can't go that far between scans."
            print "The farthest you can go at your top speed is %.2f miles." % (dist)
            print ""
            
    else:
        if (speed > top_speed):
            speed = top_speed
            dist  = (speed * slp_time * speedup) / 3600.
            print "Due to your vehicle's top speed, you can't go that far between scans."
            print "The farthest you can go at your top speed is %.2f miles." % (dist)
            print ""

    d['speed']    = speed
    d['direct']   = direct
    d['dist']     = dist
    d['dr_dist']  = dr_dist
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

    # Update moving placefile.
    file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
    file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                              time_step.strftime("%Y-%m-%d"), \
                                              (time_step+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
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

    # Update all times placefile.
    file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
    file3.write('Object: %s,%s\n' % (lat, lon))
    if (speed != 0):
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
	file3.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
    else:
	file3.write(r'Icon: 0,0,000,6,2, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nFuel Remaining: %.2f gallons"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,fuel_level))
    file3.write(file_footerend)
    file3.close()

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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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

            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+cop_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nPULLED OVER"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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
        print "Your top speed will be decreased to %s mph until you change roads or back-track." % (int(dr_top_spd),)
        print ""
        
        d = shelve.open(fname)
        dr_check = 1
        dr_dist = dist
        dr_direct = direct
        dr_deg = deg
        d['dr_check'] = dr_check
        d['dr_direct'] = dr_direct
        d['dr_deg'] = dr_deg
        d['dr_dist'] = dr_dist
        d.close()
        
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


        file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file3.write('Object: %s,%s\n' % (lat, lon))     
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file3.write(file_footerend)
        file3.close()

        
    elif (dr_check == 1):
        file1 = open("%s%s.php" % (teamfile_location, C_Team_Name,), "w" )
        file1.write(file_headertext)
        file1.write('Object: %s,%s\n' % (lat, lon))
        file1.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file1.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file1.write(file_footertext)
        file1.close()


        file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


        file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file3.write('Object: %s,%s\n' % (lat, lon))     
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file3.write(file_footerend)
        file3.close()

        
    elif (dr_check == 2):
        d = shelve.open(fname)
        dr_check = 0
        dr_dist = 0
        d['dr_check'] = dr_check
        d.close()        

    # Setting up likelihood to get stuck in the mud.
    if (mins >= stuck_time) and (dr_check == 1):
        d = shelve.open(fname)
        stuck = random.uniform(0.0001,1.0)
        if (stuck < (stuck_chance + aft_dark_inc)):
            print "Your team is stuck in the mud and is attempting to free your vehicle."
            stuck_slp = random.randint(int(slp_time/4), slp_time*2)
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+stuck_slp+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD\nSTUCK IN THE MUD"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))     
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nON A DIRT ROAD\nSTUCK IN THE MUD"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

            
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))     
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()


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


        file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


        file3 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file3.write('Object: %s,%s\n' % (lat, lon))     
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nIN CHASER CONVERGENCE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
        file3.write(file_footerend)
        file3.close()


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

        file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                    time_step.strftime("%Y-%m-%d"), \
                                                    (time_step+datetime.timedelta(seconds=(slp_time+tire_slp+extra_all_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nFLAT TIRE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


        file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file3.write('Object: %s,%s\n' % (lat, lon))     
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file3.write(r'Icon: 0,0,000,6,10, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nFLAT TIRE"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file3.write(file_footerend)
        file3.close()

        
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


        file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A DEAD END"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


        file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file3.write('Object: %s,%s\n' % (lat, lon))     
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A DEAD END"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file3.write(file_footerend)
        file3.close()
        

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


        file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+extra_all_time))).strftime("%H:%M:%S")))
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A FLOODED ROADWAY"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


        file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file3.write('Object: %s,%s\n' % (lat, lon))     
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nHIT A FLOODED ROADWAY"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file3.write(file_footerend)
        file3.close()


    # Checking if team wants to refuel.
    if (0.00 < fuel_level <= (fuel_cap * 0.10)):
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


            file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
            file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                      time_step.strftime("%Y-%m-%d"), \
                                                      (time_step+datetime.timedelta(seconds=(slp_time+refuel_slp+extra_all_time))).strftime("%H:%M:%S")))            
            file2.write('Object: %s,%s\n' % (lat, lon))     
            file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file2.write(file_footertext)
            file2.close()


            file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
            file3.write('Object: %s,%s\n' % (lat, lon))     
            file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
            file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: %s mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                        (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,speed,direct,int_deg,fuel_level))
            file3.write(file_footerend)
            file3.close()

    
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


        file2 = open("%s%s_moving.php" % (teamfile_location, C_Team_Name,), "a" )
        file2.write('TimeRange: %sT%sZ %sT%sZ\n' % (time_step.strftime("%Y-%m-%d"),time_step.strftime("%H:%M:%S"), \
                                                  time_step.strftime("%Y-%m-%d"), \
                                                  (time_step+datetime.timedelta(seconds=(slp_time+refuel_slp+extra_all_time))).strftime("%H:%M:%S")))        
        file2.write('Object: %s,%s\n' % (lat, lon))     
        file2.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file2.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file2.write(file_footertext)
        file2.close()


        file3 = open("%s%s_all.php" % (teamfile_location, C_Team_Name,), "a" )
        file3.write('Object: %s,%s\n' % (lat, lon))     
        file3.write('Icon: 0,0,%3d,2,15,\n' % (int_deg,))
        file3.write(r'Icon: 0,0,000,6,6, "Team: %s\n%s UTC\nCar type: %s\nSpeed: 0 mph\nHeading: %s (%3d)\nFuel Remaining: %.2f gallons\nREFUELING"' % \
                    (Team_Name,time_step.strftime("%Y-%m-%d %H:%M:%S"),Car_Type,direct,int_deg,fuel_level))
        file3.write(file_footerend)
        file3.close()

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
