"""
    GLOBALs.py
        by tHE iNCREDIBLE mACHINE

    DESCRIPTION: File that keeps track of global constants and variables across
                 the program. Also initializes some globals upon running.
"""

import uuid

# Declare the UUID list that keeps track of the UUID
UUID_MAP = {}
# Placeholders for...
# ...the World's Connection Server
CONNECTION_SERVER = None
# ...the World's Time Object
TIME = None
# ...the market
MARKET = None
# ...the World's ModulesList
MODULES_LIST = None
# ...all the names
NAMES = None
# ...all the items
ITEMS = None
# ...all the recipes
RECIPES = None
# ...all the production chains
PRODUCTION_CHAINS = None


# Function that creates and registers a new source
def register_uuid(name):
    # Create a UUID
    uid = str(uuid.uuid1())
    # Register and return it
    UUID_MAP[name] = uid
    return uid
