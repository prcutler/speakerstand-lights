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

pixel_map_sweep = PixelMap(pixels, [
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
    ], individual_pixels=True)

pixelmap_fw = pixel_map_sweep

# Cusomize LED Animations  ------------------------------------------------------
powerup = RainbowComet(pixelmap_fw, speed=0, tail_length=25, bounce=False)
rainbow = Rainbow(pixelmap_fw, speed=0, period=6, name="rainbow", step=2.4)
rainbow_chase = RainbowChase(pixelmap_fw, speed=0, size=3, spacing=15, step=10)
rainbow_chase2 = RainbowChase(pixelmap_fw, speed=0, size=10, spacing=1, step=18)
chase = Chase(pixelmap_fw, speed=0.1, color=RED, size=1, spacing=6)
rainbow_comet = RainbowComet(pixelmap_fw, speed=0, tail_length=80, bounce=True)
rainbow_comet2 = RainbowComet(
    pixelmap_fw, speed=0, tail_length=104, colorwheel_offset=80, bounce=True
    )
rainbow_comet3 = RainbowComet(
    pixelmap_fw, speed=0, tail_length=25, colorwheel_offset=80, step=4, bounce=False
    )
strum = RainbowComet(
    pixelmap_fw, speed=0, tail_length=25, bounce=False, colorwheel_offset=50, step=4
    )
lava = Comet(pixelmap_fw, speed=0.01, color=ORANGE, tail_length=40, bounce=False)
sparkle = Sparkle(pixelmap_fw, speed=0.01, color=BLUE, num_sparkles=10)
sparkle2 = Sparkle(pixelmap_fw, speed=0.05, color=PURPLE, num_sparkles=4)

# Animations Playlist - reorder as desired. AnimationGroups play at the same time
animations = AnimationSequence(
    # rainbow,
    # rainbow_chase,
    # rainbow_chase2,
    # chase,
    # lava,
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

mic = AnalogIn(board.A2)  # set mic input
NUM_SAMPLES = 256
samples_bit = array.array('H', [0] * (NUM_SAMPLES+3))
duration = float(0.11)

# Main loop
while True:
    # Insert Analog mic code below commented out code
    # mic.record(samples_bit, len(samples_bit))
    # mic.record(sample_rate = sample_bit, bit_depth = len(samples_bit))
    open_mic = (mic.value, 16)
    # print("Mic value: ", open_mic) # Confirmed working 20120809 7:25pm
    # (The mic is live, but no display)
    #samples_bit 16 bit?

    # class audiobusio.PDMIn(clock_pin: microcontroller.Pin, 
    # data_pin: microcontroller.Pin, *, 
    # sample_rate: int = 16000, 
    # bit_depth: int = 8, mono: bool = True, 
    # oversample: int = 64, 
    # startup_delay: float = 0.11)

    # mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK,
    #                  board.MICROPHONE_DATA,
    #                  sample_rate=16000,
    #                   bit_depth=16)

# Insert power_on method from original
    start_time = time.monotonic()  # Save start time

    samples = np.array(samples_bit[3:])
    print("Samples_bit = ",samples_bit, "Samples = ", samples)
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
            VOLUME = magnitude / (VOLUME_CALIBRATOR * 100000)
            if VOLUME > MAX_BRIGHTNESS:
                VOLUME = MAX_BRIGHTNESS
            # Next line probably needs to be changed to framebuf?   
            pixels.brightness = VOLUME
            animations.animate()



