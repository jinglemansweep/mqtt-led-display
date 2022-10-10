import time
from ntptime import settime
from pixelfont import PixelFont

def set_clock():
    (year, month, day, hour, minute, second, weekday, _) = time.localtime()[:8]
    now_fmt = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
        year, month, day, hour, minute, second
    )
    settime()
    print(f'NTP Time: {now_fmt}')

def led_log(display, msg):
    display.render_text(PixelFont, msg, 2, 1, 2, 0, 0)
    display.render()