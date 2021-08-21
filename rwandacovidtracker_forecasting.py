#Importing important Module
import streamlit as st
from datetime import timedelta, datetime
import pandas as pd
from data_utils import load_data, get_summary, get_news, get_changes, send_email
from graphs_utils import distribution_fig, plot_cases, race_bars, add_traces, plot_percentages

st.set_page_config(page_title="Rwanda Covid Tracker & Forecaster",page_icon=":flag-rw:")

#st.set_page_config(layout="wide")

#Reading the processed data
data,race_data = load_data()
summary_df, totals_transposed, totals = get_summary(data)
last_date = totals[1]

#Application
hide_st_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
#st.title('Rwanda COVID-19😷 Cases Tracker')
title = """<div style="background-color:#f07167;padding:1.5px">
            <h1 style="color:white;text-align:center;">Rwanda COVID-19😷 Cases Tracker</h1></div><br>"""

st.markdown(title,unsafe_allow_html=True)
st.sidebar.title('About')
st.sidebar.info("""This application uses the daily Coronavirus updates provided by the Rwanda's Ministry of Health and provide the summary, distribution, 
growth, and trends of cases in interactive way. It also provide links to some recent news gathered from the NewsApi.""")
st.sidebar.title('Info')
st.sidebar.info("""Gaspard Nzasabimfura  \n Data Analyst, Scientist & Engineer  \n Email: nzagaspard@gmail.com  \n Tel: +250789779262""")
st.markdown("""Rwanda total cases rose from 1 on March 14, 2020 to {:,} on {}. {:,} patients recovered and {:,} died which bring down the active cases to {:,}.""".format(int(totals[0]), last_date, int(totals[2]), int(totals[3]), int(totals[4])))

day = get_changes(data, 1)
week = get_changes(data, 7)
month = get_changes(data, 30)

#Changes
st.subheader('Daily, Weekly & Monthly Changes')
card_figure = add_traces([(day,0, '1 Day'), (week,1, '1 Week'), (month,2, '1 Month')])
st.plotly_chart(card_figure, use_container_width=True) 
#Percentages
st.subheader('Percentages')
percentages_figure = plot_percentages(totals)
st.plotly_chart(percentages_figure, use_container_width = False)
# Summary
summary, news = st.beta_columns(2)
summary.subheader('Summary')
summary.table(summary_df)

news.subheader('Recent News')

#Getting News
try:
    articles = get_news()
    for article in articles:
        url = article['url']
        title = article['title']
        news.write("[{}]({})".format(title, url))
    
except:
    news.write('The NewsApi not responding now, try refreshing!')
    

#Cases distribution figure
st.subheader('Distribution')
distribution_figure = distribution_fig(totals_transposed, last_date)
st.plotly_chart(distribution_figure, use_container_width=False) 

#Time Series/Trend
st.subheader('Time Series/Trend')
cases_selcol, start_col, end_col = st.beta_columns(3)
cases_selector = cases_selcol.selectbox('Choose what to visualize over time: ', 
                              ['All Cases', 'New Cases', 'Recovered Cases', 'Active Cases', 'Deaths'])
sd = data['Date'].min()
ed = data['Date'].max()
min_date = datetime(sd.year, sd.month, sd.day)
max_date = datetime(ed.year, ed.month, ed.day)
start = start_col.date_input('Select the Start Date',min_value= min_date, max_value = max_date, value = min_date)
end = end_col.date_input('Select the End Date', min_value= min_date, max_value = max_date, value = max_date)
start = pd.to_datetime(start, format = '%Y-%m-%d')
end = pd.to_datetime(end, format = '%Y-%m-%d')

if cases_selector == 'All Cases':
    cases_fig = plot_cases(data, start, end, 'Total Cases','red')

elif cases_selector == 'New Cases':
    cases_fig = plot_cases(data, start, end,'Cases','orangered')

elif cases_selector == 'Deaths':
    cases_fig = plot_cases(data, start, end,'Deaths','black')

elif cases_selector == 'Recovered Cases':
    cases_fig = plot_cases(data, start, end,'Recovered','green')

elif cases_selector == 'Active Cases':
    cases_fig = plot_cases(data, start, end, 'Active Cases','crimson')

st.plotly_chart(cases_fig, use_container_width=False)

#Cases Growth Figure
st.subheader('Daily Growth')
growth_check = st.checkbox('Show the daily growth (this may take a while)', help = 'Racebar')
if growth_check:
    race_bars = race_bars(race_data, last_date)
    st.plotly_chart(race_bars, use_container_width=True)

#Feedback/Questions
st.write('')
contact = st.beta_expander('Click here for Feedback or Questions')
form = contact.form(key='email_form')
names_col, email_col = form.beta_columns(2)
names = names_col.text_input('Enter your name')
email = email_col.text_input('Enter your email')
message = form.text_area('Message')
message = ' '.join(message.split())
send_button = form.form_submit_button(label='Submit')
email_message = """Subject: Info - Rwanda COVID-19 Tracker\n\nNames: {}\nEmail: {}\nMessage: {}""".format(names,email, message)
if send_button:
    try:
        slot = contact.text('Submiting...!')
        send_email(email_message)
        slot.empty()
        slot.text('Submitted!')
    except:
        contact.write('Message not sent')
        contact.info('You can send your message to nzagaspard@gmail')
