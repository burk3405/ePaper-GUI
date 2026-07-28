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
        self.fb.text(title[:47], 10, 10, BLACK)

    def draw_temperature(self, label, x, y, temperature, unit, decimals=1):
        value = ("{:." + str(decimals) + "f}").format(temperature)
        text = "{}{}".format(label, value)
        self.fb.text(text, x, y, BLACK)

        # MicroPython's built-in font has no degree glyph. Draw a small outline
        # circle immediately after the numeric value, then print the unit.
        degree_x = x + len(text) * 8 + 1
        degree_y = y + 2
        self.fb.pixel(degree_x, degree_y, BLACK)
        self.fb.pixel(degree_x - 1, degree_y + 1, BLACK)
        self.fb.pixel(degree_x + 1, degree_y + 1, BLACK)
        self.fb.pixel(degree_x, degree_y + 2, BLACK)
        self.fb.text(unit, degree_x + 5, y, BLACK)

    def draw_weather(self, weather):
        self.clear_fb(WHITE)
        header = "{} | {}".format(weather["location"], weather["updated_at"]) if weather else "Weather Dashboard"
        self.draw_header(header)

        if not weather:
            self.fb.text("No data", 10, 50, BLACK)
            return

        draw_weather_icon(
            self.fb, 10, 38, weather["condition_id"], weather["icon"]
        )

        self.draw_temperature("Now: ", 70, 44, weather["temp"], weather["temperature_unit"])
        self.draw_temperature("Feels: ", 70, 59, weather["feels_like"], weather["temperature_unit"])
        self.fb.text(weather["description"][:34], 70, 74, BLACK)

        self.fb.text("Humidity: {}%".format(weather["humidity"]), 10, 108, BLACK)
        self.fb.text("Wind: {:.1f} {}".format(weather["wind"], weather["wind_unit"]), 10, 123, BLACK)

        self.fb.hline(0, 142, EPD_WIDTH, BLACK)
        self.fb.text("3-hour forecast ({})".format(weather["timezone_label"]), 10, 150, BLACK)
        for index, item in enumerate(weather["forecast"][:4]):
            x = 10 + index * 97
            self.fb.text(item["time"], x, 166, BLACK)
            draw_weather_icon(self.fb, x, 178, item["condition_id"], item["icon"])
            self.draw_temperature("", x, 233, item["temp"], weather["temperature_unit"], decimals=0)
            self.fb.text("Rain {}%".format(item["pop"]), x, 248, BLACK)

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
