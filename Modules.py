#
# MODULES.py
#
# Part of the Factory. Contains all classes representing modules for factories
#   to purchase so they can make additional or more stuff.

import random

import APIs.calculator as calculator
import Tools
from Tools import Date
from Tools import Position
import Globals
from Globals import register_uuid


class Storage ():
    """
        A place for modules to store items in. Additionally, can use rules to
        employ the Logistics System to move goods in an automated fashion.
    """

    class Rule ():
        """
            Defines a rule used to determine what goes in and out of this
            Storage
        """

        In = "__IN"
        Out = "__OUT"
        InOut = "__IN_OUT"

        def __init__(self, item, target_stored="[max]", flow=InOut, target_modules=["*"], anti_target_modules=["depot"]):
            self.item = item
            # Allow the module to enter a variable target (e.g. [max]/2)
            self.form = calculator.parse(target_stored, verbose=False)
            self.flow = flow
            self.target_modules = target_modules
            self.anti_target_modules = anti_target_modules

    def __init__(self, max=5000):
        self._storage = {}
        self.rules = {}
        self.max = max
        self.total = 0

    def add_rule(self, id_, rule):
        """ Add a routing rule """
        self.rules[id_] = rule

    def get_rule(self, id_):
        """ Gets a routing rule with a certain ID """
        if id_ not in self.rules:
            return None
        return self.rules[id_]

    def remove_rule(self, id_):
        """ Removes a rule with a certain ID """
        self.rules.pop(id_, None)

    def __getitem__(self, key):
        """
            Grants access to the internal storage. Returns '0' if the item is
            not present in this storage.
        """

        if key not in self._storage:
            return 0
        return self._storage[key]

    def store(self, item, amount):
        """
            Adds X items of given type to the store. If more than the maximum
            is added, the amount that wouldn't fit is returned.
        """

        if item not in self._storage:
            # If we're already at maximum, return the amount as the overflow
            #   (nothing fits)
            if self.stored == self.max:
                return amount
            # Init new item
            self._storage[item] = 0
        # Compute the overflow
        overflow = (self.total + amount) - self.max
        if overflow < 0:
            overflow = 0
        # Store the amount
        self._storage[item] += amount - overflow
        self.total += amount - overflow
        return overflow

    def retrieve(self, item, amount):
        """
            Gets (and removes) given amount of given item from storage. Returns
            the actual amount retrieved.
        """

        # If the item doesn't exist, we cannot retrieve anything
        if item not in self._storage:
            return 0
        # Compute the underflow
        underflow = amount - self._storage[item]
        if underflow < 0:
            underflow = 0
        # Get the amount
        self._storage[item] -= amount - underflow
        self.total -= amount - underflow
        return amount - underflow

    # TODO: Allow requesting storage data over the network (prolly need new CFNP entry)


class Module ():
    """
        Abstract for a Module. Already handles storing and initializing of
        some variables, as well as general do_work() and log() functions.
    """

    def __init__(self, name, cost, positions, factory_name, construction_time, modules):
        self.name = name
        self.cost = cost
        self.construction_time = construction_time
        self.positions = positions
        # Do a quick check for duplicate instances
        ps = []
        for p in self.positions:
            if p in ps:
                raise ValueError("Can only contain positions that are separate instances")
            ps.append(p)

        self.work_done = 0
        self.founded = Globals.TIME.now()
        self.factory_name = factory_name
        self.modules = modules

        # Also generate a unique identifier
        self.uuid = register_uuid(self.name)

        # Store references to some globals
        self.connection_server = Globals.CONNECTION_SERVER
        self.time = Globals.TIME

    def do_work(self, workers):
        """
            Lets all (given) workers do the work they were hired to do, and
            collect that in the work pool.
        """

        for w in workers:
            # Get the workload
            self.work_done += w.work()

    def log(self, text, end="\n"):
        """ Logs on the connection_server """
        if type(text) != str:
            text = str(text)
        self.connection_server.announce(text + end, origin=self.uuid)


# ADMINISTRATIVE MODULES

