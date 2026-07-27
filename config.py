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

# Update interval in seconds
UPDATE_INTERVAL = 600  # 10 minutes; well below the 60 calls/minute free-plan limit
