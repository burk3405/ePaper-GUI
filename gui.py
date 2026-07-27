# gui.py
import framebuf
from epd4in2 import EPD4in2, EPD_WIDTH, EPD_HEIGHT
from icons import draw_weather_icon

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

    def draw_weather(self, weather):
        self.clear_fb(WHITE)
        self.draw_header(weather["location"] if weather else "Weather Dashboard")

        if not weather:
            self.fb.text("No data", 10, 50, BLACK)
            return

        draw_weather_icon(
            self.fb, 10, 38, weather["condition_id"], weather["icon"]
        )

        temp_str = "{:.1f}".format(weather["temp"])
        feels_str = "{:.1f}".format(weather["feels_like"])
        self.fb.text("Now: {}°".format(temp_str), 70, 44, BLACK)
        self.fb.text("Feels: {}°".format(feels_str), 70, 59, BLACK)
        self.fb.text(weather["description"][:34], 70, 74, BLACK)

        self.fb.text("Humidity: {}%".format(weather["humidity"]), 10, 108, BLACK)
        self.fb.text("Wind: {:.1f}".format(weather["wind"]), 10, 123, BLACK)

        self.fb.hline(0, 142, EPD_WIDTH, BLACK)
        self.fb.text("3-hour forecast (UTC)", 10, 150, BLACK)
        for index, item in enumerate(weather["forecast"][:4]):
            x = 10 + index * 97
            self.fb.text(item["time"], x, 166, BLACK)
            draw_weather_icon(self.fb, x, 178, item["condition_id"], item["icon"])
            self.fb.text("{}°".format(int(item["temp"] + 0.5)), x, 233, BLACK)
            self.fb.text("POP {}%".format(item["pop"]), x, 248, BLACK)

        self.fb.hline(0, EPD_HEIGHT - 20, EPD_WIDTH, BLACK)
        self.fb.text("OpenWeather: current + 5-day data", 10, EPD_HEIGHT - 15, BLACK)

    def full_update(self):
        # Invert for ePaper: 0=black,1=white -> driver expects 0x00=black,0xFF=white
        self.epd.display(self.buffer)

    def partial_update_region(self, x, y, w, h):
        # The 4.2-inch panel's partial refresh is unreliable. The driver uses
        # a safe full refresh until a tested partial-refresh implementation is added.
        self.epd.display_partial(self.buffer, x, y, w, h)

    def sleep(self):
        self.epd.sleep()
