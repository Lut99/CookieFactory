#
# MODULES.py
#
# Part of the Factory. Contains all classes representing modules for factories
#   to purchase so they can make additional or more stuff.

import random
import sys

import APIs.calculator as calculator
import Tools
from Tools import Date
from Tools import Position

class Storage ():
    class Rule ():
        In = "__IN"
        Out = "__OUT"
        InOut = "__IN_OUT"
        def __init__(self, item, target_stored = "[max]", flow = InOut, target_modules = [ "*" ], anti_target_modules = [ "depot" ]):
            self.item = item
            # Allow the module to enter a variable target (e.g. [max]/2)
            self.form = calculator.parse(target_stored, verbose=False)
            self.flow = flow
            self.target_modules = target_modules
            self.anti_target_modules = anti_target_modules

    def __init__(self, max = 5000):
        self.__storage = {}
        self.rules = {}
        self.max = max
        self.total = 0

    def add_rule (self, id, rule):
        self.rules[id] = rule

    def get_rule (self, id):
        if id not in self.rules: return None
        return self.rules[id]

    def remove_rule (self, id):
        self.rules.pop(id, None)

    def __getitem__(self, key):
        if key not in self.__storage:
            return 0
        return self.__storage[key]

    def store (self, item, amount):
        if item not in self.__storage:
            # If we're already at maximum, return the amount as the overflow
            #   (nothing fits)
            if self.stored == self.max:
                return amount
            # Init new item
            self.__storage[item] = 0
        # Compute the overflow
        overflow = (self.stored() + amount) - self.max
        if overflow < 0: overflow = 0
        # Store the amount
        self.__storage[item] += amount - overflow
        self.total += amount - overflow
        return overflow

    def retrieve (self, item, amount):
        # If the item doesn't exist, we cannot store anything
        if item not in self.__storage: return
        # Compute the underflow
        underflow = amount - self.__storage[item]
        if underflow < 0: underflow = 0
        # Get the amount
        self.__storage[item] -= amount - underflow
        self.total -= amount - underflow
        return amount - underflow

    # Return total amount stored
    def stored (self):
        return self.total

    # Prints the storage contents in a pretty way
    def print (self):
        # First, print some lines
        print("-" * 50)
        print("Storage contents:")
        for item in self.__storage:
            print(" - {}: {}".format(item, self.__storage[item]))
        if self.stored() == 0:
            print("   (None)")
        print("Total: {}/{} units stored".format(self.stored(), self.max))
        print("-" * 50)

class Module ():
    def __init__(self, name, cost, positions, modules, time, construction_time):
        if name == type:
            print("Name of module cannot equal it's type")
            return
        self.name = name
        self.cost = cost
        self.modules = modules
        self.time = time
        self.construction_time = construction_time
        self.positions = positions
        self.work_done = 0
        self.archive = {}

    def do_work (self, workers):
        for w in workers:
            # Get the workload
            self.work_done += w.work()

# ADMINISTRATIVE MODULES

# Basic to any factory: manages money, houses the boss
class Office (Module):
    type = "office"

    def __init__(self, budget, market, modules, time):
        super().__init__("Headquarters (HQ)", 0, [Position(
            name="CEO",
            workload=2,
            salary=100,
            schedule=[ 9, 17 ],
            education_level = 3
        )], modules, time, Date(0,0,0,0))

        self.budget = budget
        self.market = market
        # Prepare the production chains
        self.production_chains = []
        # Do the archive
        self.archive['daily_balances'] = []
        self.archive['yearly_balances'] = [ self.budget ]
        self.archive['sold'] = 0

    def check_balance (self):
        return self.budget

    def deposit (self, amount):
        self.budget += amount

    def pay (self, amount):
        if self.budget >= amount:
            self.budget -= amount
            return amount
        return 0

    # Buy resources
    def buy_resources(self, item, amount):
        # Pay until we get to an amount we can buy
        if item not in self.market.buy_list:
            # Cannot buy
            print("Attempted to buy unexisting item from market: {}".format(item))
            return 0
        price = self.market.buy_list[item]
        while self.budget < price * amount:
            amount -= 1
        # Now get the money from the budget and use that to buy the items
        return self.market.buy(item, amount, self.pay(price * amount))

    # Sell resources
    def sell_resources(self, item, amount):
        # Sell it the market
        self.deposit(self.market.sell(item, amount))
        # Update the archive
        self.archive['sold'] += amount

    # Evaluate if we need more production chains
    def evaluate (self):
        if len(self.production_chains) == 0:
            pass

    # Archive certain stats
    def manage_archive (self):
        if self.time.hour == 0:
            # New day
            self.archive['daily_balances'].append(self.budget)
            if self.time.day == 0 and self.time.month == 0:
                # New year
                self.archive['yearly_balances'].append(self.budget)

