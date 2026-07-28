# config.py
# Fill these in before running.

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# OpenWeather API. Create a key at https://home.openweathermap.org/users/sign_up
OWM_API_KEY = "YOUR_OPENWEATHER_API_KEY"

# Geographic coordinates are the recommended API location format. Set both for
# the most precise location, or leave them as None to use OWM_CITY instead.
OWM_LAT = None             # e.g. 41.8757
OWM_LON = None             # e.g. -87.6189
OWM_CITY = "Chicago,US"    # Compatibility fallback, e.g. "London,GB"
OWM_UNITS = "imperial"     # "metric" or "imperial"
OWM_LANGUAGE = "en"        # OpenWeather response-language code

# Displayed location and time. OpenWeather's city response does not include a
# state/province, so set LOCATION_REGION yourself (or leave it blank).
LOCATION_REGION = "Illinois"  # e.g. "Illinois", "Ontario", or ""

# The Pico does not include a timezone database. Set a fixed UTC offset for the
# timezone you want displayed. EST is UTC-5 (-300 minutes); change to -180 and
# label "EDT" when daylight-saving time applies.
TIMEZONE_LABEL = "EST"
TIMEZONE_OFFSET_MINUTES = -240
USE_24_HOUR_TIME = False
SYNC_CLOCK_WITH_NTP = True  # Requires the Pico W to have Internet access.

# Update interval in seconds
UPDATE_INTERVAL = 600  # 10 minutes; well below the 60 calls/minute free-plan limit
