from ledmatrix import LedMatrix
from pixelfont import PixelFont
from hal import HAL

print("START")

GPIO_PIN = 16
DISPLAY_PIXEL_COUNT = 256
DISPLAY_ROWS = 8
DISPLAY_COLS = 32
DISPLAY_FPS = 10
DISPLAY_DEBUG = True
DISPLAY_INTENSITY = 2

driver = HAL(gpio_pin=GPIO_PIN, pixel_count=DISPLAY_PIXEL_COUNT)
display = LedMatrix(driver, dict(
    debug=DISPLAY_DEBUG,
    columns=DISPLAY_COLS,
    stride=DISPLAY_ROWS,
    fps=DISPLAY_FPS
))

display.render_text(PixelFont, "raphtoro", 0, 0, 10,0,5)
display.render()
