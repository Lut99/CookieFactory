# WORLD.py
#   by tHE iNCREDIBLE mACHINE
#
# A script that hosts the factory world. It comes with a nice interface to keep
#   watch of everything happening.

import inspect

import Tools
from Tools import Market
from Tools import Date
from Tools import Command
import Factory
from Factory import Factory
import Modules

def main ():
    # Construct the MODULES list in Tools
    modules_members = inspect.getmembers(Modules, lambda a:not(inspect.isroutine(a)))
    for attribute in [a for a in modules_members if not(a[0].startswith('__') and a[0].endswith('__'))]:
        clss = getattr(Modules, attribute[0])
        if inspect.isclass(clss) and clss != Modules.Module and issubclass(clss, Modules.Module):
            Tools.MODULES[clss.type] = clss
    print("Loaded the modules ({} entries)".format(len(modules_members)))

    # Load the names & the items
    Tools.NAMES = Tools.load_csv("resources/data/names.csv")
    print("Loaded the names ({} entries)".format(len(list(Tools.NAMES.values())[0])))
    Tools.ITEMS = Tools.load_csv("resources/data/items.csv")
    print("Loaded the items ({} entries)".format(len(list(Tools.ITEMS.values())[0])))

    # Load the Recipes and Production chains
    Tools.RECIPES = Tools.load_recipes("resources/data/cookie_factory.recipes", Tools.ITEMS)
    print("Loaded the recipes ({} entries)".format(len(Tools.RECIPES)))
    Tools.PRODUCTION_CHAINS = Tools.load_production_chains("resources/data/cookie_factory.prodchains")
    print("Loaded the production chains ({} entries)".format(len(Tools.PRODUCTION_CHAINS)))

    # Init Console instance
    Tools.CONSOLE = Tools.Console()

    # Do the interface
    

if __name__ == "__main__":
    main()