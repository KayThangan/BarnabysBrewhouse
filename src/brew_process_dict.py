"""
This module is a program that simulates anything to do with tanks. Such
as allocating and releasing tanks. Also, storing each tanks
specification.
"""
from brew_logger import errorLogger, eventLogger

errorLogger = errorLogger()
eventLogger = eventLogger()

def update_tank_used_capacity(tank_name: str, volume: int):
    """
    This method updates the used_capacity in the TANKS dictionary.
    :param tank_name: a string containing the name of the tank.
    :param volume: an integer of the tank's volume.
    """
    errorLogger.info("Updating the used capacity in the TANKS "
                     "dictionary.")
    TANKS.update({
        tank_name: {
            "volume": TANKS[tank_name]["volume"],
            "capability": TANKS[tank_name]["capability"],
            "used_capacity": volume
        }
    })
    eventLogger.critical("@tanks : @%s", TANKS)

def get_tank_for_capability(capability: str, volume: int) -> str:
    """
    This method gets the capability of a tank.
    :param capability: a string of the capability.
    :param volume: an integer of the tank's volume.
    :return tank: a string of the tank's name.
    """
    errorLogger.info("Getting a tank that is compatible with the "
                     "capability.")
    for tank in TANKS:
        if capability in TANKS[tank]["capability"]:
            if volume <= TANKS[tank]["volume"] and \
                    TANKS[tank]["used_capacity"] == 0:
                update_tank_used_capacity(tank, volume)
                return tank
    return None

def allocate_tank(capability: str, quantity: int) -> str:
    """
    This function allocates tanks for a given capability.
    :param capability: a string of the tank's capability.
    :param quantity: an integer of the beer quantity.
    :return: a string of the tank.
    """
    errorLogger.info("Allocating a tank.")
    volume = quantity * 0.5
    if capability == "hot_brew":
        return "Kettle"
    elif capability == "fermentation":
        return get_tank_for_capability("fermenter", volume)
    elif capability == "conditioning":
        return get_tank_for_capability("conditioner", volume)
    elif capability == "bottling":
        return "bottling"
    return None

def release_tank(tank: str):
    """
    This allow to release tank.
    :param tank: a string representing the tank's name.
    :return: boolean
    """
    errorLogger.info("Releasing a tank.")
    TANKS.update({
        tank: {
            "volume": TANKS[tank]["volume"],
            "capability": TANKS[tank]["capability"],
            "used_capacity": 0
        }
    })
    eventLogger.critical("@tanks : @%s", TANKS)
    return True

def tank_status() -> dict:
    """
    Gets the TANKS' status.
    :return: a dictionary of the TANKS.
    """
    errorLogger.info("Getting the tanks' status.")
    return TANKS

TANKS = {
    "Gertrude": {
        "volume": 680,
        "capability": ["conditioner"],
        "used_capacity": 0
    },
    "Harry": {
        "volume": 680,
        "capability": ["conditioner"],
        "used_capacity": 0
    },
    "R2D2": {
        "volume": 800,
        "capability": ["fermenter"],
        "used_capacity": 0
    },
    "Brigadier": {
        "volume": 800,
        "capability": ["fermenter", "conditioner"],
        "used_capacity": 0
    },
    "Florence": {
        "volume": 800,
        "capability": ["fermenter", "conditioner"],
        "used_capacity": 0
    },
    "Dylon": {
        "volume": 800,
        "capability": ["fermenter", "conditioner"],
        "used_capacity": 0
    },
    "Albert": {
        "volume": 1000,
        "capability": ["fermenter", "conditioner"],
        "used_capacity": 0
    },
    "Camilla": {
        "volume": 1000,
        "capability": ["fermenter", "conditioner"],
        "used_capacity": 0
    },
    "Emily": {
        "volume": 1000,
        "capability": ["fermenter", "conditioner"],
        "used_capacity": 0
    }
}

beer_stock = {}

def update_beer_stock(beer_name: str, quantity: int):
    """
    This method updates the current beer stock.
    :param beer_name: a string of the beer name.
    :param quantity: an integer representing the quantity of beer.
    :return:
    """
    errorLogger.info("Updating the beer stock.")
    temp = 0
    try:
        if beer_stock[beer_name]:
            temp = beer_stock[beer_name] + quantity
    except:
        temp = quantity
    beer_stock.update({beer_name: temp})
    eventLogger.critical("@stock : @%s", beer_stock)

def beer_stock_status():
    """
    Getting the beer stock status.
    :return beer_stock: a dictionary of the beer stock.
    """
    errorLogger.info("Retrieving the status of the beer stock.")
    return beer_stock
