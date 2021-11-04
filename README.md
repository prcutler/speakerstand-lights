# Sound Reactive NeoPixel FeatherWing 

The `speakerstand-lights` project is written in CircuitPython and     uses a [NeoPixel FeatherWing](https://www.adafruit.com/product/3124), an [Adafruit rp2040 Pico Feather](https://learn.adafruit.com/adafruit-feather-rp2040-pico), and a digital microphone breakout board I used an [I2S mic](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout) and any *digital* mic will work, but not analog. Together, they create a sound reactive spectrogram displayed on the NeoPixel FeatherWing's pixels.

### Part 1: CircuitPython Code

Thank you to Adafruit, including Kattni Rembor and Philip Burgess, for the [Adafruit EyeLights LED Glasses Music-Reactive Lights](https://learn.adafruit.com/adafruit-eyelights-led-glasses-and-driver/music-reactive-lights) project.  Better yet, it's released under a MIT license making it easy to modify.

To use with the Feather rp2040 Pico and a FeatherWing NeoPixel, the code needed to be updated to remove the `LED_Glasses` module and replaced with `PixelFramebuffer` from the `adafruit_pixel_framebuf` module.

Additionally, I reduced the spectrum the microphone listens for as the NeoPixel FeatherWing has less pixels (8x4) than the original code's 13x9 LED matrix.

I commented out the original code and included the original spectrum variables in the comments.

Video never captures LEDs right, but here is an animated gif:

![Audio Reactive NeoPixels](/pictures/neopixel-feather.gif)

### Part Two - 3D Printing a new speaker stand

I will be installing the NeoPixel FeatherWing in AudioEngine P4 speaker stands which I will be 3D printing (and will add the CAD and STL files here when complete).  This will include a cutout for the NeoPixel FeatherWing on the front and the USB power cable on the back.

AudioEngine P4 speaker on its stand with the NeoPixel FeatherWing:

![AudioEngine P4 speaker on its stand with the NeoPixel FeatherWing](/pictures/speaker-feather.png)

Original speaker stands for the P4 / H4 from AudioEngine:

![Original speaker stands for the P4 / H4 from AudioEngine:](/pictures/p4-speakerstand.jpg)

### Thank You and Credits

* Adapted from the [FFT Example: Waterfall Spectrum Analyzer](https://learn.adafruit.com/ulab-crunch-numbers-fast-with-circuitpython/overview ) by Jeff Epler

* Also adapted from [Mini LED Matrix Audio Visualizer](https://learn.adafruit.com/mini-led-matrix-audio-visualizer/code-the-mini-led-matrix-audio-visualizer) by Liz Clark

* Adapted from the [FFT Example: Waterfall Spectrum Analyzer](https://learn.adafruit.com/ulab-crunch-numbers-fast-with-circuitpython/overview ) by Jeff Epler

* Also adapted from [Mini LED Matrix Audio Visualizer](https://learn.adafruit.com/mini-led-matrix-audio-visualizer/code-the-mini-led-matrix-audio-visualizer) by Liz Clark
