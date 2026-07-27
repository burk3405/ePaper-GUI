# Monochrome weather glyphs for MicroPython framebuffers.
# OpenWeather condition IDs identify the weather class; the icon suffix (d/n)
# distinguishes day and night for clear and partly-cloudy conditions.

BLACK = 0
WHITE = 1


def _circle(fb, x0, y0, radius, color=BLACK):
    x = radius
    y = 0
    error = 1 - x
    while x >= y:
        fb.pixel(x0 + x, y0 + y, color)
        fb.pixel(x0 + y, y0 + x, color)
        fb.pixel(x0 - y, y0 + x, color)
        fb.pixel(x0 - x, y0 + y, color)
        fb.pixel(x0 - x, y0 - y, color)
        fb.pixel(x0 - y, y0 - x, color)
        fb.pixel(x0 + y, y0 - x, color)
        fb.pixel(x0 + x, y0 - y, color)
        y += 1
        if error < 0:
            error += 2 * y + 1
        else:
            x -= 1
            error += 2 * (y - x) + 1


def _filled_circle(fb, x0, y0, radius, color):
    for y in range(-radius, radius + 1):
        x = int((radius * radius - y * y) ** 0.5)
        fb.hline(x0 - x, y0 + y, 2 * x + 1, color)


def _sun(fb, x, y):
    _circle(fb, x + 24, y + 22, 10)
    for dx, dy in ((0, -17), (12, -12), (17, 0), (12, 12),
                   (0, 17), (-12, 12), (-17, 0), (-12, -12)):
        x1 = x + 24 + dx
        y1 = y + 22 + dy
        x2 = x + 24 + (dx * 23 // 17)
        y2 = y + 22 + (dy * 23 // 17)
        fb.line(x1, y1, x2, y2, BLACK)


def _moon(fb, x, y):
    _filled_circle(fb, x + 24, y + 23, 14, BLACK)
    _filled_circle(fb, x + 30, y + 17, 14, WHITE)
    _circle(fb, x + 24, y + 23, 14)


def _cloud(fb, x, y, large=True):
    base_y = y + (32 if large else 36)
    radius = 10 if large else 7
    _circle(fb, x + 17, base_y - 5, radius)
    _circle(fb, x + 30, base_y - 10, radius + 2)
    _circle(fb, x + 42, base_y - 4, radius)
    fb.line(x + 7, base_y, x + 49, base_y, BLACK)
    fb.line(x + 7, base_y, x + 7, base_y - 3, BLACK)
    fb.line(x + 49, base_y, x + 49, base_y - 3, BLACK)


def _rain(fb, x, y, heavy=False):
    _cloud(fb, x, y - 5)
    for dx in (15, 27, 39):
        fb.line(x + dx, y + 34, x + dx - 4, y + 43, BLACK)
        if heavy:
            fb.line(x + dx + 3, y + 34, x + dx - 1, y + 43, BLACK)


def _snow(fb, x, y):
    _cloud(fb, x, y - 5)
    for cx in (17, 31, 43):
        cy = y + 39
        fb.hline(x + cx - 4, cy, 9, BLACK)
        fb.vline(x + cx, cy - 4, 9, BLACK)
        fb.line(x + cx - 3, cy - 3, x + cx + 3, cy + 3, BLACK)
        fb.line(x + cx - 3, cy + 3, x + cx + 3, cy - 3, BLACK)


def _fog(fb, x, y):
    _cloud(fb, x, y - 10, False)
    for row, start, length in ((31, 5, 38), (37, 11, 38), (43, 5, 38)):
        fb.hline(x + start, y + row, length, BLACK)


def _thunder(fb, x, y):
    _cloud(fb, x, y - 6)
    fb.line(x + 29, y + 31, x + 22, y + 42, BLACK)
    fb.line(x + 22, y + 42, x + 29, y + 42, BLACK)
    fb.line(x + 29, y + 42, x + 23, y + 48, BLACK)


def _partly_cloudy(fb, x, y, night):
    if night:
        _moon(fb, x - 4, y - 4)
    else:
        _sun(fb, x - 4, y - 4)
    _cloud(fb, x, y + 4, False)


def draw_weather_icon(fb, x, y, condition_id, icon_code=""):
    """Draw a 52x52 icon from OpenWeather's primary condition and icon code."""
    is_night = icon_code.endswith("n")
    if 200 <= condition_id < 300:
        _thunder(fb, x, y)
    elif 300 <= condition_id < 400:
        _rain(fb, x, y, False)
    elif 500 <= condition_id < 600:
        _snow(fb, x, y) if condition_id == 511 else _rain(fb, x, y, condition_id >= 502)
    elif 600 <= condition_id < 700:
        _snow(fb, x, y)
    elif 700 <= condition_id < 800:
        _fog(fb, x, y)
    elif condition_id == 800:
        _moon(fb, x, y) if is_night else _sun(fb, x, y)
    elif condition_id == 801:
        _partly_cloudy(fb, x, y, is_night)
    else:  # 802-804 and unknown conditions: scattered, broken, or overcast cloud.
        _cloud(fb, x, y)
