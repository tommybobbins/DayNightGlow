DayNightGlow
============

Raspberry Pi and PiGlow day/night light. This is a set of scripts designed to provide similar light to Sunshine and Nighttime. It uses the piglow.py Python module from Jason Barnett @Boeeerb: https://github.com/Boeeerb/PiGlow

It uses the Astral python package to calculate sunrise, sunset and solar noon.
It then calculates for each of the 7 colours in a PiGlow how much light of each of those colours should be showing. It calculates the intensity of the light (between 0 and 255) around a normal distribution. It therefore requires the scipy packages. Instructions for installing both these are found in sunny.py

    $ sudo apt-get install python-scipy
    $ sudo pip install astral
    $ sudo mkdir /home/pi/LOGGING
To run automatically:

    nano /etc/rc.local
Add the following above the exit 0 towards the end of the file.

    /usr/bin/python /home/pi/DayNightGlow/sunny.py &

For example, for the colour red, we think of seeing it at Dawn and Dusk, for a short period of time, but quite brightly. So we calculate a normal distribution with a High Q (low mu of 0.04) and full brightness (255).

The Green LED would never end up switched on, so we normalise that around noon. White needs to be throttled as it washes out all other colours.

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

The PiGlow is available from Pimoroni:
http://shop.pimoroni.com/products/piglow
