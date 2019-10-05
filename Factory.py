#
# COOKIE FACTORY.py
#   by tHE iNCREDIBLE mACHINE
#
# A simulation of a cookie factory.
# For a detailed explaination and changelog, see cookie_factory_doc.txt

# TODO:
#  - Add TCP connections etc to World.py
# See 'README.md' for the Roadmap for bigger stages in the upcoming development

import time
import Modules
import numpy as np
import random

import Tools
from Tools import Date
from Tools import Worker
from Tools import Market
from Tools import ModulesList
from Tools import NAMES as Names

# THE FACTORRRRYYY
class Factory ():
    # Init
    def __init__(self, name, budget, type, market, time):
        self.name = name
        self.type = type
        self.market = market
        self.time = time
        # Init modules so we can pass a reference
        self.modules = ModulesList(self.time)
        # Add the basic objects
        self.modules.spawn(Modules.Archive(self.name, self.modules, self.time), special="archive")
        self.modules.spawn(Modules.Office(budget, self.market, self.name, self.modules, self.time), special="office")
        self.modules.spawn(Modules.HumanResources(self.name, self.modules, self.time), special="hr")
        self.modules.spawn(Modules.Logistics(self.name, self.modules, self.time), special="logistics")
        self.modules.spawn(Modules.Depot(self.name, self.modules, self.time), special="depot")

        self.log("Factory founded")

    # MAIN
    def run (self, ticked):
        # An hour has ended

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

            # Check if any workers grew older
            for w in self.modules.hr.workers:
                if w.b_day.day == self.time.day and w.b_day.month == self.time.month:
                    w.celebrate_birthday()

        if 'months' in ticked:
            # A month ended

            # Fire, hire and pay new and / or old workers
            self.modules.hr.manage_workers([Worker(self.time) for i in range(10)])

            # Do the production chain evaluation
            self.modules.office.evaluate()
        if 'years' in ticked:
            # A year ended
            pass
        
        # Call archive managers
        self.modules.archive.manage(ticked)

    # Threading functions
    def log (self, text):
        Tools.CONSOLE.print("[" + self.name + "] " + text)

    def stop (self):
        self.log("Successfully closed")
        print("[" + self.name + "] Successfully closed")
        print(" > Start    : {}".format(Date(0, 0, 0, 1970)))
        print(" > End      : {}".format(self.time))
        print(" > Duration : {} days".format((self.time - Date(0, 0, 0, 1970)).todays()))

    # Factory functions

