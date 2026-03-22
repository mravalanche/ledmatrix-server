from ledmatrix_server import homeassistant as ha
from ledmatrix_server.common import log
from ledmatrix_server.resources.loader import get_image


def sun_up() -> bool:
    sun = ha.get_state("sun.sun")

    return True if sun == "above_horizon" else False


def get_weather_icon():
    try:
        weather_code = int(ha.get_state("sensor.openweathermap_weather_code")) # type: ignore
    except Exception:
        log.error("Something went wrong getting the weather, so it's obviously a tornado")
        return get_image("weather_tornady.bmp")
    
    log.debug(f"Weather code: {weather_code}")

    # Handle typical codes from https://openweathermap.org/weather-conditions

    if 200 <= weather_code <= 232: return get_image("weather_thundery.bmp")
    if weather_code == 511: return get_image("weather_sleety.bmp")
    if 300 <= weather_code <= 531: return get_image("weather_rainy.bmp")
    if 600 <= weather_code <= 602: return get_image("weather_snowy.bmp")
    if 611 <= weather_code <= 616: return get_image("weather_sleety.bmp")
    if 620 <= weather_code <= 622: return get_image("weather_snowy.bmp")
    if 701 <= weather_code <= 771: return get_image("weather_foggy.bmp")
    if weather_code == 781: return get_image("weather_tornady.bmp")
    if 803 <= weather_code <= 804: return get_image("weather_cloudy.bmp")

    # Handle day/night options
    if weather_code == 800:
        return get_image("weather_sunny.bmp") if sun_up() else get_image("weather_moony.bmp")
    
    if weather_code in [801, 802, 803]:
        return get_image("weather_sunnyish.bmp") if sun_up() else get_image("weather_moonyish.bmp")

    # If all else fails, there must be a tornado
    log.warning(f"Got weather code {weather_code} but didn't know how to handle it.")
    return get_image("weather_tornady.bmp")


def get_colour_for_temp(temp:int) -> int:
    if temp <= 0: return 0xffffff
    if temp < 10: return 0x4444ff
    if temp < 20: return 0xffff22
    if temp < 30: return 0xff9000
    if temp >= 30: return 0xff0000
    return 0x00ffff


def get_temp_tup(temp_entity:str, formatter="") -> tuple:
    temp:int = ha.get_state(temp_entity) # type: ignore
    if not temp:
        temp = 0
    temp = round(float(temp))
    temp_colour = get_colour_for_temp(temp)
    log.debug(f"Temp: {temp}, Colour: {temp_colour}")
    return (f"{temp:{formatter}}", temp_colour)


def get_temp_high() -> tuple:
    return get_temp_tup("input_number.today_high_temperature")


def get_temp_low() -> tuple:
    return get_temp_tup("input_number.today_low_temperature", formatter=">2")


def get_rain_chance_str() -> str:
    rain_chance:float = ha.get_state("input_number.today_precipitation_probability") # type: ignore
    if not rain_chance:
        rain_chance = 0
    rain_chance = round(float(rain_chance))
    return f"{rain_chance:>3}"
