# PLOTS.py
#   by tHE iNCREDIBLE mACHINE
#
# Script to store plots in, and plot-related data

import datetime
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Class to contain a plot
class Plot ():
    def __init__(self, name, plot_type, title, x_label, y_label):
        self.name = name
        self.type = plot_type
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        
        if self.type == "plot":
            self.plot_function = plot
        elif self.type == "date_plot":
            self.plot_function = date_plot
    
    # Runs the plot
    def plot (self, a, values):
        self.plot_function(self.title, self.x_label, self.y_label, a, values)

# Different plot functions
# They plot over an existing subfigure
def plot (title, x_label, y_label, a, values):
    a.clear()
    a.plot(values['x_values'], values['y_values'])
    a.set_title(title)
    a.set_xlabel(x_label)
    a.set_ylabel(y_label)

def date_plot(title, x_label, y_label, a ,values):
    # Convert the values['x_values'] to dates
    dates = [datetime.datetime.strptime(d, "%d/%m/%Y").date() for d in values["x_values"]]
    a.clear()
    # Set the formatter to dates
    a.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y"))
    a.xaxis.set_major_locator(mdates.DayLocator())
    # Actually plot
    a.plot(dates, values['y_values'])
    a.set_title(title)
    a.set_xlabel(x_label)
    a.set_ylabel(y_label)
    # Done