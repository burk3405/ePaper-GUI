# MicroPython driver for the Waveshare Pico-ePaper-4.2 (400x300, B/W).
# This board uses a UC8176 controller and the Pico's SPI1 pin assignment.

from machine import Pin, SPI
import time

EPD_WIDTH = 400
EPD_HEIGHT = 300

# Wired directly by the Pico-ePaper-4.2 board / its supplied 8-pin cable.
SCK_PIN = 10
MOSI_PIN = 11
CS_PIN = 9
DC_PIN = 8
RST_PIN = 12
BUSY_PIN = 13

POWER_SETTING = 0x01
POWER_OFF = 0x02
POWER_ON = 0x04
BOOSTER_SOFT_START = 0x06
DEEP_SLEEP = 0x07
DATA_START_TRANSMISSION_1 = 0x10
DATA_START_TRANSMISSION_2 = 0x13
DISPLAY_REFRESH = 0x12
PANEL_SETTING = 0x00
PLL_CONTROL = 0x30
VCOM_AND_DATA_INTERVAL = 0x50
TCON_RESOLUTION = 0x61
VCM_DC_SETTING = 0x82

# The display's full-refresh waveform tables. The controller needs these
# tables loaded before it can perform a reliable B/W refresh.
LUT_VCOM = (
    0x00, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x00, 0x0F, 0x0F, 0x00, 0x00, 0x01,
    0x00, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
)
LUT_WW = (
    0x50, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x90, 0x0F, 0x0F, 0x00, 0x00, 0x01,
    0xA0, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
)
LUT_BW = (
    0x50, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x90, 0x0F, 0x0F, 0x00, 0x00, 0x01,
    0xA0, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
)
LUT_WB = (
    0xA0, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x90, 0x0F, 0x0F, 0x00, 0x00, 0x01,
    0x50, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
)
LUT_BB = (
    0x20, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x90, 0x0F, 0x0F, 0x00, 0x00, 0x01,
    0x10, 0x08, 0x08, 0x00, 0x00, 0x02,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
)


class EPD4in2:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT, value=1)
        self.dc_pin = Pin(DC_PIN, Pin.OUT, value=0)
        self.cs_pin = Pin(CS_PIN, Pin.OUT, value=1)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.spi = SPI(
            1,
            baudrate=4_000_000,
            polarity=0,
            phase=0,
            sck=Pin(SCK_PIN),
            mosi=Pin(MOSI_PIN),
        )
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def send_command(self, command):
        self.dc_pin.value(0)
        self.cs_pin.value(0)
        self.spi.write(bytes((command,)))
        self.cs_pin.value(1)

    def send_data(self, data):
        self.dc_pin.value(1)
        self.cs_pin.value(0)
        self.spi.write(bytes((data,)) if isinstance(data, int) else data)
        self.cs_pin.value(1)

    def reset(self):
        # The Pico-ePaper power circuit requires short reset pulses.
        for _ in range(3):
            self.reset_pin.value(1)
            time.sleep_ms(20)
            self.reset_pin.value(0)
            time.sleep_ms(2)
        self.reset_pin.value(1)
        time.sleep_ms(20)

    def wait_until_idle(self, timeout_ms=15_000):
        # BUSY is low while the UC8176 is working and high when it is idle.
        started = time.ticks_ms()
        while self.busy_pin.value() == 0:
            if time.ticks_diff(time.ticks_ms(), started) > timeout_ms:
                raise RuntimeError("e-paper BUSY timeout; check Pico-ePaper-4.2 wiring and power")
            time.sleep_ms(50)

    def _load_luts(self):
        for command, lut in ((0x20, LUT_VCOM), (0x21, LUT_WW), (0x22, LUT_BW),
                             (0x23, LUT_WB), (0x24, LUT_BB)):
            self.send_command(command)
            self.send_data(bytes(lut))

    def init(self):
        self.reset()

        self.send_command(POWER_SETTING)
        self.send_data(bytes((0x03, 0x00, 0x2B, 0x2B)))
        self.send_command(BOOSTER_SOFT_START)
        self.send_data(bytes((0x17, 0x17, 0x17)))
        self.send_command(POWER_ON)
        self.wait_until_idle()

        self.send_command(PANEL_SETTING)
        self.send_data(bytes((0xBF, 0x0D)))
        self.send_command(PLL_CONTROL)
        self.send_data(0x3C)
        self.send_command(TCON_RESOLUTION)
        self.send_data(bytes((0x01, 0x90, 0x01, 0x2C)))
        self.send_command(VCM_DC_SETTING)
        self.send_data(0x28)
        self.send_command(VCOM_AND_DATA_INTERVAL)
        self.send_data(0x97)
        self._load_luts()

    def _refresh(self):
        self.send_command(DISPLAY_REFRESH)
        time.sleep_ms(100)
        self.wait_until_idle()

    def clear(self, color=0xFF):
        if color not in (0x00, 0xFF):
            raise ValueError("color must be 0x00 (black) or 0xFF (white)")
        frame = bytes((color,)) * (self.width * self.height // 8)
        self.send_command(DATA_START_TRANSMISSION_1)
        self.send_data(frame)
        self.send_command(DATA_START_TRANSMISSION_2)
        self.send_data(frame)
        self._refresh()

    def display(self, image):
        if len(image) != self.width * self.height // 8:
            raise ValueError("image must contain exactly 15,000 bytes")
        self.send_command(DATA_START_TRANSMISSION_2)
        self.send_data(image)
        self._refresh()

    def display_partial(self, image, x=0, y=0, w=EPD_WIDTH, h=EPD_HEIGHT):
        # The manufacturer's own 4.2-inch example warns that partial refresh is
        # poor. A full refresh is reliable and prevents ghosting/corruption.
        self.display(image)

    def sleep(self):
        self.send_command(POWER_OFF)
        self.wait_until_idle()
        self.send_command(DEEP_SLEEP)
        self.send_data(0xA5)
