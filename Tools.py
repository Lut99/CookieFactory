# TOOLS.py
#
# A file containing tools and stuff

import random

import APIs.AdvancedParser as AdvancedParser
from Globals import register_uuid
from Globals import CONNECTION_SERVER
from Globals import ITEMS
from Globals import RECIPES
from Globals import NAMES
from Globals import TIME
from Globals import MODULES_LIST


class Date ():
    """
        The Date class provides a ready-to-use simulation time. Goes by hours.
    """

    # A few constants
    NameOfMonth = {
        0 : "January",
        1 : "February",
        2 : "March",
        3 : "April",
        4 : "May",
        5 : "June",
        6 : "July",
        7 : "August",
        8 : "September",
        9 : "October",
        10 : "November",
        11 : "December"
    }
    HOURS_PER_DAY = 24
    DAYS_PER_MONTH = {
        0 : 31,
        1 : 28,
        2 : 31,
        3 : 30,
        4 : 31,
        5 : 30,
        6 : 31,
        7 : 31,
        8 : 30,
        9 : 31,
        10 : 30,
        11 : 31
    }
    MONTHS_PER_YEAR = 12

    def __init__(self, hour=0, day=0, month=0, year=0, epoch=0):
        self.epoch = epoch
        # Add the hour, day, month and year
        self.epoch += Date.epochify(hour, day, month, year)
        # Check if valid
        if self.epoch < 0:
            raise ValueError("Time cannot be lower than The Beginning (00:00:00 00/00/0000)")
        # Update the hour etc. as well
        self.hour, self.day, self.month, self.year = Date.depochify(self.epoch)

    def __str__(self):
        """ Returns the string representation of the current time """
        return "{:02d}:00:00 {:02d}/{:02d}/{:04d}".format(self.hour, self.day + 1, self.month + 1, self.year)

    def __hash__(self):
        """ Returns the hash of the epoch """
        return hash(self.epoch)

    def __le__(self, other):
        """ Handles a comparison with other dates """
        return self.epoch <= other.epoch

    def __lt__(self, other):
        """ Handles a comparison with other dates """
        return self.epoch < other.epoch

    def __ge__(self, other):
        """ Handles a comparison with other dates """
        return self.epoch >= other.epoch

    def __gt__(self, other):
        """ Handles a comparison with other dates """
        return self.epoch > other.epoch

    def __eq__(self, other):
        """ Handles a comparison with other dates """
        return self.epoch == other.epoch

    def __ne__(self, other):
        """ Handles a comparison with other dates """
        return not self.__eq__(other)

    def __add__(self, other):
        """ Handles a sum with other dates """
        return Date(epoch=self.epoch + other.epoch)

    def __sub__(self, other):
        """ Handles a sum with other dates """
        epoch = self.epoch - other.epoch
        if epoch < 0:
            raise ValueError("Time cannot be lower than The Beginning (00:00:00 00/00/0000)")
        return Date(epoch=epoch)

    def tick(self, hours=1):
        """ Advances the time by the given amount of hours """
        # Save the current date for the ticked
        prev_hour, prev_day, prev_month, prev_year = self.hour, self.day, self.month, self.year
        # Increment
        self.epoch += hours
        # Update the other values
        self.hour, self.day, self.month, self.year = Date.depochify(self.epoch)
        # Assemble the ticked
        ticked = []
        if prev_hour != self.hour: ticked.append('hours')
        if prev_day != self.day: ticked.append('days')
        if prev_month != self.month: ticked.append('months')
        if prev_year != self.year: ticked.append('years')
        # Return
        return ticked

    def now(self):
        """ Returns a copy """
        return Date(epoch=self.epoch)

    def tohours(self):
        """ Returns the total number of hours since the epoch """
        return self.epoch

    def todays(self, ceiling=False):
        """
            Returns the total number of days since the epoch. Rounded down
            by default, but can be rounded up if specified by ceiling.
        """

        to_return = self.epoch // Date.HOURS_PER_DAY
        if ceiling and self.epoch % Date.HOURS_PER_DAY > 0:
            to_return += 1
        return to_return

    def tomonths(self, ceiling=False):
        """
            Returns the total number of months since the epoch. Rounded down
            by default, but can be rounded up if specified by ceiling.
        """

        to_return = 0
        # Keep subtracting hours-in-months from the epoch until we can't fit it
        #   anymore
        month = 0
        epoch = self.epoch
        month_hours = Date.DAYS_PER_MONTH[month] * Date.HOURS_PER_DAY
        # Now keep subtracting months and counting
        while epoch - month_hours >= 0:
            # Apply the effect
            epoch -= month_hours
            to_return += 1
            # Increment the month and compute the hours that passed that month
            month = (month + 1) % Date.MONTHS_PER_YEAR
            month_hours = Date.DAYS_PER_MONTH[month] * Date.HOURS_PER_DAY

        # Check if we should round up
        if ceiling and epoch > 0:
            to_return += 1

        # Done
        return month

    def toyears(self, ceiling=False):
        """
            Returns the total number of years since the epoch. Rounded down
            by default, but can be rounded up if specified by ceiling.
        """

        hours = Date.HOURS_PER_DAY * sum(Date.DAYS_PER_MONTH.values()) * Date.MONTHS_PER_YEAR
        to_return = self.epoch // hours
        if ceiling and self.epoch % hours > 0:
            to_return += 1
        return to_return

    def getdate(self):
        """ Returns the date part of the string representation """
        return "{:02d}/{:02d}/{:04d}".format(self.day + 1, self.month + 1, self.year)

    def gettime(self):
        """ Returns the time part of the string representation """
        return "{:02d}:00:00".format(self.hour)

    @staticmethod
    def random():
        """ Returns a random date in the given year range. """
        return Date(epoch=random.randint(0, 100000000))

    @staticmethod
    def epochify(hours, days, months, years):
        """ Converts a set of hours, days, months and year to an epoch time """
        epoch = 0
        # Add the hours
        epoch += hours
        # Add the days
        epoch += days * Date.HOURS_PER_DAY
        # Add the months
        epoch += sum([Date.DAYS_PER_MONTH[month] for month in range(months)]) * Date.HOURS_PER_DAY
        # Add the years
        epoch += years * sum(Date.DAYS_PER_MONTH.values()) * Date.HOURS_PER_DAY

        # Done
        return epoch

    # Converts hours since epoch to hours, days, months and years
    @staticmethod
    def depochify(epoch):
        """
            Converts a given epoch to a set of hours, days, months and years
        """

        # First, take as many years as possible
        HOURS_PER_YEAR = sum(Date.DAYS_PER_MONTH.values()) * Date.HOURS_PER_DAY
        # Do the years...
        years = int(epoch / HOURS_PER_YEAR)
        epoch = epoch % HOURS_PER_YEAR
        # ...months...
        months = 0
        while epoch - (Date.DAYS_PER_MONTH[months] * Date.HOURS_PER_DAY) >= 0:
            epoch -= Date.DAYS_PER_MONTH[months] * Date.HOURS_PER_DAY
            months += 1
        # ...days...
        days = int(epoch / Date.HOURS_PER_DAY)
        epoch = epoch % Date.HOURS_PER_DAY
        # ...and hours are now epoch :)
        # Done
        return epoch, days, months, years


