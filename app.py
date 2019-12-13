import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from database import fetch_all_dis_as_df
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
        In this part we will give a visualization of recent disasters.
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
                html.H6("Disaster Status", style={'fontSize': '1.5rem', 'paddingLeft': '54px', 'color': '#a3a7b0',
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
                html.H5("Disaster Kind", style={'fontSize': '1.5rem',
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



def what_if_description():
    """
    Returns description of "What-If" - the interactive component
    """
    return html.Div(children=[
        dcc.Markdown('''
        # " What If "
        This is the what if description.''', className='eleven columns', style={'paddingLeft': '5%'})
    ], className="row")

def what_if_tool():
    """
    Returns the What-If tool as a dash `html.Div`. The view is a 8:3 division between
    demand-supply plot and rescale sliders.
    """
    return html.Div(children=[
        html.Div(children=[dcc.Graph(id='what-if-figure')], className='nine columns'),

        html.Div(children=[
            html.H5("Rescale Power Supply", style={'marginTop': '2rem'}),
            html.Div(children=[
                dcc.Slider(id='wind-scale-slider', min=0, max=4, step=0.1, value=2.5, className='row',
                           marks={x: str(x) for x in np.arange(0, 4.1, 1)})
            ], style={'marginTop': '5rem'}),

            html.Div(id='wind-scale-text', style={'marginTop': '1rem'}),

            html.Div(children=[
                dcc.Slider(id='hydro-scale-slider', min=0, max=4, step=0.1, value=0,
                           className='row', marks={x: str(x) for x in np.arange(0, 4.1, 1)})
            ], style={'marginTop': '3rem'}),
            html.Div(id='hydro-scale-text', style={'marginTop': '1rem'}),
        ], className='three columns', style={'marginLeft': 5, 'marginTop': '10%'}),
    ], className='row eleven columns')




def architecture_summary():
    """
    Returns the text and image of architecture summary of the project.
    """
    return html.Div(children=[
        dcc.Markdown('''
            # Project Architecture
            project architecture.
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
    # dcc.Graph(id='trend-graph', figure=static_stacked_trend_graph(stack=False)),
    #dcc.Graph(id='stacked-trend-graph', figure=static_stacked_trend_graph(stack=True)),
    what_if_description(),
    what_if_tool(),
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
    return map_plot(df[(df['title'] == disaster) & df.status.isin(status)])

@app.callback(
    dash.dependencies.Output('wind-scale-text', 'children'),
    [dash.dependencies.Input('wind-scale-slider', 'value')])
def update_wind_sacle_text(value):
    """Changes the display text of the wind slider"""
    return "Wind Power Scale {:.2f}x".format(value)


@app.callback(
    dash.dependencies.Output('hydro-scale-text', 'children'),
    [dash.dependencies.Input('hydro-scale-slider', 'value')])
def update_hydro_sacle_text(value):
    """Changes the display text of the hydro slider"""
    return "Hydro Power Scale {:.2f}x".format(value)


_what_if_data_cache = None


@app.callback(
    dash.dependencies.Output('what-if-figure', 'figure'),
    [dash.dependencies.Input('wind-scale-slider', 'value'),
     dash.dependencies.Input('hydro-scale-slider', 'value')])
def what_if_handler(wind, hydro):
    """Changes the display graph of supply-demand"""
    ##df = fetch_all_dis_as_df(allow_cached=True)
    fig = go.Figure()
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=1050, host='0.0.0.0')


