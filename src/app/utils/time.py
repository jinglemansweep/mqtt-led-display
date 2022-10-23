from app.utils.system import ntptime, uasyncio, utime
from app.settings import UTC_OFFSET


async def ntp_update():
    repeat_delay = 3600  # 1 hour
    success = False
    try:
        ntptime.settime()
        success = True
        print("ntp: updated")
    except:
        print("ntp: error")
        repeat_delay = 10
    finally:
        print(f"ntp: update in {repeat_delay}s")
        await uasyncio.sleep(repeat_delay)
        uasyncio.create_task(ntp_update())
    return success


def get_time(utc_offset=UTC_OFFSET):
    utc = utime.time()
    # Timezone
    local_time = utc + (utc_offset * 3600)
    local_tuple = utime.localtime(local_time)
    # Daylight Savings Time
    dst_offset = 0
    year = local_tuple[0]
    dst_mar = utime.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0)
    )
    dst_oct = utime.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0, 0)
    )
    if local_time < dst_mar:  # Before last Sunday of March
        pass
    elif local_time < dst_oct:  # Before last Sunday of October
        dst_offset += 3600
    else:  # After last Sunday of October
        pass
    return utime.localtime(local_time + dst_offset)
