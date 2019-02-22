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
from collections import defaultdict
# Do the plot imports
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import Tools
from Tools import Market
from Tools import Date
from Tools import Command
import Factory
from Factory import Factory
import Modules
import resources.code.Plots as Plots

def is_int(var):
    try:
        int(var)
        return True
    except ValueError:
        return False

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

        # Define the commands
        self.commands = [
            Command("freeze","pause", description="Freeze the execution of the factories", executer=self.command_freeze),
            Command("unfreeze","resume", description="Resumes the execution of the factories", executer=self.command_resume),
            Command("help", description="Shows this help menu", executer=self.command_help),
            Command("stop","quit","exit","shutdown", description="Stops the simulation", executer=self.command_quit)
        ]

        # Init the prev dict
        self.prev = defaultdict(str)
        self.prev["Plots"] = defaultdict(str)

        print("Initialized WorldUpdater thread")

    def run (self):
        self.running = True
        self.frozen = False
        self.freeze_start = -1
        self.freeze_duration = -1
        task_i = 0
        ticked = []
        while self.running:
            # Run the current task
            if not self.frozen:
                self.tasks[task_i].run(ticked)
                task_i += 1

                # Make sure we keep on looping
                if task_i >= len(self.tasks):
                    # Do a tick of the time
                    ticked = self.time.tick()
                    task_i = 0
                    # Wait a bit
                    if 'days' in ticked:
                        time.sleep(.1)
            
            # Update itself
            self.update()
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
        if self.running and time.time() - self.last_draw > self.draw_interval:
            # Update console
            self.print(Tools.CONSOLE.flush(), end="")

            # Update the general time
            self.window.lblTitleTime.config(text=self.time.getdate())

            # Update overview tab
            self.window.lblTime.config(text="Current time: " + str(self.time.gettime()))
            self.window.lblDate.config(text="Current date: " + str(self.time.getdate()))
            self.last_draw += self.draw_interval

            # Update factory tab
            tasks_hash = hash(tuple(self.tasks))
            if self.prev['task_hash'] != tasks_hash:
                self.prev['task_hash'] = tasks_hash
                selected = self.window.FactorySelectorVar.get()
                menu = self.window.FactorySelector["menu"]
                menu.delete(0, tk.END)
                for task in self.tasks:
                    if isinstance(task, Factory):
                        menu.add_command(label=task.name, command=lambda value=task.name: self.window.FactorySelectorVar.set(value))
                # Restore the selected
                self.window.FactorySelectorVar.set(selected)

            factory_selected = False
            for task in self.tasks:
                if isinstance(task, Factory) and task.name == self.window.FactorySelectorVar.get():
                    self.update_factory(task)
                    factory_selected = True
                    break
            # If we have a factory, set the buttons to enable
            if factory_selected:
                self.window.btnPlots.config(state="normal")
            else:
                self.window.btnPlots.config(state="disabled")

            # Check for unfreezing interval
            if self.freeze_duration > -1 and time.time() - self.freeze_start > self.freeze_duration:
                self.freeze_start = -1
                self.freeze_duration = -1
                self.command_resume(self, [])
    
    # Updates the factory tab
    def update_factory(self, factory):
        info = (
            "Name: " + factory.name + 
            "\nType: " + factory.type + 
            "\nAge: " + str((self.time - factory.modules.archive.get("General", "Founded")).toyears()) + " yrs" +
            "\nFounded: " + factory.modules.archive.get("General", "Founded").getdate() + 
            "\nTotal sold: " + str(factory.modules.archive.get("Finance", "Total Sold"))
        )
        if self.prev['info'] != info:
            self.window.lblFactoryInfo.config(text=info)
            self.prev['info'] = info
        
        # Collect the modules
        modules = [m.name for m in factory.modules]
        selected = "__NONE"
        for i in self.window.list_modules.curselection():
                selected = self.window.list_modules.get(i)
        if hash(tuple(modules)) != self.prev['modules_hash']:
            self.prev['modules_hash'] = hash(tuple(modules))
            self.window.list_modules.delete(0,tk.END)
            for m in modules:
                self.window.list_modules.insert(tk.END, m)
            # Restore the selected
            if selected in self.window.list_modules.get(0,tk.END):
                index = self.window.list_modules.get(0,tk.END).index(selected)
                self.window.list_modules.selection_set(index)
        
        # Do the module info
        info = "Name: \nType: \nWorkers: \nConstructed: \nAge: "
        if selected in factory.modules:
            # Get module info
            module = factory.modules[selected]
            info = (
                "Name: " + module.name +
                "\nType: " + module.type +
                "\nWorkers: " + str(len(factory.modules.hr.get_workers(module=module.name))) +
                "\nConstructed: " + module.founded.getdate() + 
                "\nAge: " + str(self.time.toyears() - module.founded.toyears())
            )
        if self.prev['modules_info'] != info:
            self.prev['modules_info'] = info
            self.window.lblModuleInfo.config(text=info)

        # According to the selected module, select the workers
        workers = [w.name for w in factory.modules.hr.get_workers(module=selected)]
        selected = "__NONE"
        for i in self.window.list_workers.curselection():
            selected = self.window.list_workers.get(i)
        if hash(tuple(workers)) != self.prev['worker_hash']:
            self.prev['worker_hash'] = hash(tuple(workers))
            self.window.list_workers.delete(0,tk.END)
            for w in workers:
                self.window.list_workers.insert(tk.END, w)
            # Restore the selected
            if selected in self.window.list_workers.get(0,tk.END):
                index = self.window.list_workers.get(0,tk.END).index(selected)
                self.window.list_workers.selection_set(index)
        
        # Do the worker info
        info = "Name: \nAge: \nPosition: \nSalary: \nHired: "
        if selected in workers:
            worker = factory.modules.hr.get_worker(selected)
            info = (
                "Name: " + worker.name + 
                "\nAge: " + str(worker.age) + 
                "\nBirthday: " + worker.b_day.getdate() + 
                "\nPosition: " + worker.position.name + 
                "\nSalary: " + str(worker.salary) + 
                "\nHired: " + worker.started.getdate()
            )
        if self.prev['workers_info'] != info:
            self.prev['workers_info'] = info
            self.window.lblWorkerInfo.config(text=info)

        # Also update the plots
        if self.window.plot_window != None:
            self.update_plots(factory)
            if not tk.Toplevel.winfo_exists(self.window.plot_window.root):
                self.window.plot_window = None

    # Updates the Plot window 
    def update_plots (self, factory):
        # Get the to-be-updated plot
        plot = None
        for plt in self.window.plot_window.plots:
            if plt.name == self.window.plot_window.lstPlotSelectorVar.get():
                plot = plt
                break
        if plot == None: return
        # Set the title to that plot
        if "{factory}" in plot.title:
            plot.title = plot.title.replace("{factory}", factory.name)

        # Collect the info for the plot from the archive
        values = {}
        if plot.name == "Yearly Balance":
            # Get the years (only last hundred years)
            found_year = factory.modules.archive.get("General", "Founded").year
            newest_year = factory.time.year
            oldest_year = newest_year - 100
            if oldest_year < found_year:
                oldest_year = found_year
            values['x_values'] = range(oldest_year, newest_year)
            values['y_values'] = factory.modules.archive.get("Finance", "Yearly Balances")[-100:]
        elif plot.name == "Daily Balance":
            # Get the last 100 days
            balances = factory.modules.archive.get("Finance", "Daily Balances")[-100:]
            # Get the dates
            newest_date = factory.time.now() - Tools.Date(0, 1, 0, 0)
            oldest_date = newest_date - Tools.Date(0, len(balances), 0, 0)
            
            values['x_values'] = [(newest_date - Tools.Date(0, day, 0, 0)).getdate() for day in range((newest_date - oldest_date).todays())]
            values['y_values'] = balances
        # Check if we ACTUALLY need to update
        values_hash = hash(frozenset([frozenset(values[key]) for key in values]))
        if values_hash != self.prev["Plots"][plot.name]:
            self.prev["Plots"][plot.name] = values_hash
            # Prepare to set the update
            self.window.plot_window.schedule_plot_update(plot.plot, self.window.plot_window.a, values)

    # Prints on the command
    def print(self, text, end="\n"):
        if type(text) != str:
            text = str(text)
        self.window.console.insert(tk.END, text + end)

    # Handles commands
    def handle_command (self, command, args):
        # Check if we have that command
        handled = False
        for cmd in self.commands:
            if command in cmd.triggers:
                cmd.execute(self, args)
                handled = True
                break
        if not handled:
            self.print("Unknown command '{}', type 'help' to see a list\n".format(command))

        # Clear the entry
        if self.running:
            self.window.entry.delete(0, tk.END)
    
    # Command handlers
    def command_freeze(self, updater, args):
        extra = ""
        if len(args) == 1:
            if is_int(args[0]) and int(args[0]) >= 0:
                self.freeze_start = time.time()
                self.freeze_duration = int(args[0])
                extra += " for {} seconds".format(self.freeze_duration)
            else:
                updater.print("Invalid argument: specify a positive integer")
                return
        
        if updater.frozen:
            updater.print("The simulation is already frozen.")
        else:
            updater.frozen = True
            updater.print("Froze the execution of the simulation" + extra)
            print("Froze the execution of the simulation" + extra)
    def command_resume(self, updater, _):
        # Cancel the freeze timer if it's running
        if self.freeze_start >= 0 or self.freeze_duration >= 0:
            self.freeze_start = -1
            self.freeze_duration = -1

        if not updater.frozen:
            updater.print("The simulation is already unfrozen.")
        else:
            updater.frozen = False
            updater.print("Resumed the execution of the simulation")
            print("Resumed the execution of the simulation")
    def command_help (self, updater, _):
        updater.print("*** COMMANDS AVAILABLE ***")
        for command in updater.commands:
            updater.print(" - ", end="")
            i = 0
            for trigger in command.triggers:
                updater.print("'" + trigger + "'",end="")
                if i == len(command.triggers) - 2:
                    updater.print(" or ",end="")
                elif i < len(command.triggers) - 2:
                    updater.print(", ",end="")
                i += 1
            updater.print(":\n   " + command.description)
        updater.print("**************************")
    def command_quit (self, updater, _):
        updater.print("Stopping...\n")
        updater.window.destroy()
        updater.running = False