# Class representing the Position a worker can work in
class Position ():
    def __init__(self, name="", workload=0, salary=0, schedule = [0, 0], education_level=0):
        self.name = name
        self.workload = workload
        self.salary = salary
        self.schedule = schedule
        self.education_level = education_level


class Worker ():
    """ Represents a human that can work in a factory. """

    class Stats ():
        """ A struct for workers to keep track of their stats. """
        def __init__(self, education_level="@rnd", enthusiasm="@rnd", base_energy="@rnd"):
            self.education_level = education_level if education_level != "@rnd" else random.randint(1, 3)
            self.enthusiasm = enthusiasm if enthusiasm != "@rnd" else random.uniform(0, 1)
            self.base_energy = base_energy if base_energy != "@rnd" else random.randint(150, 200)
            self.experience = 0

    def __init__(self, name="@rnd", age="@rnd", stats="@rnd"):
        if name == "@rnd":
            rnd_i = random.randint(0, len(NAMES['FirstName']) - 1)
            name = NAMES['FirstName'][rnd_i] + " " + NAMES['LastName'][rnd_i]
        self.name = name
        self.age = age if age != "@rnd" else random.randint(18, 67)
        self.stats = stats if stats != "@rnd" else Worker.Stats()
        self.energy = self.stats.base_energy
        self.on_duty = False
        self.no_salary = 0

        # Generate a random b_day
        year = TIME.getyears() - age
        month = random.randint(0, Date.MONTHS_PER_YEAR - 1)
        day = random.randint(0, Date.DAYS_PER_MONTH[month] - 1)
        self.b_day = Date(day=day, month=month, year=year)

        # Prepare some standard initialisations
        self.module = "__EMPTY"
        self.position = Position()
        self.started = TIME.now()
        self.perfect = -1
        self.salary = -1

        # Generate a UUID
        self.uuid = register_uuid(self.name)

    def sleep(self):
        """ Resets the Worker's energy """
        self.energy = self.stats.base_energy

    def pause(self):
        """ Partly refreshes the Worker's energy """
        self.energy += 200

    def work(self):
        """
            Let's the Worker do some work. Will not work if not on duty or not
            paid for long enough.
        """

        if not self.on_duty or self.no_salary > 0: return 0
        # Reduce the energy for an as large workload as possible.
        workload = self.position.workload
        while workload > 0:
            energy_lost = workload * (15 - (self.stats.enthusiasm * 5))
            if self.energy >= energy_lost:
                self.energy -= energy_lost
                return workload + int(workload * self.stats.experience)
            workload -= 1
        self.energy = 0
        return 0

    def level_up(self):
        """ Level up by a random amount each day """
        self.stats.experience += random.uniform(0, 0.01)

    def celebrate_birthday(self):
        """ Age the worker :) """
        self.age += 1
        self.log(f"Woohoo! I just became {self.age}")

    def log(self, text, end="\n"):
        """ Logs on the connection_server """
        if type(text) != str:
            text = str(text)
        CONNECTION_SERVER.announce(text + end, origin=self.uuid)