# Basic to any factory: manages money, houses the boss
class Office (Module):
    """ Manages the factory, both stragetically as economically. """
    def __init__(self, budget, factory_name, modules):
        super().__init__("Headquarters (HQ)", 0, [Position(
            name="CEO",
            workload=2,
            salary=100,
            schedule=[9, 17],
            education_level=3
        )], factory_name, Date(0, 0, 0, 0), modules)

        # Init the type of the module
        self.type = "Office"

        # Store the budget and the market
        self.budget = budget
        self.market = Globals.MARKET
        # Prepare the production chains
        self.production_chains = []
        # Do the archive
        self.modules.archive.add_cabinet("General")
        self.modules.archive.set("General", "Founded", self.time.now())

        self.modules.archive.add_cabinet("Finance")
        self.modules.archive.set("Finance", "Total Sold", 0)
        self.modules.archive.set("Finance", "Daily Balances", [])
        self.modules.archive.set("Finance", "Yearly Balances", [])

        self.modules.archive.add_tick(self.manage_archive)

    def check_balance(self):
        """ Returns the amount of money the factory has left to spend """
        return self.budget

    def deposit(self, amount):
        """ Stores a given amount of money to the factory's accounts """
        self.budget += amount

    def pay(self, amount):
        """
            Subtract a given amount from the factory's accounts. Returns how
            many is paid if the server has enough budget, or else 0.
        """

        if self.budget >= amount:
            self.budget -= amount
            return amount
        return 0

    def buy_resources(self, item, amount):
        """
            Attempts to buy the given amount of the given item from the global
            market. Tries to buy as much as possible, and returns the number of
            items actually bought.
        """

        # Pay until we get to an amount we can buy
        if item not in self.market.buy_list:
            # Cannot buy
            self.log(f"Attempted to buy unexisting item from market: {item}")
            return 0
        price = self.market.buy_list[item]
        # Compute the maximum amount we can buy
        max_amount = self.budget // price
        if amount > max_amount:
            amount = max_amount
        # Now get the money from the budget and use that to buy the items
        return self.market.buy(item, amount, self.pay(price * amount))

    # Sell resources
    def sell_resources(self, item, amount):
        """ Sell the given amount of the given item to the market """
        self.deposit(self.market.sell(item, amount))
        # Manage the counter for the archive
        self.modules.archive.update('Finance', 'Total Sold', 1)

    # Evaluate if we need more production chains
    def evaluate(self):
        """ Function that will decide important factory processes. TBD. """
        if len(self.production_chains) == 0:
            pass

    # Archive certain stats
    @staticmethod
    def manage_archive(modules, ticked):
        """ Periodically updates the archive. """
        if 'days' in ticked:
            # New day
            modules.archive.update('Finance', 'Daily Balances', modules.office.check_balance())
            if 'years' in ticked:
                # New year
                modules.archive.update('Finance', 'Yearly Balances', modules.office.check_balance())


# Can be purchased to research new recipes and modules.
class Research (Module):
    type = "research"

    def __init__(self):
        super().__init__()


