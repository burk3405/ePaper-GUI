# main.py
import time
from config import UPDATE_INTERVAL
from weather import fetch_weather
from gui import WeatherGUI

def main():
    gui = WeatherGUI()

    # Initial full update
    print("Fetching initial weather data...")
    weather = fetch_weather()
    if weather is None:
        print("No weather data available; displaying the fallback screen.")
    else:
        print("Weather received for {}.".format(weather["location"]))
    gui.draw_weather(weather)
    print("Refreshing e-paper display...")
    gui.full_update()
    print("Initial display update complete.")

    last_update = time.time()

    while True:
        now = time.time()
        if now - last_update >= UPDATE_INTERVAL:
            print("Fetching scheduled weather update...")
            weather = fetch_weather()
            if weather is None:
                print("No weather data available; displaying the fallback screen.")
            else:
                print("Weather received for {}.".format(weather["location"]))
            gui.draw_weather(weather)
            # Uses the driver's safe full-refresh fallback.
            print("Refreshing e-paper display...")
            gui.partial_update_region(0, 0, 400, 300)
            print("Scheduled display update complete.")
            last_update = now

        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    pass
