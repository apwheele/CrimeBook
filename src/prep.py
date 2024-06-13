'''
This file preps the Cary
data
'''

from datetime import datetime
from io import StringIO
import numpy as np
import pandas as pd
import requests

# These are the categories I am interested in
# First field is 'Crime Category', 
# Second field is 'Crime Type'
# if None for second field, does not use it
cats = {'Murder': ('MURDER',None),
        'Robbery': ('ROBBERY',None),
        'Agg Assault': ('AGGRAVATED ASSAULT',None),
        'Burglary': ('BURGLARY',None),
        'MV Theft': ('MOTOR VEHICLE THEFT',None),
        'Theft from MV': ('LARCENY',['LARCENY - FROM MOTOR VEHICLE',
                                     'LARCENY - FROM MOTOR VEHICLE (NON FORCED)',
                                     'LARCENY - FROM MOTOR VEHICLE (FORCED)']),
        'Shoplifting': ('LARCENY',['LARCENY - SHOPLIFTING'])
}

# Aggregate crime weights and acronym for apt table
weights = {'Murder': (100,'Mur'),
           'Robbery': (25,'Rob'),
           'Agg Assault': (15,'AA'),
           'Burglary': (12, 'Bur'),
           'MV Theft': (10, 'MVT'),
           'Theft from MV': (5, 'TFMV')
}


def get_cary():
    '''function to get Cary online data'''
    cary_url = ('https://data.townofcary.org/api/explore/v2.1/catalog/datasets'
             '/cpd-incidents/exports/csv?lang=en&timezone=US%2FEastern'
             '&use_labels=true&delimiter=%2C')
    res_csv = requests.get(cary_url)
    data = pd.read_csv(StringIO(res_csv.text),low_memory=False)
    return data


def prep_data(cat_info=cats,
              extra_vars=['Apartment Complex','Phx Community','Phx Status']):
    '''
    function to prepare data
    
    cat_info -- dictionary (default see prep.cats object)
                that lists first the crime category and then
                the Crime Type, key is the name in subsequent graphs
    extra_vars - list of extra variables you want to keep
                 default apartment and Phx info
    
    returns dataframe with formatted date field and dummy variables
    for each of the crime categories
    '''
    # This downloads data and creates dummy variables
    data = get_cary()
    for cn in cat_info.keys():
        c1, c2 = cat_info[cn]
        if c2:
            data[cn] = (data['Crime Category'] == c1) & (data['Crime Type'].isin(c2))
        else:
            data[cn] = (data['Crime Category'] == c1)
    # converting to timevariable
    data['Date'] = pd.to_datetime(data['Begin Date Of Occurrence'])
    # getting last date in data
    max_date = data['Date'].max()
    # Returning only variables I want and rows that meet one of these criteria
    dummy_vars = list(cat_info.keys())
    any_vals = (data[dummy_vars].sum(axis=1) > 0)
    data[dummy_vars] = 1*data[dummy_vars]
    keep_vars = ['Date'] + dummy_vars + extra_vars
    data.sort_values(by='Date',inplace=True) # sorting so oldest to newest
    return data.loc[any_vals,keep_vars].reset_index(drop=True), max_date


# Year to Date Stats
def ytd_stats(data,date='Date',valfields=list(cats.keys())):
    '''
    Function to calculate year-to-date stats
    calculates based on the last date in the data you feed
    in
    
    data - dataframe with dummy variables
    date - string for the date field name, default 'Date'
    valfields - list of strings for dummy variable fields you want
                to calculate metrics for, default taken from prep.cats
                dictionary keys
    
    returns dataframe with the year-to-date metrics
    along with the date for the event
    '''
    # Getting the last date in the data
    last_date = data[date].max()
    curr_year, month, curr_day = last_date.year, last_date.month, last_date.day
    # Calculating prior year
    # leap year exception
    if (month == 2) & (curr_day == 29):
        prior_day = 28
    else:
        prior_day = curr_day
    prior_year = curr_year - 1
    prior_date = pd.to_datetime(f'{prior_year}-{month}-{prior_day}')
    # Getting prior/current year records
    prior_val = (data[date].dt.year == prior_year) & (data[date] <= prior_date)
    curr_val = (data[date].dt.year == curr_year) & (data[date] <= last_date)
    # Aggregating totals
    prior_tot = data.loc[prior_val,valfields].sum()
    curr_tot = data.loc[curr_val,valfields].sum()
    # Putting together in dataframe
    df = pd.concat([prior_tot,curr_tot],axis=1)
    df.columns = ['Prior YTD','Current YTD']
    df['Difference'] = df['Current YTD'] - df['Prior YTD']
    return df, last_date.strftime('%Y-%m-%d')


