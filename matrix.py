'''Adapted from the FFT Example: Waterfall Spectrum Analyzer
by Jeff Epler
https://learn.adafruit.com/ulab-crunch-numbers-fast-with-circuitpython/overview '''

'''Also adapted from Mini LED Matrix Audio Visualizer by Liz Clark
https://learn.adafruit.com/mini-led-matrix-audio-visualizer/code-the-mini-led-matrix-audio-visualizer '''

import array
import board
import neopixel
from analogio import AnalogIn
import busio
from ulab import numpy as np
from ulab.scipy.signal import spectrogram


# This seems harder to get to max volume than vu-meter

led_pin = board.D6  # NeoPixel LED strand is connected to GPIO #0 / D0
n_pixels = 32  # Number of pixels you are using
dc_offset = 0  # DC offset in mic signal - if unusure, leave 0
noise = 100  # Noise/hum/interference in mic signal
samples = 60  # Length of buffer for dynamic level adjustment
top = n_pixels + 1  # Allow dot to go slightly off scale

peak = 0  # Used for falling dot
dot_count = 0  # Frame counter for delaying dot-falling speed
vol_count = 0  # Frame counter for storing past volume data

lvl = 10  # Current "dampened" audio level
min_level_avg = 0  # For dynamic adjustment of graph low & high
max_level_avg = 512

# Collection of prior volume samples
vol = array.array("H", [0] * samples)

mic_pin = AnalogIn(board.A2)

strip = neopixel.NeoPixel(led_pin, n_pixels, brightness=0.1, auto_write=True)