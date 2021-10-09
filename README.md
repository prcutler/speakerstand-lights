# Sound Reactive NeoPixel FeatherWing 

The `cp-spakerstand-lights` project is written in CircuitPython and     uses the [NeoPixel FeatherWing](https://www.adafruit.com/product/3124), rp2040 Feather, and a digital microphone breakout board. Together, they create a sound reactive spectrogram displayed on the NeoPixel FeatherWing.

I can't take credit for probably 90% of the code, it was adapted from these two projects, especially the second one:

* Adapted from the [FFT Example: Waterfall Spectrum Analyzer](https://learn.adafruit.com/ulab-crunch-numbers-fast-with-circuitpython/overview ) by Jeff Epler

* Also adapted from [Mini LED Matrix Audio Visualizer](https://learn.adafruit.com/mini-led-matrix-audio-visualizer/code-the-mini-led-matrix-audio-visualizer) by Liz Clark

I will be installing the NeoPixel FeatherWing in AudioEngine P4 speaker stands which I will be 3D printing (and will add the CAD and STL files here when complete).  This will include a cutout for the NeoPixel FeatherWing on the front and the USB power cable on the back.

The code works with the NeoPixels reacting to volume, but it needs to be tweaked to lower the ceiling and raise the floor of how far the pixels move.  The included code was originally written for a 13x9 matrix and I'm using a 4x8 matrix via the `adafruit_pixel_framebuf` library.

AudioEngine P4 speaker on its stand with the NeoPixel FeatherWing:

![AudioEngine P4 speaker on its stand with the NeoPixel FeatherWing](/pictures/speaker-feather.png)

Original speaker stands for the P4 / H4 from AudioEngine:

![Original speaker stands for the P4 / H4 from AudioEngine:](/pictures/p4-speakerstand.jpg)



