# Minimal hardware test for the Waveshare Pico-ePaper-4.2.
# Upload this file together with epd4in2.py, then run it from Thonny.

import framebuf
import time
from epd4in2 import EPD4in2, EPD_WIDTH, EPD_HEIGHT


def main():
    epd = EPD4in2()
    print("BUSY before init:", epd.busy_pin.value(), "(0 means idle)")
    print("Detecting and initialising display controller...")
    epd.init()
    print("Detected controller:", "V2" if epd.is_v2 else "legacy B")
    print("BUSY after init:", epd.busy_pin.value(), "(0 means idle)")

    image = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)
    canvas = framebuf.FrameBuffer(image, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)
    canvas.fill(1)
    canvas.rect(0, 0, EPD_WIDTH, EPD_HEIGHT, 0)
    canvas.fill_rect(20, 20, 360, 80, 0)
    canvas.text("Pico-ePaper-4.2", 120, 45, 1)
    canvas.text("DISPLAY TEST", 145, 75, 1)
    canvas.text("If you can read this, it works.", 72, 150, 0)

    print("Starting full refresh; the display should flicker for about 4 seconds...")
    epd.display(image)
    print("Display test completed.")
    time.sleep(1)


main()
