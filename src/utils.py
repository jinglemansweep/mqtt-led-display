import utime
from machine import RTC
import ntptime
from pixelfont import PixelFont

def set_clock(offset=0):
    year = utime.localtime()[0]  # current year
    now = ntptime.time()
    dst_mar = utime.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0)
    )
    dst_oct = utime.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0, 0)
    )
    if now < dst_mar: # Before last Sunday of March
        ntptime.NTP_DELTA = 3155673600 - (offset * 3600) # GMT: UTC+0H
    elif now < dst_oct: # Before last Sunday of October
        ntptime.NTP_DELTA = 3155673600 - (offset * 3600) - 3600 # BST: UTC+1H
    else: # After last Sunday of October
        ntptime.NTP_DELTA = 3155673600 - (offset * 3600) # GMT: UTC+0H
    ntp_done = False
    while not ntp_done:
        try:
            print('NTP: Setting Time')
            ntptime.settime()
            ntp_done = True
        except OSError:
            print('NTP: Error')    
    (year, month, day, hour, minute, second, weekday, _) = utime.localtime()[:8]
    now_fmt = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        year, month, day, hour, minute, second
    )
    print(f"NTP Time: {now_fmt}")    

def led_log(display, msg):
    display.render_text(PixelFont, msg, 2, 1, 2, 0, 0)
    display.render()