class Window ():
    def __init__(self):
        self.plot_window = None

        self.stopped = False

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

        # Do the title
        self.lblTitle = tk.Label(self.root, text="Factory Simulator", anchor="c")
        self.lblTitle.config(font=("Helvetica",36))
        self.lblTitle.config(background="gray91")
        self.lblTitle.grid(padx=0,pady=0,column=0,row=0,sticky=tk.W+tk.E)
        # Do the general time
        self.lblTitleTime = tk.Label(self.root, text="XX/XX/XXXX", anchor="c")
        self.lblTitleTime.config(font=("Helvetica",18))
        self.lblTitleTime.config(background="gray91")
        self.lblTitleTime.grid(padx=0,pady=0,column=0,row=1,sticky=tk.W+tk.E)

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
        self.FactorySelectorVar = tk.StringVar(self.tab_factory)
        self.FactorySelector = tk.OptionMenu(self.tab_factory, self.FactorySelectorVar, "<None>")
        self.FactorySelector.grid(padx=10,pady=10,row=0,column=0,columnspan=2, sticky=tk.E+tk.W)

        self.boxFactoryInfo = tk.LabelFrame(self.tab_factory,text="Factory info")
        self.boxFactoryInfo.grid(padx=(10),pady=10,row=1,column=0)

        self.lblFactoryInfo = tk.Label(self.boxFactoryInfo, text="", justify=tk.LEFT)
        self.lblFactoryInfo.pack(side=tk.LEFT)

        self.boxAdditional = tk.LabelFrame(self.tab_factory, text="Additional Info")
        self.boxAdditional.grid(padx=10,pady=10,row=1,column=2,sticky=tk.N+tk.W+tk.E+tk.S)

        self.btnPlots = tk.Button(self.boxAdditional, text="Factory Plots", command=self.showPlots)
        self.btnPlots.pack()

        self.btnLayout = tk.Button(self.boxAdditional, text="Factory Layout", state=tk.DISABLED)
        self.btnLayout.pack()

        self.boxModuleInfo = tk.LabelFrame(self.tab_factory,text="Modules")
        self.boxModuleInfo.grid(padx=10,pady=10,row=2,column=0,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)

        self.list_modules = tk.Listbox(self.boxModuleInfo, exportselection=False)
        self.list_modules.grid(padx=10,pady=10,row=0,column=0,sticky=tk.N+tk.S+tk.W+tk.E)

        self.lblModuleInfo = tk.Label(self.boxModuleInfo, text="", justify=tk.LEFT)
        self.lblModuleInfo.grid(padx=10,pady=10,row=0,column=1, sticky=tk.N+tk.W)

        self.list_workers = tk.Listbox(self.boxModuleInfo, exportselection=False)
        self.list_workers.grid(padx=10,pady=10,row=0,column=2,sticky=tk.N+tk.S+tk.W+tk.E)

        self.lblWorkerInfo = tk.Label(self.boxModuleInfo, text="", justify=tk.LEFT)
        self.lblWorkerInfo.grid(padx=10,pady=10,row=0,column=3, sticky=tk.N+tk.W)

        self.tab_factory.columnconfigure(1, weight=1)
        self.tab_factory.rowconfigure(2, weight=1)

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
        self.notebook.grid(row=2, column=0, columnspan=3, sticky=tk.N+tk.E+tk.W+tk.S)

        self.notebook.rowconfigure(0, weight=1)
        self.notebook.columnconfigure(0, weight=1)

        print("  Finilising window...")
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.bind("<Return>", self.buttonClick)

        print("Done")

    def destroy (self):
        # Destroy child windows (if they're there)
        if self.plot_window != None:
            self.plot_window.root.destroy()

        # Destroy self
        self.root.destroy()
    
    def buttonClick(self, other=None):
        # Parse the command
        text = self.entry.get()
        # Split
        command, args = split_commandline(text)
        # Run them
        self.updater.handle_command(command, args)
        
    def showPlots(self, other=None):
        window = tk.Toplevel(self.root)
        self.plot_window = PlotWindow(window)