# A requirement for any factory. Manages staff and salaries.
class HumanResources (Module):
    """
        Manages the workers in the factory, including pay, hiring and fireing,
        and levelling.
    """

    def __init__(self, factory_name, modules):
        super().__init__("Human Resources (HR)", 0, [Position(
            name="Recruiter",
            workload=1,
            salary=50,
            schedule=[9, 17],
            education_level=1
        ) for i in range(5)], factory_name, Date(0, 0, 0, 0), modules)

        self.type = "HumanResources"

        self.workers = []

        # Initialise the archive
        self.modules.archive.add_cabinet("Workers")
        self.modules.archive.set("Workers", "History", [])
        self.modules.archive.set("Workers", "Hired", 0)
        self.modules.archive.set("Workers", "Fired", 0)

    # Counts position in a module
    def count_positions(self, positions, position):
        """
            Returns the number of available positions of the given type in the
            given module.
        """

        c = 0
        for p in positions:
            if p.worker is None and p.name == position:
                c += 1
        return c

    def manage_workers(self, available_workers):
        """
            Hires and fires workers in the ModulesList. Also handles the pay.
            Reasons for fireing could be because a worker quits (no salary
            paid), a worker is too old (pension) or a worker hasn't worked
            enough.
            Additionally, for each worker in HR, we can hire a new worker for
            another module each hiring wave.
        """

        # Loop trough each module and decide what's best
        for m in self.modules:
            # Assemble the positions
            can_hire = True
            for p in m.positions:
                if p.worker:
                    w = p.worker
                    # Try to pay him
                    if self.modules.office.pay(w.salary):
                        w.no_salary = 0
                    else:
                        # We couldn't pay the poor guy
                        w.no_salary += 1
                    # Check to see if we should FIRE him
                    if w.age > 67:
                        # Fire bc he's too old
                        self.fire(w, "pension age")
                    elif w.no_salary == 4:
                        # Didn't pay him enough
                        self.fire(w, "not paid enough")
                    elif w.no_salary == 0 and w.perfect / (self.time - w.started).todays() < 0.5:
                        # Didn't work enough
                        self.fire(w, "low performance")
                elif can_hire and len(available_workers) > 0 and (m == self or self.work_done > 0):
                    # We found a spot! Hire someone if:
                    #   - We haven't hired someone for this module already (to
                    #     prevent one module swallowing all workers)
                    #   - There are workers available
                    #   - We still have work that can be done (and it's not HR)
                    w = random.choice(available_workers)
                    if self.hire(w, m, p):
                        if m != self:
                            # Hiring for HR is free
                            self.work_done -= 1
                        available_workers.remove(w)
                        can_hire = False
        # Before we quit, remove any workers that have invalid positions
        for w in self.workers:
            if w.position not in w.module.positions:
                # The worker's position has been removed
                self.fire(w, "too many workers")

    def manage_shifts(self):
        """
            Puts workers on and off duty according to the shifts in the
            schedule.
        """

        for w in self.workers:
            if self.time.hour == w.position.schedule[0] - 1:
                # Put the worker on duty
                w.on_duty = True
            elif self.time.hour == w.position.schedule[1] - 1:
                # Put the worker off-duty
                w.on_duty = False
                # Make him sleep
                w.sleep()

    # Called at the end of a day to evaluate workers
    def evaluate(self):
        """ Check if any workers went level up """
        for w in self.workers:
            if w.energy > 0:
                w.perfect += 1
                # Also level up the worker
                w.level_up()

    def hire(self, worker, module, position):
        """
            Hires a worker for a given module and a given position, but only
            if the worker meets the specified requirements
        """

        if worker.stats.education_level >= position.education_level:
            # Hire him / her
            worker.module = module
            worker.position = position
            position.worker = worker
            worker.started = self.time.now()
            worker.perfect = 0
            worker.salary = position.salary
            self.workers.append(worker)
            self.modules.archive.update("Workers", "Hired", 1)
            self.log(f"Hired {worker.name} (age {worker.age}) to work in {module.name} as {position.name}")
            return True
        return False

    def fire(self, worker, reason):
        """ Fires a worker for a given reason """
        # Remove the worker
        self.workers.remove(worker)
        worker.position.worker = None
        # Now add his name and reason for fireing
        self.modules.archive.update("Workers", "History", {
            'name': worker.name,
            'module': worker.module.name,
            'position': worker.position.name,
            'days_employed': (self.time - worker.started).todays(),
            'reason': reason
        })
        self.modules.archive.update("Workers", "Fired", 1)
        self.log(f"Fired {worker.name} from {worker.module.name} because {reason}")

    def get_worker(self, name):
        """ Returns a worker with the given name """
        # Loop through the workers
        for w in self.workers:
            if w.name == name:
                return w
        return None

    def get_workers(self, module="*", position="*"):
        """
            Returns all workers working in a specific model and / or position
        """

        # Assemble all workers with the module
        to_return = []
        for w in self.workers:
            if (w.module == module or module == "*") and (w.position == position or position == "*"):
                to_return.append(w)
        return to_return


