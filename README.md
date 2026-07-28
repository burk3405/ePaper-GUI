# Pico ePaper Weather Dashboard

A MicroPython weather dashboard for the Waveshare **Pico-ePaper-4.2** monochrome
400×300 display. It shows current OpenWeather conditions plus the next four
three-hour forecast periods, using the OpenWeather 5-day / 3-hour forecast API.

## What you need

- [Waveshare Pico-ePaper-4.2 display](https://www.amazon.com/Waveshare-4-2inch-Display-Raspberry-Interface/dp/B09B3LGKHJ)
- [Raspberry Pi Pico **W** (recommended) running MicroPython](https://www.amazon.com/dp/B0DP54FWX1)
- [OpenWeather account and API key](https://openweathermap.org/)
- Wi-Fi network with Internet access
- USB data cable and a MicroPython upload tool, such as Thonny or mpremote

A standard original Pico can drive the display but has no onboard Wi-Fi. To
retrieve weather, use a Pico W or adapt the networking layer for an external
Wi-Fi module such as an ESP8266 running AT firmware.

## Display wiring

The driver is configured for the Pico-ePaper-4.2 board's documented SPI1 pin
assignment. If the board is not attached directly to the Pico headers, use this
8-pin cable mapping:

| Display pin | Pico pin | Purpose |
| --- | --- | --- |
| VCC | VSYS | Power input |
| GND | GND | Ground |
| DIN | GP11 | SPI1 MOSI |
| CLK | GP10 | SPI1 SCK |
| CS | GP9 | Chip select |
| DC | GP8 | Data/command select |
| RST | GP12 | Reset |
| BUSY | GP13 | Display busy output |

When mounting the board directly, follow the direction indicator printed next
to the Pico-ePaper USB logo and press the header fully into place. The display
has no separate power connector: it receives power through those header pins
while the Pico is powered by USB. For a cable-mounted board, VCC must connect
to the Pico's `VSYS` pin and GND must connect to GND. Do not use the GP2–GP7
mapping from generic Waveshare examples: it will not communicate with this
board.

## Set up OpenWeather

1. Create an account at <https://home.openweathermap.org/users/sign_up>.
2. Create an API key and wait for it to become active.
3. Open `config.py` and set `WIFI_SSID`, `WIFI_PASSWORD`, and `OWM_API_KEY`.
4. Set `OWM_LAT` and `OWM_LON` to your location. Coordinates are OpenWeather's
   recommended lookup method. Alternatively, leave them as `None` and set
   `OWM_CITY`, for example `"Chicago,US"`.
5. Choose `OWM_UNITS`: `imperial`, `metric`, or `standard`.

The application sends two requests per refresh: `/data/2.5/weather` for current
conditions and `/data/2.5/forecast?cnt=40` for 40 three-hour forecast entries
(five days). The default 10-minute refresh interval makes 0.2 requests per
minute, far below a 60-requests-per-minute allowance. The display renders the
next four forecast periods while retaining all five days in the returned data.

## Install and run

1. Flash a current Pico W MicroPython UF2 to the board, if needed.
2. Copy every project Python file to the Pico filesystem root:
   `config.py`, `Pico-ePaper-4.2-B.py`, `epd4in2.py`, `icons.py`, `weather.py`,
   `gui.py`, and `main.py`.
3. Confirm that `main.py` is named exactly `main.py`; MicroPython runs it after
   booting.
4. Reset the Pico.

A full e-paper refresh typically takes several seconds and flickers. This is
normal. The project intentionally uses full refreshes because Waveshare's 4.2"
partial-refresh example is unreliable and can leave ghosting.

### Run headless after power-on

MicroPython automatically runs a file named `main.py` from the filesystem root
every time the Pico receives power. In Thonny, use **File → Save as**, select
the **MicroPython device**, and save the finished dashboard entry point as
exactly `main.py`. Confirm that all of the files listed above, particularly
`config.py`, `epd4in2.py`, and `Pico-ePaper-4.2-B.py`, are also stored on the
device rather than only on the computer.

After verifying one successful run in Thonny, disconnect it and power the Pico
from any suitable USB power adapter or USB power bank. It will boot, connect to
Wi-Fi, fetch weather, and refresh the display without Thonny or a computer.

## Display and API behavior

OpenWeather returns a primary `weather.id` plus an `icon` value such as `01d` or
`10n`. The dashboard uses those documented fields to draw distinct glyphs for:

- clear day or night
- few, scattered, broken, and overcast clouds
- drizzle, rain, freezing rain, and heavy rain
- thunderstorm
- snow and sleet
- mist, fog, haze, smoke, dust, and other atmospheric conditions

The forecast row shows its UTC time, predicted temperature, condition glyph, and
OpenWeather's precipitation probability (`pop`).

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `e-paper BUSY timeout` | Confirm the supplied adaptive driver is uploaded, then check GP8–GP13 wiring, GND, and a stable power connection. |
| Screen stays unchanged | Verify the board direction or cable mapping. A refresh should visibly flicker. |
| Screen says `No data` | Check Pico W Wi-Fi credentials, Internet access, OpenWeather key activation, and location values. The display itself is working. |
| `ImportError: network` | This code needs a Pico W or an adapted external Wi-Fi implementation. |
| Weather values are wrong | Prefer `OWM_LAT` and `OWM_LON` over a city name. |
| Forecast time seems offset | The forecast row intentionally displays the API's UTC `dt_txt` time. |

## Project files

- `main.py` — boot entry point and update schedule
- `config.py` — Wi-Fi, location, API, and refresh settings
- `weather.py` — OpenWeather current and five-day forecast requests
- `gui.py` — dashboard layout
- `icons.py` — weather condition glyphs
- `Pico-ePaper-4.2-B.py` — official Waveshare driver verified for this display
- `epd4in2.py` — dashboard-compatible wrapper around the official display driver