# A class representing the global market (This is the static version).
class Market ():
    """
        A class representing the global market. This is the static version,
        meaning that prices stay the same no matter how much is paid and that
        resources can be bought and sold indefinitely.
    """

    def __init__(self):
        # Construct the price lists
        self._items = {}
        self.buy_list = {}
        self.sell_list = {}
        for i in range(len(ITEMS)):
            self._items[ITEMS['Name'][i]] = {
                'type': ITEMS['Type'][i],
                'buy': ITEMS['BuyPrice'][i],
                'sell': ITEMS['SellPrice'][i]
            }
            if ITEMS['BuyPrice'][i] != "-":
                self.buy_list[ITEMS['Name'][i]] = float(ITEMS['BuyPrice'][i])
            if ITEMS['SellPrice'][i] != "-":
                self.sell_list[ITEMS['Name'][i]] = float(ITEMS['SellPrice'][i])

        # Done

    def buy(self, item, amount, payment):
        """
            Retrieves stuff from the market, in exchange for enough payment.
        """

        # Check if we have the item
        if item not in self.buy_list:
            return 0
        # Get the total price
        price = self.buy_list[item] * amount
        # Check if the amount of money given is enough (any more will be
        #   happily accepted)
        if payment >= price:
            return amount
        return 0

    def sell(self, item, amount):
        """
            Sells stuff to the market, and the amount of money that this
            generates is returned.
        """

        # Check if the item is bought
        if item not in self.sell_list:
            return 0
        # Return the money got by selling
        return self.sell_list[item] * amount


