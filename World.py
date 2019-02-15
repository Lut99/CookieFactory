# WORLD.py
#   by tHE iNCREDIBLE mACHINE
#
# A script that hosts the factory world. It comes with a nice interface to keep
#   watch of everything happening.

import sys
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading
import time
import inspect

import Tools
from Tools import Market
from Tools import Date
import Factory
from Factory import Factory
import Modules

def split_commandline(text):
    command = ""
    args = []
    quote_mode = False
    for i in range(len(text)):
        c = text[i]
        if c == "\"" and (i == 0 or text[i - 1] != "\\"):
            quote_mode = not quote_mode
        elif not quote_mode and c == ' ' and (i == 0 or text[i - 1] != "\\"):
            args.append("")
        else:
            if len(args) == 0:
                command += c
            else:
                args[-1] += c
    return command,args


class WorldUpdater (threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)

        # Save the window
        self.window = window

        # Init console holder
        self.console_lines = []

        # Create the general time
        self.time = Date(0, 0, 0, 1970)

        # Init the factory holder
        self.tasks = [Factory("Cookie Inc.", 2000000, "cookie", Market(Tools.ITEMS, Tools.RECIPES, Tools.PRODUCTION_CHAINS), self.time)]

        # Init the UI redraw timer
        self.last_draw = time.time()
        self.draw_interval = .25

        print("Initialized WorldUpdater thread")

    def run (self):
        self.running = True
        task_i = 0
        ticked = []
        while self.running:
            # Run the current task
            self.tasks[task_i].run(ticked)

            # Make sure we keep on looping
            task_i += 1
            if task_i >= len(self.tasks):
                # Do a tick of the time
                ticked = self.time.tick()
                task_i = 0
                # Update itself
                self.update()
                # Wait a bit
                time.sleep(.1)
        # Stop all the factories
        for task in self.tasks:
            task.stop()
    
    def stop (self):
        self.running = False
        # Wait until quit
        while self.isAlive():
            pass
        # Done
        print("Stopped WorldUpdater thread")
    
    # Updates the stats on-screen
    def update (self):
        if time.time() - self.last_draw > self.draw_interval:
            # Update console
            self.window.console.insert(tk.END, Tools.CONSOLE.flush())

            # Update overview tab
            self.window.lblTime.config(text="Current time: " + str(self.time.gettime()))
            self.window.lblDate.config(text="Current data: " + str(self.time.getdate()))
            self.last_draw += self.draw_interval

class Window ():
    def __init__(self):
        print("Loading interface...")
        self.root = tk.Tk()
        self.root.title("Factory Simulator")

        # Create the notebook
        self.notebook = ttk.Notebook(self.root)

        # Create the tabs
        self.tab_console = tk.Frame(self.notebook)
        self.tab_overview = tk.Frame(self.notebook)
        self.tab_factory = tk.Frame(self.notebook)
        self.tab_options = tk.Frame(self.notebook)

        self.lblTitle = tk.Label(self.root, text="Factory Simulator", anchor="c")
        self.lblTitle.config(font=("Helvetica",36))
        self.lblTitle.config(background="gray91")
        self.lblTitle.grid(padx=0,pady=0,column=0,row=0,sticky=tk.W+tk.E)

        # Add tab stuff

        # Console
        print("  Loading 'Console' tab...")
        self.tab_console.config(background="gray91")

        self.console = tk.Text(self.tab_console)
        self.console.grid(padx=10,pady=(10),row=0,column=0,columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W)
        self.console.bind("<Key>", lambda e: "break")

        self.entry = tk.Entry(self.tab_console)
        self.entry.grid(padx=10,pady=(5,10),row=1,column=0,sticky=tk.W+tk.E)
        self.entry.config(background='white')

        self.btnSubmit = tk.Button(self.tab_console, text="Enter", command=self.buttonClick)
        self.btnSubmit.grid(padx=(0,10),pady=(5,10),row=1,column=1)
        self.btnSubmit.config(background="gray91")

        self.tab_console.columnconfigure(0, weight=1)
        self.tab_console.rowconfigure(0, weight=1)

        # Overview
        print("  Loading 'Overview' tab...")
        self.boxOverviewInfo = tk.LabelFrame(self.tab_overview,text="General Info")
        self.boxOverviewInfo.pack()

        self.lblTime = tk.Label(self.boxOverviewInfo, text="Current time: XX:XX:XX")
        self.lblTime.pack()
        
        self.lblDate = tk.Label(self.boxOverviewInfo, text="Current date: XX/XX/XX")
        self.lblDate.pack()

        # Factory
        print("  Loading 'Factory Details' tab...")
        self.boxFactoryInfo = tk.LabelFrame(self.tab_factory,text="Factory info")
        self.boxFactoryInfo.grid(padx=(10),pady=10,row=1,column=0)

        self.lblName = tk.Label(self.boxFactoryInfo, text="Name:")
        self.lblName.pack(side=tk.LEFT)

        # Options
        print("  Loading 'Options' tab...")

        # Add the tabs and return
        print("  Initializing tabs...")
        tabs = {"Console":self.tab_console, "Overview":self.tab_overview, "Factory Details":self.tab_factory, "Options":self.tab_options}
        for name in tabs:
            tabs[name].grid(padx=0,pady=0,row=0,column=0,sticky=tk.E+tk.W+tk.S+tk.N)
            self.notebook.add(tabs[name], text=name)
            print("    Initialised tab '{}'".format(name))

        print("  Finilising notebook...")
        self.notebook.select(self.tab_overview)
        self.notebook.enable_traversal()
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=tk.N+tk.E+tk.W+tk.S)

        self.notebook.rowconfigure(0, weight=1)
        self.notebook.columnconfigure(0, weight=1)

        print("  Finilising window...")
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.bind("<Return>", self.buttonClick)

        print("Done")
    
    def buttonClick(self, other=None):
        # Parse the command
        text = self.entry.get()
        # Split
        command, args = split_commandline(text)
        if command == "exit":
            self.console.insert(tk.END, "Stopping...\n")
            self.stop()
            sys.exit()
        else:
            self.console.insert(tk.END, "Unknown command '{}', type 'help' to see a list\n".format(command))

        # Clear the entry
        self.entry.delete(0, len(text))
        
def main ():
    window = Window()

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

    updater = WorldUpdater(window)
    updater.start()

    try:
        window.root.mainloop()
        updater.stop()
    except KeyboardInterrupt:
        updater.stop()

if __name__ == "__main__":
    main()