import board
import neopixel
import time
import audiobusio
import displayio
import random
import digitalio
import array
from teaandtechtime_fft import spectrogram, fft, ifft
from math import sin, pi

# Add AnalogIn
from analogio import AnalogIn

display = board.DISPLAY

# Create a bitmap with heatmap colors
bitmap = displayio.Bitmap(8, 4, 32)

# Create a heatmap color palette
palette = displayio.Palette(32)
palette[55] = 0xFF0000
palette[54] = 0xFF0A00
palette[53] = 0xFF1400
palette[52] = 0xFF1E00
palette[51] = 0xFF2800
palette[50] = 0xFF3200
palette[49] = 0xFF3C00
palette[48] = 0xFF4600
palette[47] = 0xFF5000
palette[46] = 0xFF5A00
palette[45] = 0xFF6400
palette[44] = 0xFF6E00
palette[43] = 0xFF7800
palette[42] = 0xFF8200
palette[41] = 0xFF8C00
palette[40] = 0xFF9600
palette[39] = 0xFFA000
palette[38] = 0xFFAA00
palette[37] = 0xFFB400
palette[36] = 0xFFBE00
palette[35] = 0xFFC800
palette[34] = 0xFFD200
palette[33] = 0xFFDC00
palette[32] = 0xFFE600
palette[31] = 0xFFF000
palette[30] = 0xFFFA00
palette[29] = 0xFDFF00
palette[28] = 0xD7FF00
palette[27] = 0xB0FF00
palette[26] = 0x8AFF00
palette[25] = 0x65FF00
palette[24] = 0x3EFF00
palette[23] = 0x17FF00
palette[22] = 0x00FF10
palette[21] = 0x00FF36
palette[20] = 0x00FF5C
palette[19] = 0x00FF83
palette[18] = 0x00FFA8
palette[17] = 0x00FFD0
palette[16] = 0x00FFF4
palette[15] = 0x00E4FF
palette[14] = 0x00D4FF
palette[13] = 0x00C4FF
palette[12] = 0x00B4FF
palette[11] = 0x00A4FF
palette[10] = 0x0094FF
palette[9] = 0x0084FF
palette[8] = 0x0074FF
palette[7] = 0x0064FF
palette[6] = 0x0054FF
palette[5] = 0x0044FF
palette[4] = 0x0032FF
palette[3] = 0x0022FF
palette[2] = 0x0012FF
palette[1] = 0x0002FF
palette[0] = 0x0000FF


# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(
    bitmap,
    pixel_shader=palette,
    width=1,
    height=display.height,
    tile_width=display.width,
    tile_height=1,
)

# Create a Group
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)

# Add the Group to the Display
display.show(group)

# instantiate board mic
# mic = audiobusio.PDMIn(board.D1, board.D12, sample_rate=16000, bit_depth=16)

# Use analog mic
mic = AnalogIn(board.A2)

# assign the fft size we want to use
fft_size = 256
# use some extra sample to account for the mic startup
samples_bit = array.array("H", [0] * (fft_size + 3))

# Uncomment this code to test the fft library
"""
#create basic data structure to hold samples
samples = array.array('f', [0] * fft_size)

#assign a sinusoid to the samples
frequency = 63  # Set this to the Hz of the tone you want to generate.
for i in range(fft_size):
    samples[i] = sin(pi * 2 * i / (fft_size/frequency))

#create complex samples
test_complex_samples = []
for n in range(fft_size):
    test_complex_samples.append(((float(samples[n]))-1 + 0.0j))

#compute fft of complex samples
test_fft = fft(test_complex_samples)

#compute ifft of the fft values
test_ifft = ifft(test_fft)

#print computed values for testing and verification
#print complex samples
print("samples")
for i in test_complex_samples:
    print(i)
    time.sleep(.01)

#print fft values
print("fft")
for i in test_fft:
    print(i)
    time.sleep(.01)

#print ifft values
print("ifft")
for i in test_ifft:
    print(i)
    time.sleep(.01)

#compute absolut value of the error per sample
print("error")
sum = 0
for i in range(fft_size):
    sum = sum + abs(test_ifft[i] - test_complex_samples[i])

print(sum)
"""

# Main Loop
i = 0
max_all = 1

while True:
    # Draw even more pixels
    for y in range(display.height):
        # Add Analog mic recording
        sample = mic.value / 64
        # mic.record(samples_bit, len(samples_bit))
        complex_samples = []
        for n in range(fft_size):
            complex_samples.append((float(samples_bit[n + 3]) / 32768.0) + 0.0j)
        # compute spectrogram
        spectrogram1 = spectrogram(complex_samples)
        spectrogram1 = spectrogram1[1 : (fft_size // 2) - 1]
        min_curr = abs(min(spectrogram1))
        max_curr = max(spectrogram1) + min_curr

        if max_curr > max_all:
            max_all = max_curr
        else:
            max_curr = max_curr - 1

        # Slide tile window
        for line in range(display.height):
            tile_grid[line] = (display.height - y - 1 + line) % display.height

        # Plot FFT
        offset = (display.width - len(spectrogram1)) // 2
        for x in range(len(spectrogram1)):
            bitmap[x + offset, display.height - y - 1] = int(
                ((spectrogram1[x] + min_curr) / (max_all)) * 55
            )
