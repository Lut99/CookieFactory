# PLOTS.py
#   by tHE iNCREDIBLE mACHINE
#
# Script to store plots in, and plot-related data

from matplotlib.figure import Figure

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
    
    # Runs the plot
    def plot (self, a, values):
        self.plot_function(self.x_label, self.y_label, a, values)

# Different plot functions
# They plot over an existing subfigure
def plot (x_label, y_label, a, values):
    a.clear()
    a.plot(values['x_values'], values['y_values'])
    a.set_xlabel(x_label)
    a.set_ylabel(y_label)