from app.resources.pixelfont import PixelFont

def led_log(display, msg):
    display.clear()
    display.render_text(PixelFont, msg, y=1)
    display.render()