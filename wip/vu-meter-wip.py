# LED VU meter for Arduino and Adafruit NeoPixel LEDs.

# Hardware requirements:
# - M0 boards
# - Adafruit Electret Microphone Amplifier (ID: 1063)
# - Adafruit Flora RGB Smart Pixels (ID: 1260)
# OR
# - Adafruit NeoPixel Digital LED strip (ID: 1138)
# - Optional: battery for portable use (else power through USB or adapter)
# Software requirements:
# - Adafruit NeoPixel library

# Connections:
# - 3.3V to mic amp +
# - GND to mic amp -
# - Analog pin to microphone output (configurable below)
# - Digital pin to LED data input (configurable below)
# See notes in setup() regarding 5V vs. 3.3V boards - there may be an
# extra connection to make and one line of code to enable or disable.

# Written by Adafruit Industries.  Distributed under the BSD license.
# This paragraph must be included in any redistribution.

# fscale function:
# Floating Point Autoscale Function V0.1
# Written by Paul Badger 2007
# Modified fromhere code by Greg Shakar
# Ported to Circuit Python by Mikey Sklar

# Code runs but no lights
# TODO: Try vertical lines of 4 pixes

import time

import board
import neopixel
from analogio import AnalogIn

# Import from featherwing example
from adafruit_led_animation import helper

# Import PixelFramebuffer
from adafruit_pixel_framebuf import PixelFramebuffer
from adafruit_led_animation.helper import PixelMap

# n_pixels = 32  # Number of pixels you are using
mic_pin = AnalogIn(board.A2)  # Microphone is attached to this analog pin
led_pin = board.D6  # NeoPixel LED strand is connected to this pin
sample_window = 0.1  # Sample window for average level
peak_hang = 24  # Time of pause before peak dot falls
peak_fall = 4  # Rate of falling peak dot
input_floor = 10  # Lower range of analogRead input
# Max range of analogRead input, the lower the value the more sensitive
# (1023 = max)
input_ceiling = 300

peak = 4  # Peak level of column; used for falling dots
sample = 0

dotcount = 0  # Frame counter for peak dot
dothangcount = 0  # Frame counter for holding peak dot

# strip = neopixel.NeoPixel(led_pin, n_pixels, brightness=0.1, auto_write=False)

# Add Neopixel Featherwing vertical and horizontal functions

pixel_width = 8
pixel_height = 4

pixels = neopixel.NeoPixel(
    led_pin,
    pixel_width * pixel_height,
    brightness=0.1,
    auto_write=False,
)

pixel_framebuf = PixelFramebuffer(
    pixels,
    pixel_width,
    pixel_height,
    alternating=False,
)

# Was pixel_map_around (I think that's the sound reactive one) in ukulele
pixel_map_around = PixelMap(pixels.n,[
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
    ], individual_pixels=True)

# Was Bottom up along both sides at once
pixel_map_reverse = PixelMap(pixels.n,[
    31, 30, 29, 28, 27, 26, 25, 24,
    23, 22, 21, 20, 19, 18, 17, 16,
    15, 14, 13, 12, 11, 10, 9, 8,
    7, 6, 5, 4, 3, 2, 1, 0,
    ], individual_pixels=True)

#Was Every other pixel, starting at the bottom and going upwards along both sides
pixel_map_skip = PixelMap(pixels.n,[
    0, 2, 4, 6, 
    8, 10, 12, 14,
    16, 18, 20, 22,
    24, 26, 28, 30,
    ], individual_pixels=True)

pixel_map = [pixel_map_around, pixel_map_reverse, pixel_map_skip]

# Can we use this to iterate pixels going across horizontally?
pm_col_list = [
    0, 1, 2, 3, 4, 5, 6, 7
]



def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (int(pos * 3), int(255 - (pos * 3)), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))


def remapRange(value, leftMin, leftMax, rightMin, rightMax):
    # this remaps a value fromhere original (left) range to new (right) range
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (int)
    valueScaled = int(value - leftMin) / int(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))


