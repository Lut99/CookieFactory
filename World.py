# WORLD.py
#   by tHE iNCREDIBLE mACHINE
#
# A script that hosts the factory world. It comes with a nice interface to keep
#   watch of everything happening.

import inspect
import argparse
import uuid

import Tools
from Tools import Date
import Modules
import Interface
import Terminal


def main (ip_address):
    # Open a server for interface connections
    connection_server = Interface.ConnectionServer(ip_address=ip_address)
    connection_server.start()

    # Initialize the general time
    time = Date()
    print("Initialized time object")

    # Create the Terminal
    term = Terminal.Terminal(connection_server, time)

    # Construct the MODULES list in Tools
    modules_members = inspect.getmembers(Modules, lambda a:not(inspect.isroutine(a)))
    for attribute in [a for a in modules_members if not(a[0].startswith('__') and a[0].endswith('__'))]:
        clss = getattr(Modules, attribute[0])
        if inspect.isclass(clss) and clss != Modules.Module and issubclass(clss, Modules.Module):
            Tools.MODULES[clss.type] = clss
    term.print("Loaded the modules ({} entries)".format(len(modules_members)))

    # Load the names & the items
    Tools.NAMES = Tools.load_csv("resources/data/names.csv")
    term.print("Loaded the names ({} entries)".format(len(list(Tools.NAMES.values())[0])))
    Tools.ITEMS = Tools.load_csv("resources/data/items.csv")
    term.print("Loaded the items ({} entries)".format(len(list(Tools.ITEMS.values())[0])))

    # Load the Recipes and Production chains
    Tools.RECIPES = Tools.load_recipes("resources/data/cookie_factory.recipes", Tools.ITEMS)
    term.print("Loaded the recipes ({} entries)".format(len(Tools.RECIPES)))
    Tools.PRODUCTION_CHAINS = Tools.load_production_chains("resources/data/cookie_factory.prodchains")
    term.print("Loaded the production chains ({} entries)".format(len(Tools.PRODUCTION_CHAINS)))


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