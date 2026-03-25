
from time import sleep
from pathlib import Path

import ledmatrix_server.homeassistant as ha
import ledmatrix_server.weather as wtr

from ledmatrix_server.common import log, DEBUG
from ledmatrix_server.resources.loader import get_image
from ledmatrix_server.render import Display, ImageComponent, TextComponent
from ledmatrix_server.helpers import is_christmas
from ledmatrix_server.config import config

output = config.output_path
if not output:
    output = "output"

canvas = Display(width=64, height=32, output=Path(output))

# -------------------------
# Functions
# -------------------------

def get_in_out(sensor: str):
    state = ha.get_state(sensor)

    if isinstance(state, str):
        state = state.lower()
    else:
        return get_image("cat_unknown.bmp")

    if state == "on":
        return get_image("cat_in.bmp")
    elif state == "off":
        return get_image("cat_out.bmp")
    else:
        return get_image("cat_unknown.bmp")


def update_canvas():
    # Cats
    maple_icon = get_image("maple_xmas.bmp") if is_christmas() else get_image("maple.bmp")
    maple_state_icon = get_in_out("binary_sensor.maple")
    maple_xyz = (1, 18, 0) if is_christmas() else (1, 22, 0)
    cinnamon_icon = get_image("cinnamon_xmas.bmp") if is_christmas() else get_image("cinnamon.bmp")
    cinnamon_state_icon = get_in_out("binary_sensor.cinnamon")
    cinnamon_xyz = (50, 18, 0) if is_christmas() else (50, 22, 0)
    
    # Weather
    temp_high, temp_high_c = wtr.get_temp_high()
    temp_low, temp_low_c = wtr.get_temp_low()
    precip = wtr.get_rain_chance_str()

    # Render
    canvas.set("brolly", ImageComponent(59, 10, 0, get_image("brolly.bmp")))
    canvas.set("thermo", ImageComponent(59, -1, 0, get_image("thermometer.bmp")))

    canvas.set("maple", ImageComponent(*maple_xyz, maple_icon))
    canvas.set("maple_state", ImageComponent(15, 23 ,0, maple_state_icon))
    canvas.set("cinnamon", ImageComponent(*cinnamon_xyz, cinnamon_icon))
    canvas.set("cinnamon_state", ImageComponent(36, 23, 0, cinnamon_state_icon))
    
    canvas.set("weather", ImageComponent(31, 9, 0, wtr.get_weather_icon()))
    canvas.set("temp_high", TextComponent(49, 1, 0, temp_high, colour=temp_high_c))
    canvas.set("temp_low", TextComponent(38, 4, 0, temp_low, colour=temp_low_c))
    canvas.set("precip", TextComponent(44, 12, 0, precip, colour=0x00ffff))


def main():
    log.info("Started!")
    while True:
        update_canvas()
        if DEBUG:
            canvas.print_to_console()
        canvas.export()
        sleep(5)


# -------------------------
# Running Code
# -------------------------

if __name__ == "__main__":
    main()

