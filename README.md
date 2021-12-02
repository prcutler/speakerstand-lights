[![Project Type: Toy](https://img.shields.io/badge/project%20type-toy-blue)](https://project-types.github.io/#toy)
[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/prcutler/speakerstand-lights)


# Sound Reactive NeoPixel FeatherWing 

The `speakerstand-lights` project is written in CircuitPython and     uses a [NeoPixel FeatherWing](https://www.adafruit.com/product/3124), an [Adafruit Feather rp2040 Pico](https://learn.adafruit.com/adafruit-feather-rp2040-pico), and a digital microphone breakout board. I used an [I2S mic](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout) and any *digital* mic will work, but not analog. Together, they create a sound reactive spectrogram displayed on the NeoPixel FeatherWing's pixels.

You will need to know the basics of soldering to stack the Feathers and to attach the microphone.

Learn more at the [project homepage](https://paulcutler.org/project/speakerstand-lights/).

### Part 1: CircuitPython Code

Thank you to Adafruit, including Kattni Rembor and Philip Burgess, for the [Adafruit EyeLights LED Glasses Music-Reactive Lights](https://learn.adafruit.com/adafruit-eyelights-led-glasses-and-driver/music-reactive-lights) project.  Better yet, it's released under a MIT license making it easy to modify.  Using this code, I only had to change a few lines to make it work with the NeoPixel FeatherWing!

To use with the Feather rp2040 Pico and a FeatherWing NeoPixel, the code needed to be updated to remove the `LED_Glasses` module and replaced with `PixelFramebuffer` from the `adafruit_pixel_framebuf` module.

Additionally, I reduced the spectrum the microphone listens for as the NeoPixel FeatherWing has less pixels (8x4) than the original code's 13x9 LED matrix.

I commented out the original code and included the original spectrum variables in the comments.  You can play with the variables to find the visualizer you want.

Video never captures LEDs right, but here is an animated gif:

![Audio Reactive NeoPixels](/pictures/neopixel-feather.gif)

### Part Two - 3D Printing a new speaker stand

I will be installing the NeoPixel FeatherWing in an AudioEngine P4 speaker stand which I will be 3D printing (and will add the CAD and STL files to the repository when complete).  This will include a cutout for the NeoPixel FeatherWing on the front and the USB power cable on the back.

Original speaker stands for the P4 / H4 from AudioEngine:

![Original speaker stands for the P4 / H4 from AudioEngine:](/pictures/p4-speakerstand.jpg)

### Thank You and Credits

Thanks again to Adafruit, including Kattni Rembor and Philip Burgess, for the [Adafruit EyeLights LED Glasses Music-Reactive Lights](https://learn.adafruit.com/adafruit-eyelights-led-glasses-and-driver/music-reactive-lights)  -  I only had to change a few lines of code to make this work with a NeoPixel Feather!

I spent hours tearing apart and putting back together the audio code, spectrograms, and more from these Adafruit projects, also open source:

* [FFT Example: Waterfall Spectrum Analyzer](https://learn.adafruit.com/ulab-crunch-numbers-fast-with-circuitpython/overview ) by Jeff Epler

* [Mini LED Matrix Audio Visualizer](https://learn.adafruit.com/mini-led-matrix-audio-visualizer/code-the-mini-led-matrix-audio-visualizer) by Liz Clark

* [Light-Up Reactive Ukulele](https://learn.adafruit.com/light-up-reactive-ukulele) by Erin St Blaine

* CircuitPlayground Sound Meter (which I can't find right now)

* [Adafruit NeoPixel Uberguide](https://learn.adafruit.com/adafruit-neopixel-uberguide) by Phillip Burgess

* [Easy NeoPixel Graphics with the CircuitPython Pixel Framebuf Library](https://learn.adafruit.com/easy-neopixel-graphics-with-the-circuitpython-pixel-framebuf-library) by Melissa LeBlanc-Williams
