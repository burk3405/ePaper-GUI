# gui.py
from machine import Pin
import framebuf
from epd4in2 import EPD4in2, EPD_WIDTH, EPD_HEIGHT
from icons import SUN_ICON, CLOUD_ICON, RAIN_ICON

WHITE = 1
BLACK = 0

class WeatherGUI:
    def __init__(self):
        self.epd = EPD4in2()
        self.epd.init()

        self.buffer = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)
        self.fb = framebuf.FrameBuffer(self.buffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)

    def clear_fb(self, color=WHITE):
        fill_color = 0xFF if color == WHITE else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = fill_color

    def draw_header(self, title):
        self.fb.fill_rect(0, 0, EPD_WIDTH, 30, WHITE)
        self.fb.rect(0, 0, EPD_WIDTH, 30, BLACK)
        self.fb.text(title, 10, 10, BLACK)

    def select_icon(self, main):
        main = (main or "").lower()
        if "rain" in main:
            return RAIN_ICON
        if "cloud" in main:
            return CLOUD_ICON
        return SUN_ICON

    def draw_icon(self, icon_bytes, x, y):
        icon_fb = framebuf.FrameBuffer(bytearray(icon_bytes), 32, 32, framebuf.MONO_HLSB)
        self.fb.blit(icon_fb, x, y)

    def draw_weather(self, weather):
        self.clear_fb(WHITE)
        self.draw_header("Weather Dashboard")

        if not weather:
            self.fb.text("No data", 10, 50, BLACK)
            return

        icon = self.select_icon(weather["main"])
        self.draw_icon(icon, 10, 40)

        temp_str = "{:.1f}".format(weather["temp"])
        feels_str = "{:.1f}".format(weather["feels_like"])
        self.fb.text("Now: {}°".format(temp_str), 60, 40, BLACK)
        self.fb.text("Feels: {}°".format(feels_str), 60, 55, BLACK)
        self.fb.text(weather["description"], 60, 70, BLACK)

        self.fb.text("Humidity: {}%".format(weather["humidity"]), 10, 100, BLACK)
        self.fb.text("Wind: {} m/s".format(weather["wind"]), 10, 115, BLACK)

        # Footer
        self.fb.hline(0, EPD_HEIGHT - 20, EPD_WIDTH, BLACK)
        self.fb.text("Updated", 10, EPD_HEIGHT - 15, BLACK)

    def full_update(self):
        # Invert for ePaper: 0=black,1=white -> driver expects 0x00=black,0xFF=white
        self.epd.display(self.buffer)

    def partial_update_region(self, x, y, w, h):
        # Extract region bytes and call partial update.
        # For simplicity, we just send the whole buffer as a partial window
        # covering the full screen. You can optimize later.
        self.epd.display_partial(self.buffer, 0, 0, EPD_WIDTH, EPD_HEIGHT)

    def sleep(self):
        self.epd.sleep()
