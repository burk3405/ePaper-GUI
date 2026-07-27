# weather.py
import network
import time
import urequests
from config import (
    WIFI_SSID, WIFI_PASSWORD, OWM_API_KEY, OWM_CITY, OWM_LANGUAGE, OWM_LAT,
    OWM_LON, OWM_UNITS,
)

CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
FORECAST_ENTRY_COUNT = 40  # Five days, in three-hour intervals.

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
        "time": entry["dt_txt"][11:16],
        "temp": entry["main"]["temp"],
        "condition_id": condition["id"],
        "icon": condition["icon"],
        "pop": int(entry.get("pop", 0) * 100 + 0.5),
    }


def fetch_weather():
    if not connect_wifi():
        return None

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
        "location": current.get("name", OWM_CITY),
        "description": condition["description"],
        "condition_id": condition["id"],
        "icon": condition["icon"],
        "temp": current["main"]["temp"],
        "feels_like": current["main"]["feels_like"],
        "humidity": current["main"]["humidity"],
        "wind": current.get("wind", {}).get("speed", 0),
        "forecast": forecast,
    }