# Can be purchased to research new recipes and modules.
class Research (Module):
    type = "research"

    def __init__(self):
        super().__init__()

# A requirement for any factory. Manages staff and salaries.
class HumanResources (Module):
    type = "human_resources"

    def __init__(self, modules, time):
        worker_position = Position(
            name="Travel Agent",
            workload=1,
            salary=50,
            schedule=[ 9, 17 ],
            education_level = 1
        )
        super().__init__("Human Resources (HR)", 0, [worker_position for i in range(5)], modules, time, Date(0,0,0,0))
        self.workers = []

        # Initialise the archive
        self.archive['history'] = []
        self.archive['hired'] = 0
        self.archive['fired'] = 0

    # Counts position in a module
    def count_positions(self, positions, position):
        c = 0
        for p in positions:
            c += (1 if p.name == position else 0)
        return c

    def manage_workers (self, available_workers):
        # First, check if any should be fired for some reason
        modules_count = {}
        for w in self.workers:
            # Pay him salary (is departure bonus if he's fired)
            if self.modules.office.pay(w.salary) == 0:
                # Oh no! Didn't have enough money to pay worker (kill his energy)
                w.no_salary += 1
            else:
                w.no_salary = 0

            if w.age > 67:
                # Fire due to pension
                self.fire(w, "pension age")
                self.archive['fired'] += 1
            elif w.no_salary == 4:
                # He quits do to not enough salary
                self.fire(w, "not paid enough")
                self.archive['fired'] += 1
            elif w.no_salary == 0 and w.perfect / (self.time - w.started).todays() < 0.5:
                # Fire due to too low performance
                self.fire(w, "too low performance")
                self.archive['fired'] += 1
            else:
                # Count the workers per module and position
                if w.module in modules_count:
                    if w.position.name in modules_count[w.module]:
                        modules_count[w.module][w.position.name] += 1
                    else:
                        modules_count[w.module][w.position.name] = 1
                else:
                    modules_count[w.module] = {}
                    modules_count[w.module][w.position.name] = 1
        # Hire additional workers if required (once per worker)
        for m in self.modules:
            if m.name not in modules_count:
                # It has no workers, init the module holder
                modules_count[m.name] = {}
            for p in m.positions:
                if p.name not in modules_count[m.name]:
                    # The position isn't filled, init it
                    modules_count[m.name][p.name] = 0
                if modules_count[m.name][p.name] < self.count_positions(m.positions, p.name):
                    # Hire a possible additional worker (1 per module)
                    w = available_workers[random.randint(0,len(available_workers)-1)]
                    if self.hire(w, m, p) == True:
                        self.archive['hired'] += 1
                        modules_count[m.name][p.name] += 1
                        if m != self: self.work_done -= 1
                        available_workers.remove(w)
                        if len(available_workers) == 0:
                            # Stop because there are no more workers left
                            break
                        print("(" + str(self.time) + ") Hired " + w.name + " to work in " + m.name + " as " + p.name)
                if m != self and self.work_done - 1 <= 0:
                    # Stop because all the work that can be done is done (HumanResources is free)
                    break
            if len(available_workers) == 0:
                break

        # Fire any too much workers (e.g., more workers for a position in a module than there are positions)
        for w in self.workers:
            if modules_count[w.module][w.position.name] > self.count_positions(self.modules[w.module].positions, w.position.name):
                # We gotta let him go :(
                self.fire(w, "too many workers")

    def manage_shifts (self):
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
    def evaluate (self):
        for w in self.workers:
            if w.energy > 0:
                w.perfect += 1
                # Also level up the worker
                w.level_up()

    def hire (self, worker, module, position):
        if worker.stats.education_level >= position.education_level:
            # Hire it
            worker.module = module.name
            worker.position = position
            worker.started = self.time.now()
            worker.perfect = 0
            worker.salary = position.salary
            self.workers.append(worker)
            return True
        return False

    def fire (self, worker, reason):
        # Remove the worker
        self.workers.remove(worker)
        # Now add his name and reason for fireing
        self.archive['history'].append({
            'name' : worker.name,
            'module' : worker.module,
            'position' : worker.position.name,
            'days_employed' : (self.time - worker.started).todays(),
            'reason' : reason
        })
        self.archive['fired'] += 1

    # Returns all workers working in a specific model and / or position
    def get_workers(self, module="*", position="*"):
        # Assemble all workers with the module
        to_return = []
        for w in self.workers:
            if (w.module == module or module == "*") and (w.position == position or position == "*"):
                to_return.append(w)
        return to_return