class PlotWindow ():
    plots = [
        Plots.Plot("Yearly Balance", "plot", "Yearly Balances of {factory}", "Year", "Balance"),
        Plots.Plot("Daily Balance", "date_plot", "Daily Balances of {factory}", "Date", "Balance")
    ]

    def __init__(self, root):
        # Prepare the plot update task list
        self.plot_tasks = []

        self.root = root

        # Add the listbox
        self.lstPlotSelectorVar = tk.StringVar(self.root)
        self.lstPlotSelector = tk.OptionMenu(self.root, self.lstPlotSelectorVar, *[plot.name for plot in self.plots])
        self.lstPlotSelector.grid(padx=10,pady=(10),column=0,row=0,sticky=tk.E+tk.W)
        self.lstPlotSelectorVar.set(self.plots[0].name)

        # Add the plot frame
        self.boxPlot = tk.LabelFrame(self.root, text="Plot")
        self.boxPlot.grid(padx=10,pady=(0,10),column=0,row=1,sticky=tk.N+tk.E+tk.S+tk.W)

        # Create the figure
        self.fig = Figure()
        self.a = self.fig.add_subplot(111)

        # Create the plot drawer
        self.plot = FigureCanvasTkAgg(self.fig, master=self.boxPlot)
        self.plot.get_tk_widget().pack(expand=True, fill="both")#grid(padx=10,pady=10,column=0,row=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.plot.draw()

        # Do some row configures
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Begin the update loop
        self.update_plot()
    
    def update_plot(self):
        if len(self.plot_tasks) > 0:
            # Run the first task
            plot_func, sub_plot, values = self.plot_tasks[0]
            plot_func(sub_plot, values)
            # Draw
            self.plot.draw()
            self.plot_tasks = self.plot_tasks[1:]
        # Call again after .5 seconds
        self.boxPlot.after(500, self.update_plot)
    
    def schedule_plot_update(self, plot_func, sub_plot, values):
        self.plot_tasks.append((plot_func, sub_plot, values))

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
    window.updater = updater
    updater.start()

    try:
        window.root.mainloop()
        updater.stop()
    except KeyboardInterrupt:
        updater.stop()

if __name__ == "__main__":
    main()