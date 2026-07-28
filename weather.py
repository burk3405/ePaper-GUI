# weather.py
import network
import time
import urequests
from config import (
    WIFI_SSID, WIFI_PASSWORD, OWM_API_KEY, OWM_CITY, OWM_LANGUAGE, OWM_LAT,
    OWM_LON, OWM_UNITS, LOCATION_REGION, TIMEZONE_LABEL,
    TIMEZONE_OFFSET_MINUTES, USE_24_HOUR_TIME, SYNC_CLOCK_WITH_NTP,
)

CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
FORECAST_ENTRY_COUNT = 40  # Five days, in three-hour intervals.
UNIX_TO_MICROPYTHON_EPOCH = 946684800
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)
_clock_synced = False


def _local_datetime(unix_timestamp):
    # RP2 MicroPython's time module uses a 2000 epoch, whereas OpenWeather uses
    # Unix timestamps. Use the configured fixed UTC offset before formatting.
    timestamp = int(unix_timestamp) + TIMEZONE_OFFSET_MINUTES * 60
    return time.localtime(timestamp - UNIX_TO_MICROPYTHON_EPOCH)


def _format_clock_from_datetime(date_time, include_minutes=True):
    hour = date_time[3]
    minute = date_time[4]
    if USE_24_HOUR_TIME:
        return "{:02d}:{:02d}".format(hour, minute) if include_minutes else "{:02d}:00".format(hour)

    suffix = "am" if hour < 12 else "pm"
    hour = hour % 12 or 12
    return "{}:{:02d} {}".format(hour, minute, suffix) if include_minutes else "{} {}".format(hour, suffix)


def _format_clock(unix_timestamp, include_minutes=True):
    return _format_clock_from_datetime(_local_datetime(unix_timestamp), include_minutes)


def _ordinal_day(day):
    if 10 < day % 100 < 14:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return "{}{}".format(day, suffix)


def _format_datetime(date_time):
    return "{}, {} {} {} {}".format(
        WEEKDAYS[date_time[6]],
        MONTHS[date_time[1] - 1],
        _ordinal_day(date_time[2]),
        _format_clock_from_datetime(date_time),
        TIMEZONE_LABEL,
    )


def _sync_clock():
    global _clock_synced
    if _clock_synced or not SYNC_CLOCK_WITH_NTP:
        return _clock_synced
    try:
        import ntptime
        ntptime.settime()
        _clock_synced = True
    except Exception:
        pass
    return _clock_synced


def _current_datetime():
    # After ntptime.settime(), RP2 MicroPython's time.time() uses its 2000 epoch.
    return time.localtime(time.time() + TIMEZONE_OFFSET_MINUTES * 60)


def _temperature_unit():
    return {"imperial": "F", "metric": "C", "standard": "K"}.get(OWM_UNITS, "")


def _wind_unit():
    return "mph" if OWM_UNITS == "imperial" else "m/s"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(60):
            if wlan.isconnected():
                break
            time.sleep(0.5)
    return wlan.isconnected()


def _location_query():
    if OWM_LAT is not None and OWM_LON is not None:
        return "lat={}&lon={}".format(OWM_LAT, OWM_LON)
    return "q={}".format(OWM_CITY)


def _request_json(base_url, extra_query=""):
    url = "{}?{}&appid={}&units={}&lang={}".format(
        base_url, _location_query(), OWM_API_KEY, OWM_UNITS, OWM_LANGUAGE
    )
    if extra_query:
        url = "{}&{}".format(url, extra_query)

    response = None
    try:
        response = urequests.get(url)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None
    finally:
        if response is not None:
            response.close()


def _forecast_entry(entry):
    condition = entry["weather"][0]
    return {
        "time": _format_clock(entry["dt"], include_minutes=True),
        "temp": entry["main"]["temp"],
        "condition_id": condition["id"],
        "icon": condition["icon"],
        "pop": int(entry.get("pop", 0) * 100 + 0.5),
    }


def fetch_weather():
    if not connect_wifi():
        return None

    clock_synced = _sync_clock()

    current = _request_json(CURRENT_WEATHER_URL)
    forecast_data = _request_json(FORECAST_URL, "cnt={}".format(FORECAST_ENTRY_COUNT))
    if current is None or forecast_data is None:
        return None

    try:
        condition = current["weather"][0]
        forecast = [_forecast_entry(entry) for entry in forecast_data["list"]]
    except (IndexError, KeyError, TypeError):
        return None

    return {
        "location": "{}, {}".format(current.get("name", OWM_CITY), LOCATION_REGION)
        if LOCATION_REGION else current.get("name", OWM_CITY),
        # OpenWeather's `dt` is the time its station last observed the weather;
        # it is not a live clock. Show the Pico's NTP-synchronized current time.
        "updated_at": _format_datetime(_current_datetime()) if clock_synced
        else _format_datetime(_local_datetime(current["dt"])),
        "description": condition["description"],
        "condition_id": condition["id"],
        "icon": condition["icon"],
        "temp": current["main"]["temp"],
        "feels_like": current["main"]["feels_like"],
        "humidity": current["main"]["humidity"],
        "wind": current.get("wind", {}).get("speed", 0),
        "wind_unit": _wind_unit(),
        "temperature_unit": _temperature_unit(),
        "timezone_label": TIMEZONE_LABEL,
        "forecast": forecast,
    }
