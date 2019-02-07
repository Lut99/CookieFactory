#
# COOKIE FACTORY.py
#
# A simulation of a cookie factory.
# For a detailed explaination and changelog, see cookie_factory_doc.txt

# TODO:
#  - Make interface interface
#  - Add recipes and production chains (load done, add evaluation)
#  - Overhaul the rapport generator to leave more of the generating to the
#    modules, allowing easier rapport generating with variable modules
#  - Add Storage, Mixer and Oven

import threading
import time
import Modules
import numpy as np
import random

import Tools
from Tools import Date
from Tools import Worker
from Tools import Market
from Tools import ModulesList

Names = []
Items = []

# THE FACTORRRRYYY
class Factory (threading.Thread):
    # Init
    def __init__(self, name, budget, type, market):
        threading.Thread.__init__(self)
        self.name = name
        self.type = type
        self.market = market
        self.time = Date(0, 0, 0, 1970)
        # Init modules so we can pass a reference
        self.modules = ModulesList()
        # Add the basic objects
        self.modules.spawn(Modules.Office(budget, self.market, self.modules, self.time), special="office")
        self.modules.spawn(Modules.HumanResources(self.modules, self.time), special="hr")
        self.modules.spawn(Modules.Logistics(self.modules, self.time), special="logistics")
        self.modules.spawn(Modules.Depot(self.modules, self.time), special="depot")
        self.running = True

    # MAIN
    def run (self):
        self.log("Factory founded")
        ticked = []
        while self.running:
            # Do the work

            # Manage the worker's shift
            self.modules.hr.manage_shifts()

            # Make everyone work
            for m in self.modules:
                m.do_work(self.modules.hr.get_workers(module=m.name))

            if 'days' in ticked:
                # A day ended

                # Evaluate the workers
                self.modules.hr.evaluate()

                # Update construction
                self.modules.construct()

                # Call archive managers
                for m in self.modules:
                    if hasattr(m, 'manage_archive'):
                        m.manage_archive()

                time.sleep(.5)

            if 'months' in ticked:
                # A month ended

                # Fire, hire and pay new and / or old workers
                self.modules.hr.manage_workers([Worker() for i in range(10)])

                # Do the production chain evaluation
                self.modules.office.evaluate()
            if 'years' in ticked:
                # A year ended

                # Age up workers
                for w in self.modules.hr.workers:
                    w.celebrate_birthday()

            # Generate rapports
            #self.generate_rapport()

            # Increment the time
            ticked = self.time.tick()
        # Print the worker evaluations
        for w in self.modules.hr.workers:
            print(w.name + " (" + w.position.name + "): " + str(w.perfect / (self.time - w.started).todays()))


    # Threading functions
    def log (self, text):
        print(self.name + ": " + text)

    def stop (self):
        print("Closing factory...")
        self.running = False
        while self.isAlive():
            time.sleep(.1)
        print("The factory is successfully closed")
        print("Start    : {}".format(Date(0, 0, 0, 1970)))
        print("End      : {}".format(self.time))
        print("Duration : {} days".format((self.time - Date(0, 0, 0, 1970)).todays()))

    # Factory functions
    def generate_rapport(self):
        if self.time.hour == 0 and self.time.day == 0 and self.time.month == 11:
            # End-of-year rapport instead
            print("*** RAPPORT OF {:04d} ***".format(self.time.year))
            print("Products sold: " + str(self.modules.office.archive['sold']))
            print("Workers hired: " + str(self.modules.hr.archive['hired']))
            print("Workers fired: " + str(self.modules.hr.archive['fired']))
            print("Workers total: " + str(len(self.modules.hr.workers)))
            print("-----------------------------------")
            if len(self.modules.office.archive['daily_balances']) >= 2:
                revenue = self.modules.office.archive['daily_balances'][-1] - self.modules.office.archive['daily_balances'][0]
            else:
                revenue = "Undef"
            print("Revenue: " + str(revenue))
            print("Balance: " + str(self.modules.office.budget))
            print("***********************************\n")
            # Prepare the values for next year
            self.modules.office.archive['sold'] = 0
            self.modules.office.archive['daily_balances'] = []
            self.modules.hr.archive['hired'] = 0
            self.modules.hr.archive['fired'] = 0

# CODE
def main ():
    global Names
    global Items

    # Load the names & the items
    Names = Tools.load_csv("names.csv")
    print("Loaded the names ({} entries)".format(len(list(Names.values())[0])))
    Items = Tools.load_csv("items.csv")
    print("Loaded the items ({} entries)".format(len(list(Items.values())[0])))

    # Load the recipes
    Recipes = Tools.load_recipes("cookie_factory.recipes")
    ProductionChains = Tools.load_production_chains("cookie_factory.prodchains")

    cookie_factory = Factory("Cookie Inc.", 2000000, "cookie", Market(Items, Recipes, ProductionChains), Recipes, ProductionChains)
    cookie_factory.start()
    try:
        while True:
            print("Type a command:")
            command = input()
            if command == "quit":
                cookie_factory.stop()
                print("Factory closed")
                break
    except KeyboardInterrupt:
        print("")
        cookie_factory.stop()
        print("Factory interrupted")

if __name__ == "__main__":
    main()
