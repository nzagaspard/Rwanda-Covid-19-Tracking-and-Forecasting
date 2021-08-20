from decouple import config
import pandas as pd
import numpy as np
import requests
import smtplib
from datetime import timedelta, datetime

def load_data():
    url = config('url')
    data = pd.read_csv(url, parse_dates = ['Date'])
    data['Total Cases'] = data['Cases'].cumsum()
    data['Total Recovered'] = data['Recovered'].cumsum()
    data['Total Recovered'] = data['Total Recovered'].replace(np.nan,0)
    data['Total Deaths'] = data['Deaths'].cumsum()
    data['Total Deaths'] = data['Total Deaths'].replace(np.nan,0)
    data['Active Cases'] = data['Total Cases'] - data['Total Recovered'] - data['Total Deaths']
    transposed_data = data.reset_index().rename({'index':'Days'}, axis = 1)
    race_data = transposed_data.melt(id_vars = ['Date','Days'], 
                                     value_vars = ['Total Cases', 'Active Cases', 'Total Recovered', 'Total Deaths'], 
                                     var_name = 'Parameter', value_name = 'Count')
    return data, race_data

def get_summary(data):
    totals = data[['Active Cases', 'Total Recovered', 'Total Deaths']].iloc[-1].astype(int).to_frame().T
    totals_transposed  = totals.T.reset_index()
    totals_transposed.columns = ['Parameter','Count']
    last_date = datetime.strftime(data['Date'].max(), '%b %d, %Y')
    total_days = len(data)
    total_active = int(data['Active Cases'].iloc[-1])
    total_cases = data['Total Cases'].max()
    total_recovered = data['Total Recovered'].max()
    total_deaths = data['Total Deaths'].max()
    most_deaths = data['Deaths'].max()
    most_recoveries = data['Recovered'].max()
    most_new_cases = data['Cases'].max()
    most_active = data['Active Cases'].max()

    summary = {'Parameter':['Days since first case','Total Cases','Total Recovered','Total Deaths',
                            'Total Active','Most cases on a single day','Most recoveries on a single day', 
                            'Most deaths on a single day', 'Most active on a single day'],
          'Count':[total_days, total_cases, total_recovered, total_deaths, total_active, 
                   most_new_cases, most_recoveries, most_deaths,  most_active]}
    summary_df = pd.DataFrame(summary)
    summary_df['Count'] = summary_df['Count'].astype(int)
    summary_df.set_index('Parameter', inplace=True)
    
    return summary_df, totals_transposed, [total_cases, last_date, total_recovered, total_deaths, total_active]

def get_changes(data, days = 1):
    before_cases = data.head(-days).Cases.sum()
    before_recovered = data.head(-days).Recovered.sum()
    before_deaths = data.head(-days).Deaths.sum()
    before_active= before_cases - (before_recovered + before_deaths)

    cases = data.tail(days).Cases.sum()
    recovered = data.tail(days).Recovered.sum()
    deaths = data.tail(days).Deaths.sum()
    active = cases - (recovered + deaths)
    
    return [[before_cases, cases], [before_recovered, recovered], [before_deaths, deaths], [before_active, active]]

def get_news():
    apikey = config('key')
    url = 'https://newsapi.org/v2/everything?'
    parameters = {'qInTitle': 'rwanda AND (coronavirus OR covid-19 OR covid)', 'pageSize': 7,
                  'apiKey': apikey, 'sortBy': 'publishedAt'}
    response = requests.get(url, params=parameters)
    response_data = response.json()
    
    return response_data['articles']

def send_email(message):
    pswd = config('login_pswd')
    email = smtplib.SMTP('smtp.gmail.com', 587) 
    email.starttls()  
    email.login("savoirict@gmail.com", pswd)
    email.sendmail("savoirict@gmail.com", "nzagaspard@gmail.com", message)
    email.quit()