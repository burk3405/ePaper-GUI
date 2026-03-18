# weather.py
import network
import time
import urequests
from config import WIFI_SSID, WIFI_PASSWORD, OWM_API_KEY, OWM_CITY, OWM_UNITS

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

def fetch_weather():
    if not connect_wifi():
        return None

    url = (
        "http://api.openweathermap.org/data/2.5/weather"
        "?q={city}&appid={key}&units={units}"
    ).format(city=OWM_CITY, key=OWM_API_KEY, units=OWM_UNITS)

    try:
        r = urequests.get(url)
        data = r.json()
        r.close()
    except Exception:
        return None

    try:
        main = data["weather"][0]["main"]
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
    except KeyError:
        return None

    return {
        "main": main,
        "description": desc,
        "temp": temp,
        "feels_like": feels,
        "humidity": humidity,
        "wind": wind,
    }
