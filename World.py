# WORLD.py
#   by tHE iNCREDIBLE mACHINE
#
# A script that hosts the factory world. It comes with a nice interface to keep
#   watch of everything happening.

import inspect
import argparse

import Tools
from Tools import Date
from Factory import Factory
import Modules
import Interface


def main (ip_address):
    # Initialize the general time
    time = Date()
    print("Initialized time object")

    # Open a server for interface connections
    connection_server = Interface.ConnectionServer(time, ip_address=ip_address)
    connection_server.start()
    connection_server.announce("Started ConnectionServer\n")

    # Construct the MODULES list in Tools
    modules_members = inspect.getmembers(Modules, lambda a:not(inspect.isroutine(a)))
    for attribute in [a for a in modules_members if not(a[0].startswith('__') and a[0].endswith('__'))]:
        clss = getattr(Modules, attribute[0])
        if inspect.isclass(clss) and clss != Modules.Module and issubclass(clss, Modules.Module):
            Tools.MODULES[clss.type] = clss
    connection_server.announce("Loaded the modules ({} entries)\n".format(len(modules_members)))

    # Load the names & the items
    Tools.NAMES = Tools.load_csv("resources/data/names.csv")
    connection_server.announce("Loaded the names ({} entries)\n".format(len(list(Tools.NAMES.values())[0])))
    Tools.ITEMS = Tools.load_csv("resources/data/items.csv")
    connection_server.announce("Loaded the items ({} entries)\n".format(len(list(Tools.ITEMS.values())[0])))

    # Load the Recipes and Production chains
    Tools.RECIPES = Tools.load_recipes("resources/data/cookie_factory.recipes", Tools.ITEMS)
    connection_server.announce("Loaded the recipes ({} entries)\n".format(len(Tools.RECIPES)))
    Tools.PRODUCTION_CHAINS = Tools.load_production_chains("resources/data/cookie_factory.prodchains")
    connection_server.announce("Loaded the production chains ({} entries)\n".format(len(Tools.PRODUCTION_CHAINS)))

    # Initialize the market
    market = Tools.Market(Tools.ITEMS, Tools.RECIPES, Tools.PRODUCTION_CHAINS)

    # Initialize the first factory
    factory = Factory("Cookie Factory, Inc.", 100000, "cookie", market, connection_server, time)

    # Run the loop
    while True:
        ticked = time.tick()
        factory.run(ticked)


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--whitelist", help="If given, only accepts interface connections on given IP")
    args = parser.parse_args()

    whitelist = ""
    if args.whitelist:
        whitelist = args.whitelist
        if whitelist != "localhost":
            # Check if it's okay
            ip_parts = whitelist.split(".")
            if len(ip_parts) != 4:
                raise ValueError("Given IP-address is not correctly formatted")
            # Check each segment
            for part in ip_parts:
                try:
                    part = int(part)
                except ValueError:
                    raise ValueError("Given IP-address is not correctly formatted")
                if part < 0 or part > 255:
                    raise ValueError("Given IP-address is not correctly formatted")

    main(whitelist)