# Manages resource flow
class Logistics (Module):
    type = "logistics"

    def __init__(self, modules, time):
        super().__init__("Logistics", 0, [ Position(
            name = "Manager",
            workload = 2,
            salary = 300,
            schedule = [ 9, 17 ],
            education_level = 1
        ) ], modules, time, Date(0,0,0,0))
        # Add some additional positions
        for _ in range(10):
            self.positions.append(Position(
                name = "Forklift Operator",
                workload = 1,
                salary = 200,
                schedule = [ 9, 17 ],
                education_level = 1
            ))
        # Set the amount that can be hauled per forktruck
        self.max_haul = 50
        # To keep track of hauled goods
        self.archive = {
            "hauled":0
        }

    # Override to do work
    def do_work (self, workers):
        if len(workers) == 0: return
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
                            'module':m,
                            'targets':rule.target_modules,
                            'antitargets':rule.anti_target_modules,
                            'item':rule.item,
                            'amount':target - m.storage[rule.item]
                        })
                    if (rule.flow == Storage.Rule.InOut or rule.flow == Storage.Rule.Out) and m.storage[rule.item] > target:
                        # Add it
                        offers.append({
                            'module':m,
                            'targets':rule.target_modules,
                            'antitargets':rule.anti_target_modules,
                            'item':rule.item,
                            'amount':m.storage[rule.item] - target
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


    # Checks to see whether offer is in the target range of request
    def isTarget (self, request, offer):
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
    def transport (self, storage_from, storage_to, item, amount, max):
        # It's a match, transport
        to_transport = amount if amount < max else max
        got = storage_from.retrieve(item, to_transport)
        # Store it
        overflow = storage_to.store(item, got)
        # Return the overflow
        storage_from.store(item, overflow)
        #print("Transported {} from item {}".format(got - overflow, item))
        # Return that which we have successfuly stored
        return got - overflow

# Serves as the connection between the factory and the (global) market.
class Depot (Module):
    type = "depot"

    def __init__(self, modules, time):
        super().__init__("Depot", 0, [ Position(
            name="Truck Driver",
            workload = 2,
            salary = 300,
            schedule = [ 9, 17 ],
            education_level = 1
        ) for i in range(10)], modules, time, Date(0,0,0,0))

        # Init the storage
        self.storage = Storage(max=float('inf'))

        # Do the trucks
        self.trucks = []

        # Set the truck max
        self.truck_max = 500

    # Override do_work
    def do_work (self, workers):
        for w in workers:
            work = w.work()
            if work > 0:
                self.trucks.append(int(self.truck_max * (2 / (1 / work))))

    # The store / retrieve functions
    def store (self, item, amount):
        # Sell these items
        for truck in self.trucks:
            shipped = truck
            if shipped > amount:
                shipped = amount
            self.modules.office.sell_resources(item, shipped)
            amount -= shipped
        # Return that which we could not transport
        return amount
    def retrieve (self, item, amount):
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
    type = "simple_processing_unit"

    def __init__(self, name):
        super().__init__(name, "simple_processing_unit", 0, [ Position(
            name="Slave",
            workload = 1,
            salary = 1,
            schedule = [ 6, 18 ],
            education_level = 1
        ) for i in range(10)], [], Date(0, 0, 0, 1970), Date(0,0,0,0))

        self.storage = Storage(max=2500)
        self.storage.add_rule("wheat", Storage.Rule('Wheat', target_stored = "[max]", flow = Storage.Rule.In, target_modules = [ "depot" ], anti_target_modules = []))
        self.storage.add_rule("flour", Storage.Rule('Flour', target_stored = "0", flow = Storage.Rule.Out, target_modules = [ "depot" ], anti_target_modules = []))

    def do_work (self, workers):
        # Convert resources
        for worker in workers:
            if worker.work() > 0:
                amount = self.storage.retrieve('Wheat', 10)
                overflow = self.storage.store('Flour', amount)
                print("Processed {} wheat".format(amount - overflow))
