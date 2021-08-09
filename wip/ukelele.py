"""
LED Ukulele with Feather Sense and PropMaker Wing
Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!
Written by Erin St Blaine & Limor Fried for Adafruit Industries
Copyright (c) 2019-2020 Adafruit Industries
Licensed under the MIT license.
All text above must be included in any redistribution.

MODES:
0 = off/powerup, 1 = sound reactive, 2 = non-sound reactive, 3 = tilt
Pluck high A on the E string to toggle sound reactive mode on or off
Pluck high A♭ on the E string to cycle through the animation modes
"""

import time
import array
import digitalio
import audiobusio
import board
import neopixel
from ulab.scipy.signal import spectrogram
from ulab import numpy as np
import adafruit_lsm6ds
from adafruit_led_animation.helper import PixelMap
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.color import colorwheel
from adafruit_led_animation.color import (
    BLACK,
    RED,
    ORANGE,
    BLUE,
    PURPLE,
    WHITE,
)

MAX_BRIGHTNESS = 0.3 #set max brightness for sound reactive mode
NORMAL_BRIGHTNESS = 0.1 #set brightness for non-reactive mode
VOLUME_CALIBRATOR = 50 #multiplier for brightness mapping
ROCKSTAR_TILT_THRESHOLD = 200 #shake threshold
SOUND_THRESHOLD = 430000 #main strum or pluck threshold

# Main loop
while True:
    i = (i + 0.5) % 256  # run from 0 to 255
    TILT_COLOR = colorwheel(i)
    if MODE == 0:  # If currently off...
        enable.value = True
        power_on(POWER_ON_DURATION)  # Power up!
        MODE = LASTMODE

    elif MODE >= 1:  # If not OFF MODE...
        mic.record(samples_bit, len(samples_bit))
        samples = np.array(samples_bit[3:])
        spectrum = spectrogram(samples)
        spectrum = spectrum[:128]
        spectrum[0] = 0
        spectrum[1] = 0
        peak_idx = np.argmax(spectrum)
        peak_freq = peak_idx * 16000 / 256
#        print((peak_idx, peak_freq, spectrum[peak_idx]))
        magnitude = spectrum[peak_idx]
#         time.sleep(1)
        if peak_freq == 812.50 and magnitude > SOUND_THRESHOLD:
            animations.next()
            time.sleep(1)
        if peak_freq == 875 and magnitude > SOUND_THRESHOLD:
            if MODE == 1:
                MODE = 2
                print("mode = 2")
                LASTMODE = 2
                time.sleep(1)
            elif MODE == 2:
                MODE = 1
                print("mode = 1")
                LASTMODE = 1
                time.sleep(1)