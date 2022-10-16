from app.resources.pixelfont import PixelFont


def led_log(display, msg, color=(0x00, 0x66, 0x00)):
    display.clear()
    display.render_text(PixelFont, msg, y=1, color=color)
    display.render()


def rgb_dict_to_tuple(rgb):
    return (rgb.get("r"), rgb.get("g"), rgb.get("b"))


def scale_brightness(value, brightness, scale):
    return int(value * (brightness / scale))
