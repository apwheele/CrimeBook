'''
This file contains
the functions for 
creating the tables
and visualizations
'''

import matplotlib.pyplot as plt
from matplotlib import rcParams

# My default chart template
theme = {'axes.grid': True,
         'axes.axisbelow': True,
         'grid.linestyle': '--',
         'legend.framealpha': 1,
         'legend.facecolor': 'white',
         'legend.shadow': True,
         'legend.fontsize': 14,
         'legend.title_fontsize': 16,
         'xtick.labelsize': 14,
         'ytick.labelsize': 14,
         'axes.labelsize': 16,
         'axes.titlesize': 20,
         'axes.titlelocation': 'left',
         'figure.dpi': 200}

# updating the default
rcParams.update(theme)

# Year to Date Table

# Monthly Graph last 3 years

