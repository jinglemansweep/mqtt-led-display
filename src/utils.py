import time
from ntptime import settime

def set_clock():
    (year, month, day, hour, minute, second, weekday, _) = time.localtime()[:8]
    now_fmt = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
        year, month, day, hour, minute, second
    )
    settime()
    print(f'NTP Time: {now_fmt}')
