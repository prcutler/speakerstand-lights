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
from adafruit_led_animation.animation import rainbow
import board
import neopixel
from ulab.scipy.signal import spectrogram
from ulab import numpy as np
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
# Add analogio for analog mic
from analogio import AnalogIn

MAX_BRIGHTNESS = 0.3 #set max brightness for sound reactive mode
NORMAL_BRIGHTNESS = 0.1 #set brightness for non-reactive mode
sample_window = 0.1  # Sample window for average level
VOLUME_CALIBRATOR = 50 #multiplier for brightness mapping
ROCKSTAR_TILT_THRESHOLD = 200 #shake threshold
SOUND_THRESHOLD = 430000 #main strum or pluck threshold

# Set to the length in seconds for the animations
POWER_ON_DURATION = 1.3
ROCKSTAR_TILT_DURATION = 1

NUM_PIXELS = 32  # Number of pixels used in project
NEOPIXEL_PIN = board.D6

pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=1, auto_write=False)
pixels.fill(0)  # NeoPixels off ASAP on startup
pixels.show()

# Was pixel_map_around (I think that's the sound reactive one)
pixel_map_around = PixelMap(pixels, [
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
    ], individual_pixels=True)

# Was Bottom up along both sides at once
pixel_map_reverse = PixelMap(pixels, [
    31, 30, 29, 28, 27, 26, 25, 24,
    23, 22, 21, 20, 19, 18, 17, 16,
    15, 14, 13, 12, 11, 10, 9, 8,
    7, 6, 5, 4, 3, 2, 1, 0,
    ], individual_pixels=True)

#Was Every other pixel, starting at the bottom and going upwards along both sides
pixel_map_skip = PixelMap(pixels, [
    0, 2, 4, 6, 
    8, 10, 12, 14,
    16, 18, 20, 22,
    24, 26, 28, 30,
    ], individual_pixels=True)

pixel_map = [pixel_map_around, pixel_map_reverse, pixel_map_skip]

def power_on(duration):
    """
    Animate NeoPixels for power on.
    """
    # TODO 20210811 - This needs to be re-written I think to keep the loop going
    start_time = time.monotonic()  # Save start time
    while True:
        elapsed = time.monotonic() - start_time  # Time spent
        if elapsed > duration:  # Past duration?
            break  # Stop animating
        powerup.animate()

def rockstar_tilt(duration):
    """
    Tilt animation - lightning effect with a rotating color
    :param duration: duration of the animation, in seconds (>0.0)
    """
    tilt_time = time.monotonic()  # Save start time
    while True:
        elapsed = time.monotonic() - tilt_time  # Time spent
        if elapsed > duration:  # Past duration?
            break  # Stop animating
        pixels.brightness = MAX_BRIGHTNESS
        pixels.fill(TILT_COLOR)
        pixels.show()
        time.sleep(0.01)
        pixels.fill(BLACK)
        pixels.show()
        time.sleep(0.03)
        pixels.fill(WHITE)
        pixels.show()
        time.sleep(0.02)
        pixels.fill(BLACK)
        pixels.show()
        time.sleep(0.005)
        pixels.fill(TILT_COLOR)
        pixels.show()
        time.sleep(0.01)
        pixels.fill(BLACK)
        pixels.show()
        time.sleep(0.03)    

# Cusomize LED Animations  ------------------------------------------------------
powerup = RainbowComet(pixel_map[1], speed=0, tail_length=25, bounce=False)
rainbow = Rainbow(pixel_map[2], speed=0, period=6, name="rainbow", step=2.4)
rainbow_chase = RainbowChase(pixel_map[1], speed=0, size=3, spacing=15, step=10)
rainbow_chase2 = RainbowChase(pixel_map[1], speed=0, size=10, spacing=1, step=18)
chase = Chase(pixel_map[1], speed=0.1, color=RED, size=1, spacing=6)
rainbow_comet = RainbowComet(pixel_map[2], speed=0, tail_length=80, bounce=True)
rainbow_comet2 = RainbowComet(
    pixel_map[0], speed=0, tail_length=104, colorwheel_offset=80, bounce=True
    )
rainbow_comet3 = RainbowComet(
    pixel_map[1], speed=0, tail_length=25, colorwheel_offset=80, step=4, bounce=False
    )
strum = RainbowComet(
    pixel_map[2], speed=0, tail_length=25, bounce=False, colorwheel_offset=50, step=4
    )