# Manages resource flow
class Logistics (Module):
    """
        Moves items around in the factory, and is therefore the backbone
        of the process.
    """

    def __init__(self, factory_name, modules):
        super().__init__("Logistics", 0, [Position(
            name="Manager",
            workload=2,
            salary=300,
            schedule=[9, 17],
            education_level=1
        )], factory_name, Date(0, 0, 0, 0), modules)
        # Add some additional positions
        for _ in range(10):
            self.positions.append(Position(
                name="Forklift Operator",
                workload=1,
                salary=200,
                schedule=[9, 17],
                education_level=1
            ))
        # Set the amount that can be hauled per forktruck
        self.max_haul = 50

        self.type = "Logistics"

    # Override to do work
    def do_work(self, workers):
        """
            Does the logistics. The system adheres to the following rules:
              - For every module with a storage (that isn't the depot):
                - Check which rules are present
                - Determine how much we can take from that module
                - Determine how much that module requests
              - Then, try to resolve each request with what we can take from
                modules
              - If a match has been found, haul it using a worker's workforce
              - Then, do the remainder of the request using the depot
                - ...unless a module has specifically blacklisted / not
                  whitelisted it
        """

        if len(workers) == 0:
            # Nothing to do if no workers are present
            return
        # For every rule in every valid storage, do...
        requests = []
        offers = []
        for m in self.modules:
            if hasattr(m, 'storage') and m.type != "depot":
                for r in m.storage.rules:
                    rule = m.storage.rules[r]
                    # Get the target value
                    target = rule.form.calc({'max':m.storage.max})
                    if (rule.flow == Storage.Rule.InOut or rule.flow == Storage.Rule.In) and m.storage[rule.item] < target:
                        # Add it
                        requests.append({
                            'module': m,
                            'targets': rule.target_modules,
                            'antitargets': rule.anti_target_modules,
                            'item': rule.item,
                            'amount': target - m.storage[rule.item]
                        })
                    if (rule.flow == Storage.Rule.InOut or rule.flow == Storage.Rule.Out) and m.storage[rule.item] > target:
                        # Add it
                        offers.append({
                            'module': m,
                            'targets': rule.target_modules,
                            'antitargets': rule.anti_target_modules,
                            'item': rule.item,
                            'amount': m.storage[rule.item] - target
                        })

        # Now drive (not to the depot, do that afterwards)
        worker = 0
        requests_overflow = []
        while len(requests) > 0:
            r = requests[0]
            requests = requests[1:]
            # Find a possible matching offer
            check = True
            for o in offers:
                if self.isTarget(r, o) and self.isTarget(o, r):
                    # Transport!
                    hauled = self.transport(o['module'].storage, r['module'].storage, r['item'], r['amount'], self.max_haul * workers[worker].work())
                    r['amount'] -= hauled
                    o['amount'] -= hauled
                    if r['amount'] > 0:
                        requests.append(r)
                    if o['amount'] == 0:
                        offers.remove(o)
                    if hauled > 0: worker += 1
                    if worker >= len(workers):
                        # No more workers :(
                        return
                    break
            if check:
                # Put it in the overflow back instead
                requests_overflow.append(r)

        # Handle the depot (first buys...)
        while len(requests_overflow) > 0:
            r = requests_overflow[0]
            requests_overflow = requests_overflow[1:]
            # Buy it from the depot if it's in their rule
            if 'depot' in r['targets'] or ('*' in r['targets'] and
                                           'depot' not in r['antitargets']):
                # Transport!
                hauled = self.transport(self.modules.depot, r['module'].storage, r['item'], r['amount'], self.max_haul * workers[worker].work())
                r['amount'] -= hauled
                if r['amount'] > 0:
                    requests_overflow.append(r)
                worker += 1
                if worker >= len(workers):
                    # No more workers :(
                    return
            else:
                requests_overflow.append(r)
        # (...then sales)
        while len(offers) > 0:
            o = offers[0]
            offers = offers[1:]
            # Sell it to the depot if it's in their rule
            if 'depot' in o.target_modules or ('*' in o.target_modules and
                                               'depot' not in o.anti_target_modules):
                # Transport!
                hauled = self.transport(o['module'].storage, self.modules.depot, r['item'], r['amount'], self.max_haul * workers[worker].work())
                o['amount'] -= hauled
                if o['amount'] > 0:
                    offers.append(r)
                worker += 1
                if worker >= len(workers):
                    # No more workers :(
                    return
            else:
                offers.append(o)

    def isTarget(self, request, offer):
        """ Checks whether offer is in the target range of request """
        return (
            (request['item'] == offer['item'] or offer['item'] == "*") and
            (offer['module'].name in request.target_modules or
             offer['module'].type in request.target_modules or
             "*" in request.target_modules) and
            (offer['module'].name not in request.anti_target_modules and
             offer['module'].type not in request.anti_target_modules and
             "*" not in request.anti_target_modules) and
            request['module'].name != offer['module'].name
        )

    # Does the physical transport
    def transport(self, storage_from, storage_to, item, amount, max):
        """
            Transport given amount with the given amount from one storage to
            the other
        """

        # It's a match, transport
        to_transport = amount if amount < max else max
        got = storage_from.retrieve(item, to_transport)
        # Store it
        overflow = storage_to.store(item, got)
        # Return the overflow
        storage_from.store(item, overflow)
        # Return that which we have successfuly stored
        return got - overflow


