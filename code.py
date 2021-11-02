"""AUDIO SPECTRUM LIGHT SHOW for Adafruit EyeLights (LED Glasses + Driver). 
From https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/EyeLights_Audio_Spectrum/code.py 
"""

import array import array
from math import log
import board
import neopixel
from audiobusio import PDMIn
from ulab import numpy as np
from ulab.scipy.signal import spectrogram
from supervisor import reload
from rainbowio import colorwheel


# Digital Audio 
import audiocore
import audiobusio

# Import PixelFramebuffer
# import helper
from adafruit_pixel_framebuf import PixelFramebuffer
from adafruit_led_animation.helper import PixelMap

# Import from featherwing example
from adafruit_led_animation import helper


# FFT/SPECTRUM CONFIG ----

fft_size = 256  # Sample size for Fourier transform, MUST be power of two
spectrum_size = fft_size // 2  # Output spectrum is 1/2 of FFT result
# Bottom of spectrum tends to be noisy, while top often exceeds musical
# range and is just harmonics, so clip both ends off:
low_bin = 10  # Lowest bin of spectrum that contributes to graph
high_bin = 75  # Highest bin "

# Set NeoPixel
pixel_pin = board.D6  # NeoPixel LED strand is connected to GPIO #0 / D0
n_pixels = 32  # Number of pixels you are using


# Add Neopixel Featherwing vertical and horizontal functions
pixel_width = 8
pixel_height = 4

pixels = neopixel.NeoPixel(
    pixel_pin,
    pixel_width * pixel_height,
    brightness=0.1,
    auto_write=False,
)

pixel_framebuf = PixelFramebuffer(
    pixels,
    pixel_width,
    pixel_height,
    brightness=0.1,
    alternating=False,
)


# Set up digial mic
mic = audiobusio.PDMIn(board.D10, board.D9,
                       sample_rate=16000, bit_depth=16)

# FFT/SPECTRUM SETUP -----

# To keep the display lively, tables are precomputed where each column of
# the matrix (of which there are few) is the sum value and weighting of
# several bins from the FFT spectrum output (of which there are many).
# The tables also help visually linearize the output so octaves are evenly
# spaced, as on a piano keyboard, whereas the source spectrum data is
# spaced by frequency in Hz.
column_table = []

spectrum_bits = log(spectrum_size, 2)  # e.g. 7 for 128-bin spectrum
# Scale low_bin and high_bin to 0.0 to 1.0 equivalent range in spectrum
low_frac = log(low_bin, 2) / spectrum_bits
frac_range = log(high_bin, 2) / spectrum_bits - low_frac

for column in range(pixel_width):
    # Determine the lower and upper frequency range for this column, as
    # fractions within the scaled 0.0 to 1.0 spectrum range. 0.95 below
    # creates slight frequency overlap between columns, looks nicer.
    lower = low_frac + frac_range * (column / pixel_width * 0.95)
    upper = low_frac + frac_range * ((column + 1) / pixel_width)
    mid = (lower + upper) * 0.5  # Center of lower-to-upper range
    half_width = (upper - lower) * 0.5  # 1/2 of lower-to-upper range
    # Map fractions back to spectrum bin indices that contribute to column
    first_bin = int(2 ** (spectrum_bits * lower) + 1e-4)
    last_bin = int(2 ** (spectrum_bits * upper) + 1e-4)
    bin_weights = []  # Each spectrum bin's weighting will be added here
    for bin_index in range(first_bin, last_bin + 1):
        # Find distance from column's overall center to individual bin's
        # center, expressed as 0.0 (bin at center) to 1.0 (bin at limit of
        # lower-to-upper range).
        bin_center = log(bin_index + 0.5, 2) / spectrum_bits
        dist = abs(bin_center - mid) / half_width
        if dist < 1.0:  # Filter out a few math stragglers at either end
            # Bin weights have a cubic falloff curve within range:
            dist = 1.0 - dist  # Invert dist so 1.0 is at center
            bin_weights.append(((3.0 - (dist * 2.0)) * dist) * dist)
    # Scale bin weights so total is 1.0 for each column, but then mute
    # lower columns slightly and boost higher columns. It graphs better.
    total = sum(bin_weights)
    bin_weights = [
        (weight / total) * (0.8 + idx / pixel_width * 1.4)
        for idx, weight in enumerate(bin_weights)