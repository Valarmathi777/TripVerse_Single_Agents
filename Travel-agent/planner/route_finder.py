from config import PREFERENCE_WEIGHTS, ECO_MODES, TAXI_CAPACITY
from api.weather import weather_blocks_transport

def filter_options(options: list, budget: float, group_size: int, weather: dict) -> list:
    valid = []
    for opt in options:
        if opt["cost"] > budget:
            continue
        if not opt["availability"]:
            continue
        if weather_blocks_transport(weather, opt["mode"].lower()):
            continue
        if opt["mode"].lower() == "taxi" and group_size > TAXI_CAPACITY:
            continue
        valid.append(opt)
    return valid
