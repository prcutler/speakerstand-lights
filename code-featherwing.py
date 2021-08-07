import array

import board
import neopixel
from analogio import AnalogIn
from adafruit_featherwing import neopixel_featherwing

from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import helper
from adafruit_led_animation.color import PURPLE, JADE, AMBER

# Update to match the pin connected to your NeoPixels
pixel_pin = board.D6
# Update to match the number of NeoPixels you have connected
pixel_num = 32

pixels = neopixel.NeoPixel(pixel_pin, pixel_num, brightness=0.5, auto_write=False)

pixel_wing_vertical = helper.PixelMap.vertical_lines(
    pixels, 8, 4, helper.horizontal_strip_gridmap(8, alternating=False)
)
pixel_wing_horizontal = helper.PixelMap.horizontal_lines(
    pixels, 8, 4, helper.horizontal_strip_gridmap(8, alternating=False)
)


dc_offset = 0  # DC offset in mic signal - if unusure, leave 0
noise = 100  # Noise/hum/interference in mic signal
samples = 60  # Length of buffer for dynamic level adjustment
top = pixel_num + 1  # Allow dot to go slightly off scale

peak = 0  # Used for falling dot
dot_count = 0  # Frame counter for delaying dot-falling speed
vol_count = 0  # Frame counter for storing past volume data

lvl = 10  # Current "dampened" audio level
min_level_avg = 0  # For dynamic adjustment of graph low & high
max_level_avg = 512

# Collection of prior volume samples
vol = array.array("H", [0] * samples)

mic_pin = AnalogIn(board.A2)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0) or (pos > 255):
        return (0, 0, 0)
    if pos < 85:
        return (int(pos * 3), int(255 - (pos * 3)), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    pos -= 170
    return (0, int(pos * 3), int(255 - pos * 3))


def remap_range(value, leftMin, leftMax, rightMin, rightMax):
    # this remaps a value from original (left) range to new (right) range
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (int)
    valueScaled = int(value - leftMin) / int(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))


while True:
    n = int((mic_pin.value / 65536) * 1000)  # 10-bit ADC format
    n = abs(n - 512 - dc_offset)  # Center on zero

    if n >= noise:  # Remove noise/hum
        n = n - noise

    # "Dampened" reading (else looks twitchy) - divide by 8 (2^3)
    lvl = int(((lvl * 7) + n) / 8)

    # Calculate bar height based on dynamic min/max levels (fixed point):
    height = top * (lvl - min_level_avg) / (max_level_avg - min_level_avg)

    # Clip output
    if height < 0:
        height = 0
    elif height > top:
        height = top

    # Keep 'peak' dot at top
    if height > peak:
        peak = height

        # Color pixels based on rainbow gradient
    for i in range(0, 32):
        if i >= height:
            pixels[i] = [0, 0, 0]
        else:
            pixels[i] = wheel(remap_range(i, 0, (pixel_num - 1), 30, 150))

    # Save sample for dynamic leveling
    vol[vol_count] = n

    # Advance/rollover sample counter
    vol_count += 1

    if vol_count >= samples:
        vol_count = 0

        # Get volume range of prior frames
    min_level = vol[0]
    max_level = vol[0]

    for i in range(1, len(vol)):
        if vol[i] < min_level:
            min_level = vol[i]
        elif vol[i] > max_level:
            max_level = vol[i]

    # minlvl and maxlvl indicate the volume range over prior frames, used
    # for vertically scaling the output graph (so it looks interesting
    # regardless of volume level).  If they're too close together though
    # (e.g. at very low volume levels) the graph becomes super coarse
    # and 'jumpy'...so keep some minimum distance between them (this
    # also lets the graph go to zero when no sound is playing):
    if (max_level - min_level) < top:
        max_level = min_level + top

    # Dampen min/max levels - divide by 64 (2^6)
    min_level_avg = (min_level_avg * 63 + min_level) >> 6
    # fake rolling average - divide by 64 (2^6)
    max_level_avg = (max_level_avg * 63 + max_level) >> 6

    print(n)
