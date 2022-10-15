import uasyncio as asyncio
from app.resources.pixelfont import PixelFont
from app.constants import UNIQUE_ID, HASS_DISCOVERY_PREFIX
from app.state import STATE

MQTT_TEXT_ID = f'{UNIQUE_ID}_text'
MQTT_TEXT_PREFIX = f'{HASS_DISCOVERY_PREFIX}/text/{MQTT_TEXT_ID}'

async def flash_message(display, msg):
    print(f'FLASH MESSAGE: {msg}')
    STATE['clock.visible'] = False
    text = msg.lower()
    display.render_text(PixelFont, text, y=1)
    display.render()        
    await asyncio.sleep(1)
    STATE['clock.visible'] = True

async def show_message(display, msg):
    print(f'RENDER MESSAGE: {msg}')
    STATE['clock.visible'] = False
    display.hscroll(-1)
    await asyncio.sleep(1)
    words = msg.lower().split(' ')
    for i, word in enumerate(words):
        display.render_text(PixelFont, word, y=1)
        display.render()        
        if i < len(words) - 1:
            await asyncio.sleep(2)     
            display.fade()            
    await asyncio.sleep(2)
    display.hscroll(-1)
    await asyncio.sleep(1)
    STATE['clock.visible'] = True