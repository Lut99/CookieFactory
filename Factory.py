#
# COOKIE FACTORY.py
#   by tHE iNCREDIBLE mACHINE
#
# A simulation of a cookie factory.
# For a detailed explaination and changelog, see cookie_factory_doc.txt

# TODO:
#  - Fix weird key error bug in Modules > Human Resources > Manage workers
#  - Overhaul Human Resources?
# See 'README.md' for the Roadmap for bigger stages in the upcoming development

import Modules
from Tools import ModulesList
from Tools import Worker
import Globals
from Globals import register_uuid


# THE FACTORRRRYYY
class Factory():
    """ The Factory class. """
    # Init
    def __init__(self, name, budget, type_):
        self.name = name
        self.type = type_

        # Create a uuid
        self.uuid = register_uuid(self.name)

        # Init modules so we can pass a reference
        self.modules = ModulesList(self.uuid)
        # Add the basic objects
        self.modules.spawn(Modules.Archive(self.name, self.modules), special="archive")
        self.modules.spawn(Modules.Office(budget, self.name, self.modules), special="office")
        self.modules.spawn(Modules.HumanResources(self.name, self.modules), special="hr")
        self.modules.spawn(Modules.Logistics(self.name, self.modules), special="logistics")
        self.modules.spawn(Modules.Depot(self.name, self.modules), special="depot")

        self.time = Globals.TIME

        self.log("Factory founded")

    # MAIN
    def run(self, ticked):
        """
            Is called after each simulated hour, to run the factory processes.
        """

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
            self.modules.hr.manage_workers([Worker() for i in range(10)])

            # Do the production chain evaluation
            self.modules.office.evaluate()
        if 'years' in ticked:
            # A year ended
            pass

        # Call archive managers
        self.modules.archive.manage(ticked)

    # Threading functions
    def log(self, text, end="\n"):
        """
            Logs over the internal connection server.
        """

        if type(text) != str:
            text = str(text)

        Globals.CONNECTION_SERVER.announce(text + end, origin=self.uuid)

    def stop(self):
        """ Stops the Factory """
        self.log("Successfully closed")
