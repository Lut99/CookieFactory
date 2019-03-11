# PLOTS.py
#   by tHE iNCREDIBLE mACHINE
#
# Script to store plots in, and plot-related data

import numpy as np
from matplotlib.figure import Figure
import matplotlib.dates as mdates

from Tools import Date

# Class to contain a plot
class Plot ():
    def __init__(self, name, plot_type, title, x_label, y_label):
        self.name = name
        self.type = plot_type
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        
        if self.type == "labels":
            self.plot_function = labels
        elif self.type == "clear":
            self.plot_function = clear
        elif self.type == "plot":
            self.plot_function = plot
        elif self.type == "date_plot":
            self.plot_function = date_plot
    
    # Runs the plot
    def plot (self, a, values):
        return self.plot_function(self.title, self.x_label, self.y_label, a, values)

# Different classes to ease creating Plots
class Labels (Plot):
    def __init__(self, title, x_label, y_label):
        super().__init__("", "labels", title, x_label, y_label)
class Clear (Plot):
    def __init__(self):
        super().__init__("", "clear", "", "", "")

# Different plot functions
# They plot over an existing subfigure

# Clears the plot
def clear (title, x_label, y_label, a, _):
    a.clear()
    return []
# Sets the title and labels
def labels (title, x_label, y_label, a, _):
    a.set_title(title)
    a.set_xlabel(x_label)
    a.set_ylabel(y_label)
    return []
# Plots a normal line
def plot (title, x_label, y_label, a, values):
    kwargs = {}
    for key in values:
        if key == 'x_values' or key == 'y_values': continue
        kwargs[key] = values[key]
    a.plot(values['x_values'], values['y_values'], **kwargs)
    a.set_title(title)
    a.set_xlabel(x_label)
    a.set_ylabel(y_label)

    return []
# Plots a normal line, but with special tick handling for dates
def date_plot(title, x_label, y_label, a ,values):
    kwargs = {}
    for key in values:
        if key == 'x_values' or key == 'y_values': continue
        kwargs[key] = values[key]
    x_range = range(len(values['x_values']))
    # Actually plot
    a.plot(x_range, values['y_values'], **kwargs)
    # Compute where the ticks should be
    ticks_pos = np.linspace(x_range[0], x_range[-1], num=20)
    ticks_val = []
    epoch_range = values['x_values'][-1].epoch - values['x_values'][0].epoch
    for pos in ticks_pos:
        # Create the matching date
        ticks_val.append(Date(epoch=values['x_values'][0].epoch + epoch_range * (pos / ticks_pos[-1])).getdate())
    a.set_xticks(ticks_pos, ticks_val)
    a.set_title(title)
    a.set_xlabel(x_label)
    a.set_ylabel(y_label)

    # Done, return the rotate_x_labels command
    return ['rotate_x_labels']