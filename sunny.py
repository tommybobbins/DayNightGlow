#!/usr/bin/python
######################################
## Sun Emulator using PiGlow        ##
##                                  ##
##  Example by @Tommybobbins        ##
######################################
# Light curves are based on statistical
# normal distributions. Requires python-scipy.
# Uses the Sunrise/Sunset times from astral 
# python package.
#
# sudo apt-get install python-scipy
# sudo pip install astral
# Uses the piglow.py Python module from Jason Barnett @Boeeerb
# sudo mkdir /home/pi/LOGGING
# To run automatically:
# Add the following above the exit 0 in the /etc/rc.local
# /usr/bin/python /home/pi/DayNightGlow/sunny.py &

from astral import *
from piglow import PiGlow
import time
import datetime
import logging
dt = datetime.datetime.now()
logging.basicConfig(filename='/home/pi/LOGGING/lightoutput_%i_%i_%i.log' %(dt.year, dt.month, dt.day),level=logging.INFO)
from scipy import stats
number_seconds_day=60*60*24
centre = 0.0
total_intensity=0
max_brightness=255
intensity={}
piglow = PiGlow()
piglow.all(0)

a = Astral()
location = a["Manchester"]
#print (" %s %s %s %s %s \n" % (dawn, sunrise, noon, sunset, dusk))
#Information for Manchester
# 2014-01-21 07:30:11+00:00 2014-01-21 08:10:06+00:00 2014-01-21 12:20:18+00:00 2014-01-21 16:30:35+00:00 2014-01-21 17:10:31+00:00
# For the local timezone
#print ("Time: %s" % t)

logging.info("Epoch_Time\tRed\tOrange\tYellow\tGreen\tBlue\tWhite\tTotal")

def calculate_intensity(x,centre,mu,max_brightness):
    #Normal distribution
    gaussian = stats.norm(loc=centre, scale=mu)
    #Calculate the intensity at max
    max_value = gaussian.pdf(centre)
    #Multiply by the max_brightness (0-255)
    normalisation_value = max_brightness / max_value
    y = normalisation_value * gaussian.pdf(x)   
#    print (x,y)
    return(y)

while True:

    sun = location.sun(local=True)
    dusk=sun['dusk']
    noon=sun['noon']
    midnight=sun['noon']
    sunrise=sun['sunrise']
    sunset=sun['sunset']
    dawn=sun['dawn']
    midnight=sun['noon']+datetime.timedelta(hours=12)
    lastmidnight=sun['noon']-datetime.timedelta(hours=12)
#    print t.day,t.month,t.year
    dt = datetime.datetime.now()


    #Convert all the timings into Epoch times
    epoch_now = time.mktime(dt.timetuple())
    epoch_dawn = time.mktime(dawn.timetuple())
    epoch_sunrise= time.mktime(sunrise.timetuple())
    epoch_midnight= time.mktime(midnight.timetuple())
    epoch_lastmidnight= time.mktime(lastmidnight.timetuple())
    epoch_noon= time.mktime(noon.timetuple())
    epoch_sunset= time.mktime(sunset.timetuple())
    epoch_dusk= time.mktime(dusk.timetuple())

    #Now calculate the difference from the current time
    dawn_diff = float(epoch_dawn - epoch_now)
    sunrise_diff = float(epoch_sunrise - epoch_now)
    noon_diff = float(epoch_noon - epoch_now)
    sunset_diff = float(epoch_sunset - epoch_now)
    dusk_diff = float(epoch_dusk - epoch_now)
    midnight_diff = float(epoch_midnight - epoch_now)
    lastmidnight_diff = float(epoch_lastmidnight - epoch_now)

    #Now convert that the a percentage of the day away we are 
    norm_dawn_diff = dawn_diff / number_seconds_day
    norm_sunrise_diff = sunrise_diff / number_seconds_day
    norm_noon_diff = noon_diff / number_seconds_day
    norm_sunset_diff = sunset_diff / number_seconds_day
    norm_dusk_diff = dusk_diff / number_seconds_day
    if (epoch_now >  epoch_noon):
        norm_midnight_diff = midnight_diff / number_seconds_day
    elif (epoch_now < epoch_noon):
        norm_midnight_diff = lastmidnight_diff / number_seconds_day
    else:
        print ("Something wrong")

    #Output how many seconds we are away
#    print ("D %f, SR %f, N %f, SS %f, D %f M %f\n" % (dawn_diff, sunrise_diff, noon_diff, sunset_diff, dusk_diff, midnight_diff))
    #Output what percentage
#    print ("D %f, SR %f, N %f, SS %f, D %f , M %f\n" % (norm_dawn_diff, norm_sunrise_diff, norm_noon_diff, norm_sunset_diff, norm_dusk_diff, norm_midnight_diff))
    # Calculate Gaussian intensity
    # Dawn 
    #dawn red narrow mu 0.2
    #sunrise orange, yellow high mu 0.4
    #noon white broad, yellow thinner , green low intensity largest mu 0.6
    #midnight = noon + 12 hours blue red low intesity mu 2
    #sunset orange, yellow mu 0.4
    #dusk red 0.2
    #print ("Red")
    intensity['red'] = calculate_intensity(norm_dawn_diff,centre,0.04,255)
    intensity['red'] += calculate_intensity(norm_dusk_diff,centre,0.04,255)
    #print ("Orange")
    intensity['orange'] = calculate_intensity(norm_sunrise_diff,centre,0.02,255)
    intensity['orange'] += calculate_intensity(norm_sunset_diff,centre,0.02,255)
    #print ("Yellow")
    intensity['yellow'] = calculate_intensity(norm_sunrise_diff,centre,0.05,255)
    intensity['yellow'] += calculate_intensity(norm_sunset_diff,centre,0.05,255)
    intensity['yellow'] += calculate_intensity(norm_noon_diff,centre,0.08,255)
    #print ("Green")
    intensity['green'] = calculate_intensity(norm_noon_diff,centre,0.1,255)
    #print ("Blue")
    intensity['blue'] = calculate_intensity(norm_midnight_diff,centre,0.15,255)
    intensity['blue'] += calculate_intensity(norm_noon_diff,centre,0.09,255)
    #print ("White")
    intensity['white'] = calculate_intensity(norm_noon_diff,centre,0.07,64)

    total_intensity = 0
    for key in intensity:
        if (intensity[key] > 255):
            intensity[key] = 255
        else:
            intensity[key] = int(round(intensity[key]))
        total_intensity += intensity[key]
#        print ("Key = %s, value = %i\n" % (key, intensity[key]))

    piglow.red(intensity['red']) 
    piglow.orange(intensity['orange']) 
    piglow.yellow(intensity['yellow']) 
    piglow.green(intensity['green']) 
    piglow.blue(intensity['blue']) 
    piglow.white(intensity['white']) 


#   Condensed logging for graphing purposes (time, followed by the colours)
    logging.info("%i %i %i %i %i %i %i %i" %(epoch_now,
                                      intensity['red'],
                                      intensity['orange'],
                                      intensity['yellow'],
                                      intensity['green'],
                                      intensity['blue'],
                                      intensity['white'],
                                      total_intensity)
                                     )
    time.sleep(60)