class ModulesList ():
    """ A class for holding and working with the Modules in a Factory. """

    class ModulesListIterable ():
        """ This class enables iteration over the modules """
        def __init__(self, modules):
            self.__modules = modules
            self.__iterable = modules.__iter__()

        def __next__(self):
            to_return = self.__iterable.__next__()
            return self.__modules[to_return]

    def __init__(self, uuid):
        self._modules = {}
        # Init the empty 'todo' list
        self._constructing = []

        # Store the factory's uuid
        self.uuid = uuid

    def __getitem__(self, key):
        """
            Allows the external world to directly interact with the internal
            modules list.
        """

        if key in self._modules:
            return self._modules[key]
        return None

    def __iter__(self):
        """
            Allows the external world to iterate directly over the internal
            modules list.
        """

        return ModulesList.ModulesListIterable(self._modules)

    def __contains__(self, elem):
        """ Handles the 'in' operator """
        if type(elem) == str:
            # If it's a string, check that instead
            return elem in self._modules
        else:
            # If it's a module, check direct
            return elem.name in self._modules
        return False

    def __len__(self):
        """ Handles the 'len()' operator """
        return len(self._modules)

    def spawn(self, module, special="None"):
        """
            Spawns a new module. Identical to building, except that there is no
            construction time and that no money has to be paid.
        """

        if module.name in self._modules or module.name in self._constructing:
            self.log(f"Could not spawn '{module.name}', because a module with that name already exists")
            return

        # Add it directly
        self._modules[module.name] = module
        # If given, add the office to their own field
        if special != "None":
            if hasattr(self, special):
                self.log(f"Could not link module '{module.name}' to the field '{special}' because that field already exists.")
                return
            setattr(self, special, module)
        self.log(f"Spawned a new {module.type}, '{module.name}'.")

    def add(self, module):
        """
            Creates a module. This process deducts money from the office (has
            to be present) and takes into account the construction time it
            takes to build a module.
        """

        if module.name in self._modules or module.name in self._constructing:
            self.log(f"Could not begin construction on '{module.name}', because a module with that name already exists")
            return
        if self.office.pay(module.cost) == 0:
            self.log(f"Could not begin construction on '{module.name}', because the factory doesn't have enough money left")
        # Add it to the list of constructing modules
        self._constructing.append({
            'module': module,
            'start': TIME.now(),
            'stop': TIME + module.construction_time
        })
        self.log(f"Begun construction on a new {module.type}, '{module.name}', at the expense of {module.cost} pounds.")

    def construct(self):
        """ Advance construction on the modules that are being constructed. """
        for key in self._constructing.copy():
            m = self._constructing[key]
            if m['start'] + self.time >= m['stop']:
                # Stop the construction!
                self.log(f"Finished construction of '{m['module'].name}'")
                self._modules[m['module'].name] = m['module']
                self._constructing.remove(m)

    def getall(self):
        """ Returns a copy of the inner _modules list """
        return self._modules.copy()

    def log(self, text, end="\n"):
        """ Logs on the connection_server """
        if type(text) != str:
            text = str(text)
        CONNECTION_SERVER.announce(text + end, origin=self.uuid)


# RECIPE & PRODCHAIN CLASSES
class Recipe ():
    """ Struct that defines a recipe. """
    def __init__(self, name, module, inputs, outputs):
        self.name = name
        self.module = module
        self.inputs = inputs
        self.outputs = outputs


class ProductionChain ():
    """ Struct that defines a production chain. """
    def __init__(self, name, modules):
        self.name = name
        self.modules = modules


# TOOLS
def isType(elem, t):
    """ Checks if given element is convertible to given type """
    try:
        t(elem)
        return True
    except ValueError:
        return False


