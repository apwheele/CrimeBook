'''
This file contains
the functions for 
creating the tables
and visualizations
'''

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from datetime import datetime

contact = ('Andrew Wheeler', 'andrew.wheeler@crimede-coder.com')

# My default chart template
theme = {'axes.grid': True,
         'axes.axisbelow': True,
         'grid.linestyle': '--',
         'legend.framealpha': 1,
         'legend.facecolor': 'white',
         'legend.shadow': True,
         'legend.fontsize': 14,
         'legend.title_fontsize': 16,
         'xtick.labelsize': 10,
         'ytick.labelsize': 10,
         'axes.labelsize': 12,
         'axes.titlesize': 14,
         'axes.titlelocation': 'left',
         'figure.dpi': 500}

# updating the default
rcParams.update(theme)


# Into title slide
def intro_slide(date,cont=contact):
    intro  =  f'# Cary Monthly Crime Report\n\n'
    intro += "This is an automated CompStat report that provides up to date metrics for "
    intro += "\n - the most recent year-to-date metrics"
    intro += "\n - monthly graphs over the prior three years"
    intro += "\n - The top 10 aparment complexes with the highest weighted crime harm scores over the past 90 days"
    intro += f"\n\nLast run at {date.strftime('%Y-%m-%d')}\n"
    intro += f'By [{contact[0]}](mailto:{contact[1]})'
    return intro

# Year to Date Table
def ytd_output(data,date_str):
    title = f'## Year to Date Stats as of {date_str}'
    mt = data.to_markdown()
    return title + '\n' + mt

# Monthly Graph last 3 years
def month_graphs(data):
    cols = list(data)[1:]
    # set xticks for January and July
    tr = data['Date'][data['Date'].dt.month.isin([1,7])]
    tr_labs = tr.dt.strftime('%Y-%m')
    for c in cols:
        fig, ax = plt.subplots(figsize=(4,1.9))
        ax.plot(data['Date'],data[c],'-o',c='k',markeredgecolor='white')
        # set xticks every quarter
        ax.set_xticks(tr,tr_labs,rotation=30,fontsize=10)
        ax.set_title(f'{c} counts per month')
        plt.show()

# Apt Crime Weights Table
def apt_table(data,range_str,n=10):
    topk = data.head(n).copy()
    # escaping the pipe in the markdown for the note
    topk['Note'] = topk['Note'].str.replace(r"|",r"\|")
    fin_str = f'## Top {n} Apartments by Crime Weights\n\n'
    fin_str += range_str
    tkm = topk.to_markdown(index=False)
    fin_str += "\n\n" + tkm
    return fin_str
