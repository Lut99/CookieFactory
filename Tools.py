# TOOLS.py
#
# A file containing tools and stuff

import sys
sys.path.append("/Users/Tim/Documents/Python") 
import os
import random
import numpy as np

import APIs.AdvancedParser
from Errors import FileParseError
from Modules import MODULES

# CLASSES

# A class to keep track of the time
class Date ():
    def __init__(self, hour=0, day=0, month=0, year=0):
        # Fix the values (if needed)
        while hour >= 24:
            hour -= 24
            day += 1
        while day >= 30:
            day -= 30
            month += 1
        while month >= 12:
            month -= 12
            year += 1
        while hour < 0:
            hour += 24
            day -= 1
        while day < 0:
            day += 30
            month -= 1
        while month < 0:
            month += 12
            year -= 1

        self.hour = hour
        self.day = day
        self.month = month
        self.year = year

    # str() handler
    def __str__(self):
        return "{:02d}:00:00 {:02d}/{:02d}/{:04d}".format(self.hour, self.day + 1, self.month + 1, self.year)
    # <= handler
    def __le__(self, other):
        self_stuff = [self.year, self.month, self.day, self.hour]
        other_stuff = [other.year, other.month, other.day, other.hour]
        for i in range(len(self_stuff)):
            if self_stuff[i] < other_stuff[i]: return True
            elif self_stuff[i] > other_stuff[i]: return False
        return True
    # < handler
    def __lt__(self, other):
        self_stuff = [self.year, self.month, self.day, self.hour]
        other_stuff = [other.year, other.month, other.day, other.hour]
        for i in range(len(self_stuff)):
            if self_stuff[i] < other_stuff[i]: return True
            elif self_stuff[i] > other_stuff[i]: return False
        return False
    # >= handler
    def __ge__(self, other):
        self_stuff = [self.year, self.month, self.day, self.hour]
        other_stuff = [other.year, other.month, other.day, other.hour]
        for i in range(len(self_stuff)):
            if self_stuff[i] < other_stuff[i]: return False
            elif self_stuff[i] > other_stuff[i]: return True
        return True
    # > handler
    def __gt__(self, other):
        self_stuff = [self.year, self.month, self.day, self.hour]
        other_stuff = [other.year, other.month, other.day, other.hour]
        for i in range(len(self_stuff)):
            if self_stuff[i] < other_stuff[i]: return False
            elif self_stuff[i] > other_stuff[i]: return True
        return False
    # == handler
    def __eq__(self, other):
        return self.year == other.year and self.month == other.month and self.day == other.day and self.hour == other.hour
    # != handler
    def __ne__(self, other):
        return not self.__eq__(other)
    # + handler
    def __add__(self, other):
        hour = self.hour + other.hour
        day = self.day + other.day
        month = self.month + other.month
        year = self.year + other.year
        while hour >= 24:
            hour -= 24
            day += 1
        while day >= 30:
            day -= 30
            month += 1
        while month >= 12:
            month -= 12
            year += 1
        return Date(hour=hour,day=day,month=month,year=year)
    # - handler
    def __sub__(self, other):
        hour = self.hour - other.hour
        day = self.day - other.day
        month = self.month - other.month
        year = self.year - other.year
        while hour < 0:
            hour += 24
            day -= 1
        while day < 0:
            day += 30
            month -= 1
        while month < 0:
            month += 12
            year -= 1
        return Date(hour=hour,day=day,month=month,year=year)

    # Advances time by x hours
    def tick (self, hours=1):
        to_return = [ 'hours' ]
        self.hour += hours
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
            if 'days' not in to_return: to_return.append('days')
        while self.day >= 30:
            self.day -= 30
            self.month += 1
            if 'months' not in to_return: to_return.append('months')
        while self.month >= 12:
            self.month -= 12
            self.year += 1
            if 'years' not in to_return: to_return.append('years')
        return to_return

    # Return a copy of itself
    def now (self):
        return Date(hour=self.hour,day=self.day,month=self.month,year=self.year)

    # Get the total number hours
    def tohours (self):
        hours = self.hour
        hours += self.days * 24
        hours += self.month * 30 * 24
        hours += self.year * 12 * 30 * 24
        return hours
    # Get the total number days
    def todays (self, ceiling=False):
        days = self.day
        days += self.month * 30
        days += self.year * 12 * 30
        if ceiling:
            days += (1 if self.hour > 0 else 0)
        return days
    # Get the total number months
    def tomonths(self, ceiling=False):
        months = self.month
        month += self.years * 12
        if ceiling:
            month += (1 if self.hour > 0 or self.days > 0 else 0)
        return month
    # Get the total number years
    def toyears(self, ceiling=False):
        if ceiling:
            return self.year + (1 if self.hours > 0 or self.days > 0 or self.months > 0 else 0)
        else:
            return self.year

    # Get either the date...
    def getdate(self):
        return "{:02d}/{:02d}/{:04d}".format(self.day + 1, self.month + 1, self.year)
    # ... or the time
    def gettime(self):
        return "{:02d}:00:00".format(self.hour)

    # STATIC FUNCTIONS

    # Returns the month name of the given number
    def name_of_month (month):
        months = {
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
        return months[month]

# Class representing the Position a worker can work in
class Position ():
    def __init__(self, name="", workload=0, salary=0, schedule = [0, 0], education_level=0):
        self.name = name
        self.workload = workload
        self.salary = salary
        self.schedule = schedule
        self.education_level = education_level

# A class representing a human, to work in the factory
class Worker ():
    # Class used by Worker to keep track of the Worker's stats
    class Stats ():
        def __init__(self, education_level="@rnd", enthusiasm="@rnd", base_energy = "@rnd"):
            self.education_level = education_level if education_level != "@rnd" else random.randint(1,3)
            self.enthusiasm = enthusiasm if enthusiasm != "@rnd" else random.uniform(0,1)
            self.base_energy = base_energy if base_energy != "@rnd" else random.randint(150,200)
            self.experience = 0

    def __init__(self, name="@rnd", age="@rnd", stats="@rnd"):
        if name == "@rnd":
            rnd_name = Names[random.randint(0,len(Names)-1)]
            if len(rnd_name[0]) > 0:
                name = rnd_name[1] + " " + rnd_name[0]
            else:
                name = rnd_name[0]
        self.name = name
        self.age = age if age != "@rnd" else random.randint(18,67)
        self.stats = stats if stats != "@rnd" else Worker.Stats()
        self.energy = self.stats.base_energy
        self.on_duty = False
        self.no_salary = 0

    def sleep (self):
        # Reset energy
        self.energy = self.stats.base_energy

    def pause (self):
        # Refresh energy a bit
        self.energy += 200

    def work (self):
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

    def level_up (self):
        # Level up by a random amount each day
        self.stats.experience += random.uniform(0, 0.01)

    def celebrate_birthday(self):
        self.age += 1

# A class representing the global market (This is the static version).
class Market ():
    def __init__(self, items, recipes, production_chains):
        # Construct the price lists
        self.__items = {}
        self.buy_list = {}
        self.sell_list = {}
        for item in items:
            self.__items[item[0]] = {'buy':item[1],'sell':item[2]}
            if item[1] != "-":
                self.buy_list[item[0]] = float(item[1])
            if item[2] != "-":
                self.sell_list[item[0]] = float(item[2])
        # Save the recipes and production chains
        self.recipes = recipes
        self.production_chains = production_chains
        # Done

    def buy (self, item, amount, payment):
        # Check if we have the item
        if item not in self.buy_list:
            return 0
        # Get the total price
        price = self.buy_list[item] * amount
        # Check if the amount of money given is enough (any more will be happily
        #   accepted)
        if payment >= price:
            return amount
        return 0

    def sell (self, item, amount):
        # Check if the item is bought
        if item not in self.sell_list:
            return 0
        # Return the money got by selling
        return self.sell_list[item] * amount

# A class for holding and working with the Modules
class ModulesList ():
    # Define the iterable
    class ModulesListIterable ():
        def __init__(self, modules):
            self.__modules = modules
            self.__iterable = modules.__iter__()

        def __next__(self):
            to_return = self.__iterable.__next__()
            return self.__modules[to_return]

    def __init__(self):
        self.__modules = {}
        # Init the empty 'todo' list
        self.__constructing = []

    # Allow the external world to directly interfact with __modules
    def __getitem__(self, key):
        if key in self.__modules:
            return self.__modules[key]
        return None

    # Also, allow the external world to iterate directely over __modules
    def __iter__(self):
        return ModulesList.ModulesListIterable(self.__modules)

    # Handle the __in__ operator
    def __contains__(self, elem):
        if isinstance(elem, Modules.Module):
            # If it's a module, check direct
            return elem.name in self.__modules
        elif type(elem) == str:
            # If it's a string, check that instead
            return elem in self.__modules
        return False

    # Spawn a new module (no construction, no pay)
    def spawn(self, module, special="None"):
        if module.name in self.__modules or module.name in self.__constructing:
            print("Could not spawn '{}', because a module with that name already exists".format(module.name))
            return
        # Add it directly
        self.__modules[module.name] = module
        if special == "office":
            self.office = module
        elif special == "hr":
            self.hr = module
        elif special == "logistics":
            self.logistics = module
        elif special == "depot":
            self.depot = module

    # Add a module the official way (construction & pay)
    def add(self, module):
        if module.name in self.__modules or module.name in self.__constructing:
            print("Could not begin construction on '{}', because a module with that name already exists".format(module.name))
            return
        if self.office.pay(module.cost) == 0:
            print("Could not begin construction on '{}', because the factory doesn't have enough money left".format(module.name))
        # Add it to the list of constructing modules
        self.__constructing.append({'module':module,'start':self.time.now(),'stop':self.time + module.construction_time})
        print("Begun construction on a new {}, '{}', at the expense of {} pounds.".format(module.type, module.name, module.cost))

    # Advance a day on the construction timers
    def construct (self):
        to_remove = []
        for key in self.__constructing:
            m = self.__constructing[key]
            if m['start'] + self.time >= m['stop']:
                # Stop the construction!
                print("Finished construction of '{}'".format(m['module'].name))
                self.__modules[m['module'].name] = m['module']
                to_remove.append(m)
        for m in to_remove: self.__constructing.remove(m)

    # Returns all modules
    def getall (self):
        to_return = {}
        for m in self.__modules:
            to_return[m] = self.__modules[m]
        return to_return

# A class for telling the factory how to make a product
class Recipe ():
    def __init__(self, name, module, inputs, outputs):
        self.name = name
        self.module = module
        self.inputs = inputs
        self.outputs = outputs

class ProductionChain ():
    def __init__(self, name, modules):
        self.name = name
        self.modules = modules

# TOOLS

# Checks if given element is convertable to given type
def isType(elem, t):
    try:
        t(elem)
        return True
    except ValueError:
        return False

# SAVE and LOAD FUNCTIONS

# Loads a CSV
def load_csv (path, elem_type="*"):
    # Try to open and load the text
    raw_text = ""
    try:
        with open(path, "r") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("Could not read file '{}': not found".format(path))
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

# The recipe parser
def recipe_parser (text, DataTypes):
    # First, parse as list
    recipes = AdvancedParser.dict_parser(text, DataTypes)
    for r in recipes:
        recipe = recipes[r]
        if 'Module' not in recipe:
            raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: missing 'Module' field".format(r))
        # Get the module
        module = recipe['Module']
        if module not in MODULES:
            raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Unknown module '{}'".format(r, module))
        # Check if it supports recipeing
        if not hasattr(module, 'recipe_fields'):
            raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Module '{}' does not produce anything".format(r, module))
        # Check if it has all other required fields
        for field, t in module.recipe_fields:
            if field not in recipe:
                raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Module '{}' requires '{}' field, but not given".format(r, module, field))
            elif type(recipe[field]) != t:
                raise AdvancedParser.DataTypeValueException("Could not parse recipe '{}' as recipe: Expected field '{}' to be {}, got {}".format(r, field, t, type(recipe[field])))
    # Done
    return recipes
def chain_parser (text, DataTypes):
    # First, parse as list
    chains = AdvancedParser.dict_parser(text, DataTypes)
    for c in chains:
        chain = chains[c]
        for m in chain:
            module = chain[m]
            for field in ['input', 'recipe', 'output']:
                if field not in module:
                    raise AdvancedParser.DataTypeValueException("Could not parse chain '{}' as production chain: missing '{}' field in module '{}'".format(c, field, m))
                if field == 'input' or field == 'output':
                    # Check if the input module (or market) exists
                    if module[field] not in MODULES:
                        raise AdvancedParser.DataTypeValueException("Could not parse chain '{}' as production chain: Unknown module '{}'".format(c, m))
    # Done
    return chains

# Load a .recipes file
def load_recipes(path, Items):
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

def load_production_chains (path):
    # Load the production chain
    prodchain_dict = AdvancedParser.parse(path, customDataTypes=[AdvancedParser.DataType('productionChain', chain_parser)])
    # Convert to ProductionChain objects
    production_chains = []
    for chain in prodchain_dict:
        # Convert each module
        modules = [prodchain_dict[chain][mod] for mod in prodchain_dict[chain]]
        production_chains.append(ProductionChain(chain, modules))

    # Done, return
    return production_chains