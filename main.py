import time
from ledmatrix import LedMatrix
from pixelfont import PixelFont
from hal import HAL
from utils import wifi_connect, set_ntp_clock
from secrets import WIFI_SSID, WIFI_KEY

print("START")

WLAN = "PT"

GPIO_PIN = 16
DISPLAY_PIXEL_COUNT = 256
DISPLAY_ROWS = 8
DISPLAY_COLS = 32
DISPLAY_FPS = 10
DISPLAY_DEBUG = False
DISPLAY_INTENSITY = 2

wifi_connect(WIFI_SSID, WIFI_KEY)
set_ntp_clock()

driver = HAL(gpio_pin=GPIO_PIN, pixel_count=DISPLAY_PIXEL_COUNT)


display = LedMatrix(driver, dict(
    debug=DISPLAY_DEBUG,
    columns=DISPLAY_COLS,
    stride=DISPLAY_ROWS,
    fps=DISPLAY_FPS
))

while True:
    (year, month, day, hour, minute, second, weekday, _) = time.localtime()[:8]
    now_fmt = '{:02d}:{:02d}'.format(hour, minute)
    display.render_text(PixelFont, now_fmt, 0, 0, 10,0,5)
    display.render()
    time.sleep(2)
    display.hscroll(-1)
    time.sleep(1)