import plotly.express as px
import plotly.graph_objects as go

def distribution_fig(data, last_date):
    totals_fix = px.pie(data, values= 'Count', names='Parameter', hole = 0.4,
                    title = "{} - {}: Rwanda's COVID-19 Total Cases Distribution".format('March 14, 2020', last_date), color = 'Parameter',
                    color_discrete_map = {'Total Recovered':'forestgreen', 'Active Cases':'red','Total Deaths':'black'})
    totals_fix.update_traces(textposition='inside',texttemplate = "%{label} <br> %{percent:.2%f}", hovertemplate='<b>%{label} </b> <br> Number of People: %{value:,}<br> Percentage: %{percent:.2%f}')
    totals_fix.update_layout(legend=dict(xanchor='right', yanchor='middle', y = 0.5, x=1),
                                title = dict(x=0.5, y = 0.99, yanchor = 'top', xanchor = 'center'),
                                titlefont = {'family': 'Arial','size':16, 'color':'rgb(37,37,37)'},  margin = {'l':5, 'r':5, 'b':20, 't':25},
                                paper_bgcolor='rgb(248, 248, 255)')
    annotations = []
    annotations.append(dict(x=0.5, y=-0.05, xanchor='center', yanchor='bottom',
                            text='©nzagaspard 2021       DataSource:Twitter - Ministry of Health @RwandaHealth',
                            font=dict(family='Arial', size=12, color='rgb(150,150,150)'), showarrow=False))
    totals_fix.update_layout(annotations = annotations)
    
    return totals_fix

def plot_cases(data, start, end, case_types,line_color):
    selected_data = data[(data['Date'] >= start) & (data['Date'] <= end)]
    selected_fig = px.line(selected_data, x = 'Date', y= case_types,
                            title = "{:%b %d, %Y} - {:%b %d, %Y}: Rwanda's COVID-19 {}".format(start, end,case_types), 
                            color_discrete_sequence = [line_color])
    selected_fig.update_layout(titlefont = {'family': 'Arial', 'size':16, 'color':'rgb(37,37,37)'},
                            margin = {'l':5, 'r':5, 'b':40, 't':40}, paper_bgcolor='rgb(248, 248, 255)', 
                            title = dict(x=0.5, y = 0.98, yanchor = 'top', xanchor = 'center'))
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1, xanchor='center', yanchor='bottom',
                            text='©nzagaspard 2021       DataSource:Twitter - Ministry of Health @RwandaHealth',
                            font=dict(family='Arial', size=12,color='rgb(150,150,150)'), showarrow=False))
    selected_fig.update_layout(annotations = annotations, hovermode = 'x')
    selected_fig.update_traces(line={'width':2.5}, hovertemplate='<b>Date:<b> %{x} <br><b>Cases:<b> %{y}')
    #selected_fig.update_xaxes(showspikes=True)
    #selected_fig.update_yaxes(showspikes=True)
    selected_fig.update_yaxes(rangemode="tozero", title = 'Number of Cases')
    selected_fig.update_yaxes(rangemode="tozero")
    
    return selected_fig

def race_bars(race_data, last_date):
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
    
    return fig

def add_traces(traces_data):
    
    card_numbers = go.Figure()
    for trace_data in traces_data:
        data, row, text = trace_data
        for i in range(4):
            numbers = data[i]
            titles = ['Total', 'Recovered', 'Deaths', 'Active']
            colors = ['Red', 'Green', 'Black', 'crimson']
            card_numbers.add_trace(go.Indicator(
                mode = "number+delta",
                value = numbers[1],
                number = {'valueformat':',:'},
                title = {"text": f"<span style='font-size:0.8em;color:gray'>{text}</span>"} if row != 0 else 
                {"text": f"{titles[i]}<br><span style='font-size:0.8em;color:gray'>{text}</span>"},
                delta = {'position': "bottom",'reference': numbers[1]/(1 + numbers[1]/numbers[0]),
                         'relative': True, 'increasing': {'color': colors[i] if numbers[1] > 0 else 'green'},
                         'decreasing': {'color':'Green'}, 'valueformat':'.1%:'},
                domain = {'row': row, 'column': i}))
    card_numbers.update_layout(grid = {'rows': 3, 'columns': 4, 'ygap': 0.4}, paper_bgcolor='rgb(248, 248, 255)',
                              margin = {'l':10, 'r':10, 'b':30})
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1, xanchor='center', yanchor='bottom',
                            text='©nzagaspard 2021       DataSource:Twitter - Ministry of Health @RwandaHealth',
                            font=dict(family='Arial', size=12,color='rgb(150,150,150)'), showarrow=False))
    card_numbers.update_layout(annotations = annotations, hovermode = 'x')
    
    return card_numbers

def plot_percentages(totals):
    recovered_p = totals[2]/totals[0] * 100
    deaths_p = totals[3]/totals[0] * 100
    active_p = (totals[0] - (totals[2] + totals[3])) / totals[0] * 100
    cases_p = [recovered_p, deaths_p, active_p]
    card_p = go.Figure() 
    
    for i in range(3):
        number = cases_p[i]
        titles = ['Recovered', 'Death', 'Active']
        colors = ['Green', 'Black', 'Red']
        card_p.add_trace(go.Indicator(
            mode = "number+gauge",
            value = number,
            number = {'valueformat':'.1f:', 'suffix':'%'},
            title =  {"text": f"{titles[i]}<br><span style='font-size:0.8em;color:gray'></span>"},
            delta = {'position': "bottom"},
            gauge = {'axis': {'range': [None, 100]}, 'bar' :  {'color': colors[i]},
                    'threshold' : {'line': {'color': colors[i], 'width': 3}, 'thickness': 0.9, 'value': number}},
            domain = {'row':1, 'column' : i}))
        

    card_p.update_layout(grid = {'rows': 1, 'columns': 3, 'xgap':0.3}, paper_bgcolor='rgb(248, 248, 255)', height = 200,
                        margin = {'l':20, 'r':30, 'b':30, 't':20})
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1, xanchor='center', yanchor='bottom',
                            text='©nzagaspard 2021       DataSource:Twitter - Ministry of Health @RwandaHealth',
                            font=dict(family='Arial', size=12,color='rgb(150,150,150)'), showarrow=False))
    card_p.update_layout(annotations = annotations, hovermode = 'x')
    return card_p