# Serves as the connection between the factory and the (global) market.
class Depot (Module):
    """
        Server as the Factory's outgoing connection to and from the market.
    """

    def __init__(self, factory_name, modules):
        super().__init__("Depot", 0, [Position(
            name="Truck Driver",
            workload=2,
            salary=300,
            schedule=[9, 17],
            education_level=1
        ) for i in range(10)], factory_name, Date(0, 0, 0, 0), modules)

        # Init the storage
        self.storage = Storage(max=float('inf'))

        # Do the trucks
        self.trucks = []

        # Set the truck max
        self.truck_max = 500

        self.type = "Depot"

    def do_work(self, workers):
        """ Overrides do_work to man the trucks instead """
        for w in workers:
            work = w.work()
            if work > 0:
                self.trucks.append(int(self.truck_max * (2 / (1 / work))))

    def store(self, item, amount):
        """ Stores a new item, aka: sells it onto the market """
        # Sell these items
        for truck in self.trucks:
            shipped = truck
            if shipped > amount:
                shipped = amount
            self.modules.office.sell_resources(item, shipped)
            amount -= shipped
        # Return that which we could not transport
        return amount

    def retrieve(self, item, amount):
        """ Retrieves an item from the market, aka: buys it """
        bought = 0
        for truck in self.trucks:
            # Attempt to buy the resources
            shipped = truck
            if shipped > amount:
                shipped = amount
            amount -= shipped
            bought += self.modules.office.buy_resources(item, shipped)
        # Return the items bought instead
        return bought


# Saves all sort of stats about the factory
class Archive (Module):
    """
        The Archive records all sort of information about the factory, and is
        useful for debugging and making Factory decisions for the Office.
    """

    def __init__(self, factory_name, modules):
        super().__init__("Archive", 0, [Position(
            name="Clerk",
            workload=0,
            salary=500,
            schedule=[9, 17],
            education_level=2
        ) for _ in range(5)], factory_name, Date(0, 0, 0, 0), modules)

        # Init the _cabinets list
        self._cabinets = {}
        # Init the _ticks list
        self._ticks = []

        self.type = "Archive"

        # Done

    def add_cabinet(self, name):
        """ Creates a new cabinet for a module to log information in. """
        if name in self._cabinets:
            self.log(f"Attempting to add cabinet that already exists: {name}")
            return False

        self._cabinets[name] = {}
        return True

    def remove_cabinet(self, name):
        """ Removes a cabinet for a module. """
        if name not in self._cabinets:
            self.log(f"Attempting to remove cabinet that does not exists: {name}")
            return False

        del self._cabinets[name]
        return True

    def add_tick(self, tick_handler):
        """ Register a tick handler that gets called every time tick """
        self._ticks.append(tick_handler)

    def remove_tick(self, tick_handler):
        """ Unregister a tick handler that gets called every time tick """
        self._ticks.remove(tick_handler)

    def manage(self, ticked):
        """ Handles all ticks. Can only do one tick for each clerk hired. """
        for tick_handler in self._ticks:
            tick_handler(self.modules, ticked)

    def set(self, cabinet, shelf, value):
        """ Set the value of a certain shelf within a cabinet. """
        if cabinet not in self._cabinets:
            Tools.CONSOLE.print("[Archive] Attempting to log in non-existing cabinet '{}'".format(cabinet))
            return False
        self._cabinets[cabinet][shelf] = value
        return True

    def get(self, cabinet, shelf):
        """ Gets the value of a certain shelf within a cabinet """
        if cabinet not in self._cabinets:
            self.log(f"Attempting to retrieve from non-existing cabinet '{cabinet}'")
            return None
        if shelf not in self._cabinets[cabinet]:
            self.log(f"Attempting to retrieve from non-existing shelf '{shelf}' in cabinet '{cabinet}'")
            return None
        return self._cabinets[cabinet][shelf]

    # Updates in a clever way
    def update(self, cabinet, shelf, d_value):
        """
            Updates a certain shelf in a certain cabinet in a type-dependent
            way. The types are:
              - Strings (gets concatenated)
              - Integers (gets added)
              - Float (gets added)
              - Lists (get appended)
              - Dictionary (sets the key to the value)
        """

        if cabinet not in self._cabinets:
            self.log(f"Attempting to update non-existing cabinet '{cabinet}'")
            return False
        if shelf not in self._cabinets[cabinet]:
            self.log(f"Attempting to update non-existing shelf '{shelf}' in cabinet '{cabinet}'")
            return False
        # Check that shelf type
        shelf_type = type(self._cabinets[cabinet][shelf])
        if shelf_type == str:
            if type(d_value) != str:
                d_value = str(d_value)
            self._cabinets[cabinet][shelf] += d_value
        elif shelf_type == int:
            if type(d_value) != int:
                self.log(f"Attempting to update shelf '{shelf}' (integer) in cabinet '{cabinet}' with '{d_value}' ({type(d_value)})")
                return False
            self._cabinets[cabinet][shelf] += d_value
        elif shelf_type == float:
            if type(d_value) != int and type(d_value) != float:
                self.log(f"Attempting to update shelf '{shelf}' (float) in cabinet '{cabinet}' with '{d_value}' ({type(d_value)})")
                return False
            self._cabinets[cabinet][shelf] += d_value
        elif shelf_type == list:
            if type(d_value) == list:
                self._cabinets[cabinet][shelf] += d_value
            else:
                self._cabinets[cabinet][shelf].append(d_value)
        elif shelf_type == dict:
            if type(d_value) != tuple or len(d_value) != 2:
                self.log(f"Attempting to update shelf '{shelf}' (dictionary) in cabinet '{cabinet}', but without given key / value tuple")
                return False
            self._cabinets[cabinet][shelf][d_value[0]] = d_value[1]
        else:
            self.log(f"Attempting to update shelf '{shelf}' in cabinet '{cabinet}', but that value is static")
            return False
        return True

    def empty(self, cabinet, shelf):
        """ Cleans out a shelf in the given cabinet """
        if cabinet not in self._cabinets:
            self.log(f"Attempting to clean non-existing cabinet '{cabinet}'")
            return False
        if shelf not in self._cabinets[cabinet]:
            self.log(f"Attempting to clean non-existing shelf '{shelf}' in cabinet '{cabinet}'")
            return False
        del self._cabinets[cabinet][shelf]
        return True


