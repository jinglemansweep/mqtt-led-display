from neopixel import NeoPixel
from machine import Pin
from ntptime import settime

class HAL:
    def __init__(self, gpio_pin=16, pixel_count=64):
        self.gpio_pin = gpio_pin
        self.pixel_count = pixel_count
        self.np = NeoPixel(Pin(self.gpio_pin), self.pixel_count)
        self.enable_auto_time = False

    def init_display(self, pixel_count=64):
        self.clear_display()

    def clear_display(self):
        for i in range(self.pixel_count):
            self.np[i] = (0, 0, 0)
            self.np.write()

    def update_display(self, num_modified_pixels):
        if not num_modified_pixels:
            return
        self.np.write()

    def put_pixel(self, addr, r, g, b):
        self.np[addr % self.pixel_count] = (r, g, b)

    def reset(self):
        self.clear_display()

    def process_input(self):
        # TODO: implement
        return 0

    def set_rtc(self, t):
        settime()

    def set_auto_time(self, enable=True):
        self.enable_auto_time = enable

    def suspend_host(self, restart_timeout_seconds):
        if restart_timeout_seconds < 15:
            return
