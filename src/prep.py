'''
This file preps the Cary
data
'''

from datetime import datetime
from io import StringIO
import pandas as pd
import requests

# Function get Cary dataset
def get_cary():
    cary_url = ('https://data.townofcary.org/api/explore/v2.1/catalog/datasets'
             '/cpd-incidents/exports/csv?lang=en&timezone=US%2FEastern'
             '&use_labels=true&delimiter=%2C')
    #res_csv = requests.get(cary_url)
    #data = pd.read_csv(StringIO(res_csv.text),low_memory=False)
    data = pd.read_csv('./src/cpd-incidents.csv',low_memory=False)
    return data

# Prepping the data and the categories I want

# Year to Date Stats

# Monthly Stats Prior 3 years

# Apartment Metrics prior 90 days




