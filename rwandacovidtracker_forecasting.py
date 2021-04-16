#Importing important Module
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta, datetime
import requests
import smtplib
from decouple import config
import streamlit as st
st.set_page_config(page_title="Rwanda Covid Tracker & Forecaster",page_icon=":flag-rw:")

#st.set_page_config(layout="wide")
#Reading and preparing the Data
#@st.cache
def get_data():
    url = config('url')
    data = pd.read_csv(url, parse_dates = ['Date'])
    data['Total Cases'] = data['Cases'].cumsum()
    data['Total Recovered'] = data['Recovered'].cumsum()
    data['Total Recovered'] = data['Total Recovered'].replace(np.nan,0)
    data['Total Deaths'] = data['Deaths'].cumsum()
    data['Total Deaths'] = data['Total Deaths'].replace(np.nan,0)
    data['Active Cases'] = data['Total Cases'] - data['Total Recovered'] - data['Total Deaths']
    transposed_data = data.reset_index().rename({'index':'Days'}, axis = 1)
    race_data = transposed_data.melt(id_vars = ['Date','Days'], value_vars = ['Total Cases', 'Active Cases', 'Total Recovered', 'Total Deaths'], 
                        var_name = 'Parameter', value_name = 'Count')
    
    return data, race_data

data,race_data =get_data()
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

summary = {'Parameter':['Days since first case','Total Cases','Total Recovered','Total Deaths','Total Active','Most cases on a single day',
                        'Most recoveries on a single day', 'Most deaths on a single day', 'Most active on a single day'],
          'Count':[total_days, total_cases, total_recovered, total_deaths, total_active, 
                   most_new_cases, most_recoveries, most_deaths,  most_active]}
summary_df = pd.DataFrame(summary)
summary_df['Count'] = summary_df['Count'].astype(int)
summary_df.set_index('Parameter', inplace=True)

def get_news():
    url = 'https://newsapi.org/v2/everything?'
    parameters = {'qInTitle': 'rwanda AND (coronavirus OR covid-19 OR covid)', 'pageSize': 7,
                  'apiKey': 'e0df67bf080b41cba1c31b94d013e209', 'sortBy': 'publishedAt'}
    response = requests.get(url, params=parameters)
    response_data = response.json()
    
    return response_data['articles']

#Application
hide_st_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
st.title('Rwanda COVID-19 Cases Tracker')
st.sidebar.title('About')
st.sidebar.info("""This application uses the daily Coronavirus updates provided by the Rwanda's Ministry of Health and provide the summary, distribution, 
growth, and trends of cases in interactive way. It also provide links to some recent news gathered from the NewsApi.""")
st.sidebar.title('Info')
st.sidebar.info("""Gaspard Nzasabimfura  \n Data Analyst & Scientist  \n Email: nzagaspard@gmail.com  \n Tel: +250789779262""")
st.markdown("""Rwanda total cases rose from 1 on March 14, 2020 to {:,} on {}. {:,} patients recovered and {:,} died which bring down the active cases to {:,}.""".format(int(total_cases), last_date, int(total_recovered), int(total_deaths), int(total_active)))

# Summary
summary, news = st.beta_columns(2)
summary.subheader('Summary')
summary.table(summary_df)
parameters = ['Days since first case','Total Cases','Total Recovered','Total Deaths','Total Active','Most cases on a single day',
                        'Most recoveries on a single day', 'Most deaths on a single day', 'Most active on a single day']
counts = [total_days, total_cases, total_recovered, total_deaths, total_active, 
                   most_new_cases, most_recoveries, most_deaths,  most_active]
#for i in range(9):
    #summary.markdown("{} : {:,}".format(parameters[i],int(counts[i])))

#
news.subheader('Recent News')
articles = get_news()

for article in articles:
    url = article['url']
    title = article['title']
    news.write("[{}]({})".format(title, url))
#Cases distribution figure
totals_fix = px.pie(totals_transposed, values= 'Count', names='Parameter',
                    title = "{} - {}: Rwanda's COVID-19 Total Cases Distribution".format('March 14, 2020', last_date), color = 'Parameter',
                    color_discrete_map = {'Total Recovered':'forestgreen', 'Active Cases':'red','Total Deaths':'black'})
totals_fix.update_traces(textposition='inside',texttemplate = "%{label} <br> %{percent:.2%f}", hovertemplate='<b>%{label} </b> <br> Number of People: %{value:,}<br> Percentage: %{percent:.2%f}')
totals_fix.update_layout(legend=dict(xanchor='right', yanchor='middle', y = 0.5, x=1),
                            title = dict(x=0.5, y = 0.99, yanchor = 'top', xanchor = 'center'),
                            titlefont = {'family': 'Arial','size':16, 'color':'rgb(37,37,37)'},  margin = {'l':5, 'r':5, 'b':20, 't':25},
                            paper_bgcolor='rgb(248, 248, 255)')
