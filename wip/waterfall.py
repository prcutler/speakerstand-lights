"""Waterfall FFT demo adapted from
https://teaandtechtime.com/fft-circuitpython-library/
to work with ulab on Adafruit CLUE"""

import array

import board
import audiobusio
from displayio import Palette

# Remove display io and add neopixel
# import displayio
import neopixel

from ulab import numpy as np
from ulab.scipy.signal import spectrogram

# Add AnalogIn
from analogio import AnalogIn

# Add adafruit_framebuf for Featherwing NeoPixels
from rainbowio import colorwheel as wheel
from ulab import numpy as np
# from adafruit_matrixportal.matrix import Matrix

# Disable displayio methods and use neopixel instead
# group = displayio.Group()  # Create a Group
# bitmap = displayio.Bitmap(8, 4, 2)  # Create a bitmap object,width, height, bit depth

COLUMNS = 8
ROWS = 4

pixels = neopixel.NeoPixel(board.D6, 32, brightness=0.3)

# Create a heatmap color palette
# palette = displayio.Palette(52)

palette = [0xffc800, 0xffd200, 0xffdc00, 0xffe600,
                        0xfff000, 0xfffa00, 0xfdff00, 0xd7ff00,
                        0xb0ff00, 0x8aff00, 0x65ff00, 0x3eff00,
                        0x17ff00, 0x00ff10, 0x00ff36, 0x00ff5c,
                        0x00ff83, 0x00ffa8, 0x00ffd0, 0x00fff4,
                        0x00a4ff, 0x0094ff, 0x0084ff, 0x0074ff,
                        0x0064ff, 0x0054ff, 0x0044ff, 0x0032ff,
                        0x0022ff, 0x0012ff, 0x0002ff, 0x0000ff]

for i, pi in enumerate(palette):
    palette[31 - i] = pi

# I think this creates the first 3 columns of the graph and then moves it right
class RollingGraph(pixels):
    def __init__(self, scale=2):
        # Create a bitmap with heatmap colors
        self.bitmap = pixels.Bitmap(
            pixels.width // scale, pixels.height // scale, len(palette)
        )
        super().__init__(self.bitmap, pixel_shader=palette)

        self.scroll_offset = 0

    def show(self, data):
        y = self.scroll_offset
        bitmap = self.bitmap

        board.DISPLAY.auto_refresh = False
        offset = max(0, (bitmap.width - len(data)) // 2)
        for x in range(min(bitmap.width, len(data))):
            bitmap[x + offset, y] = int(data[x])

        board.DISPLAY.auto_refresh = True

        self.scroll_offset = (y + 1) % self.bitmap.height


group = pixels.group(scale=3)
graph = RollingGraph(3)
fft_size = 256

# Add the TileGrid to the Group
group.append(graph)

# Add the Group to the Display
pixels.show(group)

# instantiate board mic
# mic = audiobusio.PDMIn(
#    board.MICROPHONE_CLOCK, board.MICROPHONE_DATA, sample_rate=16000, bit_depth=16
# )

# Use analog mic
mic = AnalogIn(board.A2)

# use some extra sample to account for the mic startup
samples_bit = array.array("H", [0] * (fft_size + 3))

# Main Loop
def main():
    max_all = 10

    while True:
        # Comment out the PDM mic
        # mic.record(samples_bit, len(samples_bit))

        # Use analog mic instead - Start pendant code insert:
        n = int((mic.value / 65536) * 1000)  # 10-bit ADC format
        n = abs(n - 512)  # Center on zero

        if n >= noise:  # Remove noise/hum
            n = n - noise

        # "Dampened" reading (else looks twitchy) - divide by 8 (2^3)
        lvl = int(((lvl * 7) + n) / 8)

        # End pendant code

        # Slicing from the 3: eliminates line 122?

        # Original samples:
        # samples = np.array(samples_bit[3:])

        # Modified samples - use lvl, which should be incoming mic level
        samples = np.array(lvl)

        spectrogram1 = spectrogram(samples)
        # spectrum() is always nonnegative, but add a tiny value
        # to change any zeros to nonzero numbers
        spectrogram1 = np.log(spectrogram1 + 1e-7)
        spectrogram1 = spectrogram1[1 : (fft_size // 2) - 1]
        min_curr = np.min(spectrogram1)
        max_curr = np.max(spectrogram1)

        if max_curr > max_all:
            max_all = max_curr
        else:
            max_curr = max_curr - 1

        print(min_curr, max_all)
        min_curr = max(min_curr, 3)
        # Plot FFT
        data = (spectrogram1 - min_curr) * (51.0 / (max_all - min_curr))
        # This clamps any negative numbers to zero
        data = data * np.array((data > 0))
        pixels.show(data)


main()
