# button-machine.py
# Program that runs on an RPi that interacts w/ ThingieCounter.
# This takes a little bit of time to startup. Wait for the pulsing LED.
#
# depends: gpiozero
#
# --timball@gmail.com
# Tue Mar 27 20:56:18 EDT 2018

import local_settings as conf
from gpiozero import LED, PWMLED, Button
from signal import pause

# Base url for thingiecounter api
URL = conf.URL

# These correspond to RPi pins BE VERY CAREFUL HERE!
PNK_LED = conf.PNK_LED
RED_BTN = conf.RED_BTN
GRN_BTN = conf.GRN_BTN
BLU_BTN = conf.BLU_BTN


def put_curry(endpt):
    """ put_curry -- curry function to make the .when_released even easier
    than a decorator that takes a mostly empty function

    endpt -- end point we want to inc in ThingieCounter
    """
    def curry():
        import urllib2
        import json

        # print ("decorating function w/ arg: %s" % (endpt))
        url = URL + endpt
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'PUT'
        try:
            url = opener.open(request)
        except urllib.error.URLError as e:
            print("PUT %s URLError, reason: %s" % (url, e.reason))
        except urllib.error.HTTPError as e:
            print("HTTPError PUT %s == %s" % (url, e.code))
    return curry


red = put_curry("red")
green = put_curry("green")
blue = put_curry("blue")

if __name__ == "__main__":
    pink_led = PWMLED(PNK_LED)
    pink_led.value = 1

    red_button = Button(RED_BTN)
    red_button.when_released = red

    grn_button = Button(GRN_BTN)
    grn_button.when_released = green

    blu_button = Button(BLU_BTN)
    blu_button.when_released = blue

    print("ready!")
    pink_led.pulse()

    pause()