lava = Comet(pixel_map[1], speed=0.01, color=ORANGE, tail_length=40, bounce=False)
sparkle = Sparkle(pixel_map[2], speed=0.01, color=BLUE, num_sparkles=10)
sparkle2 = Sparkle(pixel_map[1], speed=0.05, color=PURPLE, num_sparkles=4)

# Animations Playlist - reorder as desired. AnimationGroups play at the same time
animations = AnimationSequence(
    rainbow,
    rainbow_chase,
    rainbow_chase2,
    chase,
    lava,
    rainbow_comet,
    rainbow_comet2,
    AnimationGroup(
        sparkle,
        strum,
        ),
    AnimationGroup(
        sparkle2,
        rainbow_comet3,
        ),
    auto_clear=True,
    auto_reset=True,
)

# Re-add the modes - default mode = 0, but I want i = 1
MODE = 0
LASTMODE = 1 # start up in sound reactive mode
i = 1

# Setup the mic
mic = AnalogIn(board.A2)  # set mic input

NUM_SAMPLES = 256
samples_bit = array.array('H', [0] * (NUM_SAMPLES+3))

open_mic = (mic.value, 16)
# Prints mic value of 32608 (32608, 16) which is a float
print(open_mic)

# Main loop
while True:

    time_start = time.monotonic()  # current time used for sample window

    # collect data for length of sample window (in seconds)
    while (time.monotonic() - time_start) < sample_window:

        i = (i + 0.5) % 256  # run from 0 to 255
        TILT_COLOR = colorwheel(i)
        if MODE == 0:  # If currently off...
            # enable.value = True
            power_on(POWER_ON_DURATION)  # Power up!
            MODE = LASTMODE

        elif MODE >= 1:  # If not OFF MODE...
            # Insert Analog mic code below commented out code
            # mic.record(samples_bit, len(samples_bit))
            # mic.record(sample_rate = sample_bit, bit_depth = len(samples_bit))
            # samples_bit = array.array('H', [0] * (NUM_SAMPLES+3))
            # From docs: Records destination_length bytes of 
            # samples to destination. This is blocking.

            # Docs defition of digital recording: 
            # record(self, destination: _typing.WriteableBuffer, destination_length: int) 
            
            # Read the analog mic
            mic_record = mic.value / 64
            open_mic = (mic_record, 16)
            print("Mic :", open_mic)
            
            samples = np.array(open_mic[3:])
            spectrum = spectrogram(samples)
            spectrum = spectrum[:128]
            # Returns 0
            print("Spectrum: ", spectrum, type(spectrum))
            spectrum[0] = 0
            spectrum[1] = 0
            peak_idx = np.argmax(spectrum)
            peak_freq = peak_idx * 16000 / 256
        #        print((peak_idx, peak_freq, spectrum[peak_idx]))
            magnitude = spectrum[peak_idx]
            time.sleep(1)
            # This if / if /elif statement changes it from sound reactive mode to non
            # Should have nothing to do with this code as a specific note on the 
            # ukelele needs to be played
            # Commenting it all out
            # if peak_freq == 812.50 and magnitude > SOUND_THRESHOLD:
            #    animations.next()
            #    time.sleep(1)
            #if peak_freq == 875 and magnitude > SOUND_THRESHOLD:
            #    if MODE == 1:
            #        MODE = 2
            #        print("mode = 2")
            #        LASTMODE = 2
            #        time.sleep(1)
            #    elif MODE == 2:
            #        MODE = 1
            #        print("mode = 1")
            #        LASTMODE = 1
            #        time.sleep(1)
        # Disable accelerometer 
            # x, y, z = sensor.acceleration
            # accel_total = x * x + y * y # x=tilt, y=rotate
        #         print (accel_total)
            i# f accel_total > ROCKSTAR_TILT_THRESHOLD:
                #    MODE = 3
                #   print("Tilted: ", accel_total)
            if MODE == 1:
                VOLUME = magnitude / (VOLUME_CALIBRATOR * 100000)
                if VOLUME > MAX_BRIGHTNESS:
                    VOLUME = MAX_BRIGHTNESS
        #             print(VOLUME)
                pixels.brightness = VOLUME
        #             time.sleep(2)
                animations.animate()
            elif MODE == 2:
                pixels.brightness = NORMAL_BRIGHTNESS
                animations.animate()
            elif MODE == 3:
                rockstar_tilt(ROCKSTAR_TILT_DURATION)
                MODE = LASTMODE
