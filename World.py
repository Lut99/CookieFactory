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
import Globals


def main(ip_address):
    # Initialize the general time
    Globals.TIME = Date()
    print("Initialized time object")

    # Open a server for interface connections
    connection_server = Interface.ConnectionServer(ip_address=ip_address)
    connection_server.start()
    connection_server.announce("Started ConnectionServer\n")
    Globals.CONNECTION_SERVER = connection_server

    try:
        # Construct the MODULES list in Tools
        modules_list = {}
        modules_members = inspect.getmembers(Modules, lambda a: not(inspect.isroutine(a)))
        for attribute in [a for a in modules_members if not(a[0].startswith('__') and a[0].endswith('__'))]:
            clss = getattr(Modules, attribute[0])
            if inspect.isclass(clss) and clss != Modules.Module and issubclass(clss, Modules.Module):
                modules_list[attribute[0]] = clss
        Globals.MODULES_LIST = modules_list
        connection_server.announce(f"Loaded the modules ({len(modules_list)} entries)\n")
        print(Globals.MODULES_LIST)

        # Load the names & the items
        Globals.NAMES = Tools.load_csv("resources/data/names.csv")
        connection_server.announce(f"Loaded the names ({len(list(Globals.NAMES.values())[0])} entries)\n")
        Globals.ITEMS = Tools.load_csv("resources/data/items.csv")
        connection_server.announce(f"Loaded the items ({len(list(Globals.ITEMS.values())[0])} entries)\n")

        # Load the Recipes and Production chains
        Globals.RECIPES = Tools.load_recipes("resources/data/cookie_factory.recipes")
        connection_server.announce(f"Loaded the recipes ({len(Globals.RECIPES)} entries)\n")
        Globals.PRODUCTION_CHAINS = Tools.load_production_chains("resources/data/cookie_factory.prodchains")
        connection_server.announce(f"Loaded the production chains ({len(Globals.PRODUCTION_CHAINS)} entries)\n")

        # Initialize the market
        market = Tools.Market()
        Globals.MARKET = market

        # Initialize the first factory
        factory = Factory("Cookie Factory, Inc.", 100000, "cookie")

        # Run the loop
        while Globals.TIME.year < 100:
            ticked = Globals.TIME.tick()
            if 'years' in ticked:
                print(f"*** NEW YEAR {Globals.TIME.year} ***")
            factory.run(ticked)
    finally:
        # Stop everything required
        connection_server.stop()


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