# SAVE and LOAD FUNCTIONS
def load_csv(path, elem_type="*"):
    """
        Loads a CSV into a dict. If elem_type is anything but '*', it tries
        to convert all the values to that type using elem_type().
    """

    # Try to open and load the text
    raw_text = ""
    try:
        with open(path, "r") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not read file '{path}': not found")
    # Parse the raw text
    csv_data = {}
    raw_text = raw_text.split("\n")
    # Split the commas
    columns = 0
    for i in range(len(raw_text)):
        line = raw_text[i]
        # Remove preceding whitespaces
        while len(line) > 0:
            if line[0] == " ":
                line = line[1:]
            else:
                break
        if len(line) > 0 and line[0] != "#":
            # If it isn't a comment and not an empty line:
            line = line.split(",")
            # Convert types if possible
            for j in range(len(line)):
                if elem_type == "*":
                    if isType(line[j], int):
                        line[j] = int(line[j])
                    elif isType(line[j], float):
                        line[j] = float(line[j])
                else:
                    line[j] = elem_type(line[j])

            # Determine the general column size from the first columns
            if i == 0:
                columns = len(line)

            # Compare the length and fix if necessary
            if len(line) > columns:
                line = line[:columns]
            elif len(line) < columns:
                line = line + [0 for i in range(columns - len(line))]

            # Save
            raw_text[i] = line

    # Now save the data columnwise
    for i in range(columns):
        csv_data[raw_text[0][i]] = [line[i] for line in raw_text[1:] if type(line) == list]

    # Done, return
    return csv_data


# PARSERS
def recipe_parser(name, text, DataTypes):
    """
        Recipe parser for the AdvancedParser. Basically a dict parser with
        extra checks.
    """

    # First, parse as dict
    recipe = AdvancedParser.dict_parser(name, text, DataTypes)

    if 'Module' not in recipe:
        raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: missing 'Module' field".format(name))
    # Get the module
    module = recipe['Module']
    if module not in MODULES:
        raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Unknown module '{}'".format(name, module))
    # Check if it supports recipeing
    if not hasattr(MODULES[module], 'recipe_fields'):
        raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Module '{}' does not produce anything".format(name, module))
    # Check if it has all other required fields
    for field, t in MODULES[module].recipe_fields:
        if field not in recipe:
            raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Module '{}' requires '{}' field, but not given".format(name, module, field))
        elif type(recipe[field]) != t:
            raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Expected field '{}' to be {}, got {}".format(name, field, t, type(recipe[field])))
    # Done
    return recipe


def module_parser(name, text, DataTypes):
    """
        Module parser for the AdvancedParser. Basically a dict parser, but with
        extra checks.
    """

    # First, parse as list
    module = AdvancedParser.dict_parser(name, text, DataTypes)

    fields = [('input', MODULES_LIST), ('recipe', [recipe.name for recipe in RECIPES]), ('output', MODULES_LIST)]
    for f, ls in fields:
        if f not in module:
            raise AdvancedParser.DataTypeValueException(f"Could not parse module '{name}' as module: Missing field '{f}'")
        # Check if the value is valid
        if module[f] not in ls and (f == 'recipe' or module[f] != "Market"):
            raise AdvancedParser.DataTypeValueException(f"Could not parse module '{name}' as module: Value '{module[f]}' in '{f}' does not exist")
    # Done
    return module


def load_recipes(path):
    """ Load a .recipes file using the AdvancedParser """

    # Load the recipes
    recipes_dict = AdvancedParser.parse(path, customDataTypes=[AdvancedParser.DataType('recipe', recipe_parser)])
    # Convert to Recipe objects
    recipes = []
    for recipe in recipes_dict:
        # Convert inputs and outputs
        inputs = [(key, recipes_dict[recipe]['Inputs'][key]) for key in recipes_dict[recipe]['Inputs']]
        outputs = [(key, recipes_dict[recipe]['Outputs'][key]) for key in recipes_dict[recipe]['Outputs']]
        recipes.append(Recipe(recipe, recipes_dict[recipe]['Module'], inputs, outputs))
    # Done, return
    return recipes


def load_production_chains(path):
    """ Load a .prodchain file using the AdvancedParser """
    # Load the production chain
    prodchain_dict = AdvancedParser.parse(path, customDataTypes=[AdvancedParser.DataType('productionChain', AdvancedParser.dict_parser), AdvancedParser.DataType('module', module_parser)])
    # Convert to ProductionChain objects
    production_chains = []
    for chain in prodchain_dict:
        # Convert each module
        modules = [prodchain_dict[chain][mod] for mod in prodchain_dict[chain]]
        production_chains.append(ProductionChain(chain, modules))

    # Done, return
    return production_chains