def fscale(originalmin, originalmax, newbegin, newend, inputvalue, curve):
    invflag = 0

    # condition curve parameter
    # limit range
    if curve > 10:
        curve = 10
    if curve < -10:
        curve = -10

    # - invert and scale -
    # this seems more intuitive
    # postive numbers give more weight to high end on output
    curve = curve * -0.1
    # convert linear scale into lograthimic exponent for other pow function
    curve = pow(10, curve)

    # Check for out of range inputValues
    if inputvalue < originalmin:
        inputvalue = originalmin

    if inputvalue > originalmax:
        inputvalue = originalmax

    # Zero Refference the values
    originalrange = originalmax - originalmin

    if newend > newbegin:
        newrange = newend - newbegin
    else:
        newrange = newbegin - newend
        invflag = 1

    zerorefcurval = inputvalue - originalmin
    # normalize to 0 - 1 float
    normalizedcurval = zerorefcurval / originalrange

    # Check for originalMin > originalMax
    # -the math for all other cases
    # i.e. negative numbers seems to work out fine
    if originalmin > originalmax:
        return 0

    if invflag == 0:
        rangedvalue = (pow(normalizedcurval, curve) * newrange) + newbegin
    else:  # invert the ranges
        rangedvalue = newbegin - (pow(normalizedcurval, curve) * newrange)

    return rangedvalue

# Comment out drawLine and replace with pixel_framebuf.line
def drawLine(fromhere, to):
    if fromhere > to:
        fromheretemp = fromhere
        fromhere = to
        to = fromheretemp

    for index in range(fromhere, to):
        pm_col_list[index](0, 0, pixel_width - 1, pixel_height - 1, 0x000000)
        pixel_framebuf.display

while True:

    time_start = time.monotonic()  # current time used for sample window
    peaktopeak = 0  # peak-to-peak level
    signalmax = 0
    signalmin = 1023
    c = 0
    y = 0

    # collect data for length of sample window (in seconds)
    while (time.monotonic() - time_start) < sample_window:

        # convert to arduino 10-bit [1024] fromhere 16-bit [65536]
        sample = mic_pin.value / 64

        if sample < 1024:  # toss out spurious readings

            if sample > signalmax:
                signalmax = sample  # save just the max levels
            elif sample < signalmin:
                signalmin = sample  # save just the min levels

    peaktopeak = signalmax - signalmin  # max - min = peak-peak amplitude

    # Fill the strip with rainbow gradient
    # Change to use the pixel_map columns
    for i in range(0, pixel_width):
        pm_col_list[i] = wheel(remapRange(i, 0, (pixel_height - 1), 30, 150))
        pixel_framebuf.display()
        # print(strip[i])

    # Scale the input logarithmically instead of linearly
    # Replace n_pixels with pixel_height through end of file
    c = fscale(input_floor, input_ceiling, (pixel_height - 1), 0, peaktopeak, 2)

    if c < peak:
        peak = c  # keep dot on top
        dothangcount = 0  # make the dot hang before falling

       # pixel_framebuf.line takes 6 positional arguments 
       # adafruit_pixel_framebuf.PixelFramebuffer(pixels, width, height, 
       # orientation=1, alternating=True, reverse_x=False, 
       # reverse_y=False, top=0, bottom=0, rotation=0)
        
        # pixel_framebuf.line(0, 0, pixel_width - 1, pixel_height - 1, 0x00FF00)

    if c <= pixel_height:  # fill partial column with off pixels
        # Need to pass 6 positional arguments (the correct ones)
        pixel_framebuf.line()
        pixel_framebuf.display()

    # Set the peak dot to match the rainbow gradient
    #y = pixel_height - peak
    #pixel_framebuf.fill(
    #    y - 1,
    #    wheel(remapRange(y, 0, (pixel_height - 1), 30, 150)),
    #)
    #pixel_framebuf.display()

    # Frame based peak dot animation
    if dothangcount > peak_hang:  # Peak pause length
        dotcount += 1
        if dotcount >= peak_fall:  # Fall rate
            peak += 1
            dotcount = 0
    else:
        dothangcount += 1
    print(c)