# *** OPTIONAL ***
# If the factory researched enough, they can unlock robots: cheaper, faster and
#   mostly less-complaining workers. They are managed in this module.
class RobotResources (Module):
    type = "robot_resources"

    def __init__(self):
        super().__init__()


# COOKIE MODULES
# Stores stuff
class StoreRoom (Module):
    type = "store_room"

    def __init__(self):
        super().__init__()


# A Mixer, which can mix stuff.
class Mixer (Module):
    type = "mixer"
    recipe_fields = [('Inputs', dict), ('Outputs', dict)]

    def __init__(self):
        super().__init__()


# An oven, which can heat stuff
class Oven (Module):
    type = "oven"
    recipe_fields = [('Inputs', dict), ('Outputs', dict), ('BakeTemp', int), ('BakeDuration', int)]

    def __init__(self):
        super().__init__()


# OTHER MODULES
# Test module
class SimpleProcessingUnit (Module):
    def __init__(self, name, modules):
        super().__init__(name, "simple_processing_unit", 0, [Position(
            name="Slave",
            workload=1,
            salary=1,
            schedule=[6, 18],
            education_level=1
        ) for i in range(10)], "", Date(0, 0, 0, 0), modules)

        self.storage = Storage(max=2500)
        self.storage.add_rule("wheat", Storage.Rule('Wheat', target_stored="[max]", flow=Storage.Rule.In, target_modules=["depot"], anti_target_modules=[]))
        self.storage.add_rule("flour", Storage.Rule('Flour', target_stored="0", flow=Storage.Rule.Out, target_modules=["depot"], anti_target_modules=[]))

        self.type = "SimpleProcessingUnit"

    def do_work(self, workers):
        """ Does the work """
        # Convert resources
        for worker in workers:
            if worker.work() > 0:
                amount = self.storage.retrieve('Wheat', 10)
                overflow = self.storage.store('Flour', amount)
                self.log("Processed {} wheat".format(amount - overflow))
