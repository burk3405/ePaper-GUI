# main.py
import time
from config import UPDATE_INTERVAL
from weather import fetch_weather
from gui import WeatherGUI

def main():
    gui = WeatherGUI()

    # Initial full update
    weather = fetch_weather()
    gui.draw_weather(weather)
    gui.full_update()

    last_update = time.time()

    while True:
        now = time.time()
        if now - last_update >= UPDATE_INTERVAL:
            weather = fetch_weather()
            gui.draw_weather(weather)
            # Use partial update for subsequent refreshes
            gui.partial_update_region(0, 0, 400, 300)
            last_update = now

        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    pass
