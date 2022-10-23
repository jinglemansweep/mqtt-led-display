from errno import EINPROGRESS


try:
    import utime as utime
except:
    import time as utime

    if not hasattr(utime, "ticks_ms"):
        utime.ticks_ms = lambda: int(utime.time() * 1000)
    if not hasattr(utime, "ticks_diff"):
        utime.ticks_diff = lambda a, b: a - b

try:
    import uasyncio as uasyncio
except:
    import asyncio as uasyncio

try:
    import ubinascii as ubinascii
except:
    import binascii as ubinascii

try:
    import uerrno as uerrno
except:

    class uerrno:
        EINPROGRESS = "INPROGRESS"
        ETIMEDOUT = "TIMEDOUT"


try:
    import usocket as usocket
except:
    import socket as usocket

try:
    import ustruct as ustruct
except:
    import struct as ustruct

try:
    from machine import unique_id
except:
    unique_id = lambda: bytearray([0, 1, 2, 3])


try:
    import ntptime
except:

    class ntptime:
        def settime(self):
            pass