# Monthly Stats Prior 3 years
def month_counts(data,prior_months=36,date='Date',
                 valfields=['Robbery','Agg Assault','Burglary','MV Theft','Theft from MV','Shoplifting']):
    '''
    Counts of monthly crimes
    
    data - dataframe
    prior_months - integer prior months to look back (default 36)
    date - string for date field, default 'Date'
    valfields- list of strings signifying dummy variable fields to aggregate, default 
               ['Robbery','Agg Assault','Burglary','MV Theft','Theft from MV','Shoplifting']
    
    returns dataframe with counts per month for the valfieds, note the final month
    will be chopped off if a full month is not observed in the data
    '''
    last_date = data[date].max()
    # generating months
    months = pd.date_range(start=last_date,periods=prior_months+1,freq=pd.offsets.MonthEnd(-1))
    months = months[range(months.shape[0]-1,-1,-1)] # reversing
    # if not full month, chop off
    if months[-1] > last_date:
        months = months[:-1]
    else:
        months = months[1:]
    months = pd.DataFrame(months,columns=[date])
    #begin_month = months + pd.offsets.MonthBegin(-1)
    # easier to convert original data to beginning month
    df = data.copy() # should not modify the original data object
    df[date] = df[date] + pd.offsets.MonthEnd(1)
    month_counts = df.groupby(date,as_index=False)[valfields].sum()
    months = months.merge(month_counts).fillna(0) #this fills in 0 if any missing
    return months


# Apartment Metrics prior 90 days
def apt_metrics(data,crime_weights=weights,prior=90,date='Date'):
    '''
    This calculates apartment metrics given dummy variables and crime weights
    
    data - dataframe
    crime_weights - dictionary with fields (that should map to dummy variables in the
                    data) plus crime weights and abbreviations
    prior - prior days to look bake (based on last date in the data), default 90
    date - string for the date field, default 'Date'
    
    returns dataframe with the apartments and Phx status. Note dataframe should have
    fields 'Apartment Complex' and 'Phx Status' for this function to work. Phx Status
    is latest in the data.
    '''
    # Get a list of apartments and latest PhxStatus
    apt = data.drop_duplicates(subset=['Apartment Complex'],keep='last')
    apt = apt.loc[~apt['Apartment Complex'].isna(),['Apartment Complex','Phx Status']].reset_index(drop=True)
    # aggregating events in last 90 days
    last_date = data[date].max()
    prior_date = last_date - pd.Timedelta(days=prior)
    prior_data = (data[date] >= prior_date)
    # getting counts for the apartment complexes
    wv = list(crime_weights.keys())
    apt_counts = data[prior_data].groupby('Apartment Complex',as_index=False)[wv].sum()
    # Calculating note field with total events
    def tot_events(x):
        note = []
        for i,c in enumerate(crime_weights.keys()):
            lv = x.iloc[i]
            abbr = crime_weights[c][1]
            if lv > 0:
                note += [f'{abbr} {lv:.0f}']
        return ' | '.join(note)
    apt_counts['Note'] = apt_counts[wv].apply(tot_events,axis=1)
    # applying the crime weights
    for k,v in crime_weights.items():
        weightv = v[0]
        apt_counts[k] = apt_counts[k]*weightv
    # This assumes the weights are integers
    apt_counts['Crime Weight'] = apt_counts[wv].sum(axis=1)
    count_fields = ['Apartment Complex','Crime Weight','Note']
    # This merges in the counts to the big apartment list
    apt = apt.merge(apt_counts[count_fields],how='left',on='Apartment Complex').fillna(0)
    apt.sort_values(by='Crime Weight',ascending=False,inplace=True,ignore_index=True)
    apt['Phx Status'] = apt['Phx Status'].replace({0: 'Not Phx'})
    apt['Note'] = apt['Note'].replace({0: ''})
    apt['Crime Weight'] = apt['Crime Weight'].astype(int) # assumes weights are integers
    date_range = f"Apt. Crime from {prior_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}"
    return apt, date_range

