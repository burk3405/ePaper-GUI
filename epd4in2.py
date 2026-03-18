# epd4in2.py
# Minimal MicroPython driver for Waveshare 4.2" B/W ePaper (400x300).
# Designed for Raspberry Pi Pico / Pico W.

from machine import Pin, SPI
import time

EPD_WIDTH = 400
EPD_HEIGHT = 300

# Command constants (subset)
PANEL_SETTING            = 0x00
POWER_SETTING            = 0x01
POWER_ON                 = 0x04
BOOSTER_SOFT_START       = 0x06
DATA_START_TRANSMISSION_1 = 0x10
DISPLAY_REFRESH          = 0x12
PARTIAL_IN               = 0x91
PARTIAL_WINDOW           = 0x90
VCOM_AND_DATA_INTERVAL   = 0x50
TCON_RESOLUTION          = 0x61
VCM_DC_SETTING           = 0x82
POWER_OFF                = 0x02
DEEP_SLEEP               = 0x07

class EPD4in2:
    def __init__(self, sck=2, mosi=3, cs=5, dc=4, rst=6, busy=7):
        self.reset_pin = Pin(rst, Pin.OUT)
        self.dc_pin = Pin(dc, Pin.OUT)
        self.busy_pin = Pin(busy, Pin.IN)
        self.cs_pin = Pin(cs, Pin.OUT)

        self.spi = SPI(0, baudrate=2000000, polarity=0, phase=0,
                       sck=Pin(sck), mosi=Pin(mosi), miso=None)

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, ms):
        time.sleep_ms(ms)

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray([command]))
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.digital_write(self.cs_pin, 1)

    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)

    def wait_until_idle(self):
        while self.digital_read(self.busy_pin) == 0:
            self.delay_ms(50)

    def init(self):
        self.reset()

        self.send_command(POWER_SETTING)
        self.send_data(0x03)
        self.send_data(0x00)
        self.send_data(0x2B)
        self.send_data(0x2B)
        self.send_data(0x09)

        self.send_command(BOOSTER_SOFT_START)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x17)

        self.send_command(POWER_ON)
        self.wait_until_idle()

        self.send_command(PANEL_SETTING)
        self.send_data(0x0F)  # KW-BF   KWR-AF  BWROTP 0f

        self.send_command(VCOM_AND_DATA_INTERVAL)
        self.send_data(0xF7)

        self.send_command(TCON_RESOLUTION)
        self.send_data(self.width >> 8)
        self.send_data(self.width & 0xFF)
        self.send_data(self.height >> 8)
        self.send_data(self.height & 0xFF)

        self.send_command(VCM_DC_SETTING)
        self.send_data(0x0E)

    def clear(self, color=0xFF):
        self.send_command(DATA_START_TRANSMISSION_1)
        self.delay_ms(2)
        buf = bytearray([color]) * (self.width * self.height // 8)
        self.send_data(buf)
        self.delay_ms(2)
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def display(self, image):
        # image: bytearray of size width*height/8, 0=black,1=white (inverted here)
        self.send_command(DATA_START_TRANSMISSION_1)
        self.delay_ms(2)
        self.send_data(image)
        self.delay_ms(2)
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def display_partial(self, image, x, y, w, h):
        # Simple partial update wrapper.
        # Many 4.2" panels support partial; here we use a basic windowed update.
        # For safety, you can fall back to full display if partial misbehaves.
        if (x % 8) != 0:
            x = x - (x % 8)  # align to byte boundary

        self.send_command(PARTIAL_IN)
        self.send_command(PARTIAL_WINDOW)
        self.send_data(x >> 8)
        self.send_data(x & 0xF8)
        self.send_data((x + w - 1) >> 8)
        self.send_data((x + w - 1) | 0x07)
        self.send_data(y >> 8)
        self.send_data(y & 0xFF)
        self.send_data((y + h - 1) >> 8)
        self.send_data((y + h - 1) & 0xFF)
        self.send_data(0x01)  # Gates scan both inside and outside of the window

        self.send_command(DATA_START_TRANSMISSION_1)
        self.send_data(image)
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def sleep(self):
        self.send_command(POWER_OFF)
        self.wait_until_idle()
        self.send_command(DEEP_SLEEP)
        self.send_data(0xA5)