annotations = []
annotations.append(dict(x=0.5, y=-0.05, xanchor='center', yanchor='bottom',
                        text='©nzagaspard 2020       Source:Twitter - Ministry of Health @RwandaHealth',
                        font=dict(family='Arial', size=12, color='rgb(150,150,150)'), showarrow=False))
totals_fix.update_layout(annotations = annotations)
st.subheader('Distribution')
st.plotly_chart(totals_fix, use_container_width=False) 

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

def plot_cases(case_types,line_color):
    selected_data = data[(data['Date'] >= start) & (data['Date'] <= end)]
    selected_fig = px.line(selected_data, x = 'Date', y= case_types,
                            title = "{:%b %d, %Y} - {:%b %d, %Y}: Rwanda's COVID-19 {}".format(start, end,case_types), 
                            color_discrete_sequence = [line_color])
    selected_fig.update_layout(titlefont = {'family': 'Arial', 'size':16, 'color':'rgb(37,37,37)'},
                            margin = {'l':5, 'r':5, 'b':40, 't':40}, paper_bgcolor='rgb(248, 248, 255)', 
                            title = dict(x=0.5, y = 0.98, yanchor = 'top', xanchor = 'center'))
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1, xanchor='center', yanchor='bottom',
                            text='©nzagaspard 2020       Source:Twitter - Ministry of Health @RwandaHealth',
                            font=dict(family='Arial', size=12,color='rgb(150,150,150)'), showarrow=False))
    selected_fig.update_layout(annotations = annotations, hovermode = 'x')
    selected_fig.update_traces(line={'width':2.5}, hovertemplate='<b>Date:<b> %{x} <br><b>Cases:<b> %{y}')
    #selected_fig.update_xaxes(showspikes=True)
    #selected_fig.update_yaxes(showspikes=True)
    selected_fig.update_yaxes(rangemode="tozero", title = 'Number of Cases')
    selected_fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(selected_fig, use_container_width=False)
    
if cases_selector == 'All Cases':
    plot_cases('Total Cases','red')

elif cases_selector == 'New Cases':
    plot_cases('Cases','orangered')

elif cases_selector == 'Deaths':
    plot_cases('Deaths','black')

elif cases_selector == 'Recovered Cases':
    plot_cases('Recovered','green')

elif cases_selector == 'Active Cases':
    plot_cases('Active Cases','crimson')
    
#Cases Growth Figure
st.subheader('Daily Growth')
fig = px.bar(race_data, x="Count", y='Parameter', color='Parameter', animation_frame="Days", orientation = 'h',
   color_discrete_map={'Total Cases':'red', 'Active Cases':'crimson', 'Total Recovered':'green', 'Total Deaths':'black'},
    range_x=[0,race_data["Count"].max()*1.04], hover_data = {'Parameter':True, 'Days':True,'Count':True},
   title = "{} - {}: Rwanda's COVID-19 Daily Growth".format('March 14, 2020', last_date))
fig.update_traces(texttemplate='%{value}',textposition='inside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', paper_bgcolor='rgb(248, 248, 255)',
                  showlegend=False, margin = {'l':5, 'r':5, 'b':40, 't':40},
                 titlefont = {'family': 'Arial', 'size':16, 'color':'rgb(37,37,37)'},
                 title = dict(x=0.5, y = 0.98, yanchor = 'top', xanchor = 'center'))
fig.update_layout(updatemenus = [{"buttons": [{"args": [None, {"frame": {"duration": 300, "redraw": False}, "fromcurrent": True, 
                                             "transition": {"duration": 0}}], "label": "Play", "method": "animate"},
                            {"args": [[None],{"frame": {"duration": 0, "redraw": False}, "mode": "immediate",
                                              "transition": {"duration": 0}}], "label": "Pause", "method": "animate"}]}])
fig.update_xaxes(rangemode="tozero", title = 'Number of Cases')
fig.update_yaxes(rangemode="tozero", title = '')
st.plotly_chart(fig, use_container_width=True)

def send_email(message):
    st.write('Sending...!')
    try:
        email = smtplib.SMTP('smtp.gmail.com', 587) 
        email.starttls()  
        email.login("savoirict@gmail.com", "savoirict123")
        email.sendmail("savoirict@gmail.com", "nzagaspard@gmail.com", message)
        st.write('Message sent!')
    
    except:
        st.write('Message not sent')
    
    finally:
        email.quit()
    
contact = st.beta_expander('Click here for Feedback or Questions')
names_col, email_col = contact.beta_columns(2)
names = names_col.text_input('Enter your name')
email = email_col.text_input('Enter your email')
message = contact.text_area('Message')
message = ' '.join(message.split())
send = contact.button('Send')
email_message = """Subject: Info - Rwanda COVID-19 Tracker\n\nNames: {}\nEmail: {}\nMessage: {}""".format(names,email, message)
if send:
    send_email(email_message)