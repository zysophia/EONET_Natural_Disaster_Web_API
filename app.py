import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime
from visualization import alarm_visualization

from database import fetch_all_dis_as_df, fetch_all_wea_as_df
from visualization import map_plot

# Definitions of constants. This projects uses extra CSS stylesheet at `./assets/style.css`
COLORS = ['rgb(67,67,67)', 'rgb(115,115,115)', 'rgb(49,130,189)', 'rgb(189,189,189)']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/style.css']

# Define the dash app first
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Define component functions

def page_header():
    """
    Returns the page header as a dash `html.Div`
    """
    return html.Div(id='header', children=[
        html.Div([html.H3('EONET Natural Disaster Analysis')],
                 className="nine columns"),
        html.A([html.Img(id='logo', src=app.get_asset_url('404_img.png'),
                         style={'height': '35px', 'paddingTop': '7%', 'paddingRight': '7%', 'paddingLeft': '7%'}),
                html.Span('Data1050-Team-404!', style={'fontSize': '2rem', 'height': '25px', 
                                                'paddingLeft': '4px', 'color': '#a3a7b0',
                                                'textDecoration': 'none'})],
               className="three columns row",
               href='https://github.com/zysophia/EONET_Natural_Disaster_Web_API'),
    ], className="row")


def description():
    """
    Returns overall project description in markdown
    """
    return html.Div(children=[dcc.Markdown('''
        # Natural Disaster Detector
        Every year, natural and human induced disasters caused enormous infrastructural damages, monetary 
        cost, injuries and even deaths. In June 2018, the natural disaster, Wildfire happened in California affected 
        thousands of the families that lost their homes, and millions of dollars were spent on operations.

        Unfortunately, climate changes are strengthening the destructive power of natural disasters. In this
        context, Natural Disaster Detector used The Earth Observatory Natural Event Tracker (EONET) to track
        entire globe daily and look for natural events, such as Wildfires, Storms, and Sea lake Ice, which are 
        happening now (see orange points on the map) or already happened (see green points on the map) within one year. 

        **"Disaster Alarm" is a Prediction Tool** to forecast the possibility of natural disasters occurrence. It 
        can be used to explore the Wildfire Rate in Seattle and Los Angeles area based on weather and temperature
        of selected area using Dark Sky API.

        ### Data Source
        Natural Disaster Detector utilize near-real-time natural event occurrence data from
        [EONET] (https://eonet.sci.gsfc.nasa.gov/docs/v2.1), and weather data from [Dark Sky]
         (https://darksky.net/dev/docs/sources). The database **updates every 5 minutes**, and 
         our data source [https://eonet.sci.gsfc.nasa.gov/docs/v2.1] **updates four times
         a day**. And please **do not leave the Detector open for the whole day, as the Dark Sky API will charge 
         if over 1000 queries each day**.

        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")



def disaster_visualization_tool():
    """
    Returns the disaster_visualization tool as a dash `html.Div`.
    """
    return html.Div(children=[
        html.H5("Disaster Visualization", style={'fontSize': '3rem', 'height': '40px','color': '#a3a7b0',
                                                'textDecoration': 'none', 'text-align':'center', 'paddingLeft': '70px'}),
        html.Div(children=[
            html.Div(children=[
                html.H6("Disaster Status", style={'fontSize': '2rem', 'paddingLeft': '54px', 'color': '#a3a7b0',
                                                'textDecoration': 'none', 'text-align':'center',
                                                'paddingRight': '30px', 'display': 'inline-block'}),
                dcc.Checklist(id='status-checkbox', 
                            options=[
                                {'label': 'open', 'value': 'open'},
                                {'label': 'closed', 'value': 'closed'}],
                            value=['open', 'closed'],
                            labelStyle={'display': 'inline-block'},
                            style={'display': 'inline-block'})
                            ], className='twelve columns', style={'width':'100%','textAlign': 'center'}),
            html.Div(children=[
                html.H6("Disaster Kind", style={'fontSize': '2rem',
                                            'paddingLeft': '20px', 'color': '#a3a7b0',
                                            'textDecoration': 'none', 'margin-Left': '50px'}),
                dcc.RadioItems(id='disaster-click', 
                            options=[
                                {'label': 'Wildfires', 'value': 'Wildfires'},
                                {'label': 'Severe_Storms', 'value': 'Severe_Storms'},
                                {'label': 'Sea_and_Lake_Ice', 'value': 'Sea_and_Lake_Ice'}],
                            value='Wildfires',
                            style={'paddingLeft': '0px'})
                            ], className='two columns', style={'marginLeft': 0, 'marginTop': '10%'}),
            html.Div(children=[dcc.Graph(id='disaster-figure')], className='ten columns')
            ], className='row twelve columns', style={'marginBottom': '5%', 'marginTop': '1%'})
        ], className='row twelve columns')



def alarm_description():
    """
    Returns description of "What-If" - the interactive component
    """
    return html.Div(children=[
        dcc.Markdown('''
        # " Disaster Alarm "
        So far, Natural Disaster Detector has displayed the detection of natural disasters daily on a 
        global scale. In order to make the Detector to be more relevant to domestic natural events, we can ask, 
        what is the probability that Seattle and Los Angeles will suffer from wildfire? Find below what is the 
        predicted wildfire rate ** along with different level of alarm rate? ** in different city ?
        
        Feel free to try out more result with the sliders and cities. A fully-functioning What-If tool 
        should support playing with other interesting aspects of the problem (e.g. predicted/real wildfire rate).
        ''', className='eleven columns', style={'paddingLeft': '5%'})
    ], className="row")

def alarm_tool():
    """
    Returns the What-If tool as a dash `html.Div`. The view is a 8:3 division between
    demand-supply plot and rescale sliders.
    """
    return html.Div(children=[
        html.H5("WildFire Alarming", style={'fontSize': '3rem', 'height': '40px','color': '#a3a7b0',
                                                'textDecoration': 'none', 'text-align':'center', 'paddingLeft': '70px'}),
        html.Div(children=[
            html.H6("City", style={'fontSize': '2rem',
                                            'paddingLeft': '47px', 'color': '#a3a7b0',
                                            'textDecoration': 'none', 'margin-Left': '50px'}),
            dcc.RadioItems(id='city-click', 
                            options=[
                                {'label': 'Los Angeles (CA)', 'value': 'LA'},
                                {'label': 'Seattle (WA)', 'value': 'ST'}],
                            value='LA',
                            style={'paddingLeft': '15px'}),
            html.H6("Alarm Rate", style={'fontSize': '2rem', 'paddingTop': '30px',
                                            'paddingLeft': '31px', 'color': '#a3a7b0',
                                            'textDecoration': 'none', 'margin-Left': '50px'}),
            html.Div(children=[
                dcc.Slider(id='alarm-rate-slider', min=1, max=3.001, step=1, value=1, className='row',
                           marks={x: "{:.0f}".format(x) for x in [1, 2, 3]})
            ], style={'marginTop': '1.5rem'}),
        ], className='two columns', style={'marginLeft': 0, 'marginTop': '10%'}),
        html.Div(children=[dcc.Graph(id='alarm-figure')], className='ten columns', style={'marginBottom': '5%','paddingTop':'1%'}),
    ], className='row twelve columns')




def architecture_summary():
    """
    Returns the text and image of architecture summary of the project.
    """
    return html.Div(children=[
        dcc.Markdown('''
            # Project Architecture
            This project uses MongoDB as the database. All data acquired are stored in raw form to the
            database (with de-duplication). An abstract layer is built in `database.py` so all queries
            can be done via function call. For a more complicated app, the layer will also be
            responsible for schema consistency. A `plot.ly` & `dash` app is serving this web page
            through. Actions on responsive components on the page is redirected to `app.py` which will
            then update certain components on the page. 
        ''', className='row eleven columns', style={'paddingLeft': '5%'}),

        html.Div(children=[
            html.Img(src="https://docs.google.com/drawings/d/e/2PACX-1vQNerIIsLZU2zMdRhIl3ZZkDMIt7jhE_fjZ6ZxhnJ9bKe1emPcjI92lT5L7aZRYVhJgPZ7EURN0AqRh/pub?w=670&amp;h=457",
                     className='row'),
        ], className='row', style={'textAlign': 'center'}),

        dcc.Markdown('''
        
        ''')
    ], className='row')


app.layout = html.Div([
    page_header(),
    html.Hr(),
    description(),
    disaster_visualization_tool(),
    alarm_description(),
    alarm_tool(),
    architecture_summary(),
], className='row', id='content')



@app.callback(
    Output('disaster-figure', 'figure'),
    [Input('status-checkbox', 'value'),
     Input('disaster-click', 'value')])
def disaster_visual_handler(status, disaster):
    """Changes the display graph of supply-demand"""
    df = fetch_all_dis_as_df(allow_cached=True)
    if df is None:
        return go.Figure()
    return map_plot(df[(df['title'] == disaster) & df['status'].isin(status)])

_alarm_data_cache = None


@app.callback(
    Output('alarm-figure', 'figure'),
    [Input('city-click', 'value'),
     Input('alarm-rate-slider', 'value')])
def alarm_handler(city, rate):
    """Changes the display graph of supply-demand"""
    return alarm_visualization(city, rate)


if __name__ == '__main__':
    app.run_server(debug=True, port=1050, host='0.0.0.0')


