import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from datetime import datetime, timedelta
from database import fetch_all_wea_as_df

def map_plot(df):
    fig = go.Figure()
    dt_now = datetime.now()
    dt_last = dt_now - timedelta(days=365)
    df = df[df['datetime']>dt_last]
    df1, df2 = df[df['status']=='open'], df[df['status']=='closed']
    fig.add_trace(go.Scattermapbox(
            lat=df2["geo2"], lon=df2["geo1"],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10,
                opacity=0.5,
                color='rgb(64, 224, 178)'
            ),
            text=['disaster closed'],
    ))
    fig.add_trace(go.Scattermapbox(
            lat=df1["geo2"], lon=df1["geo1"],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=11,
                opacity=0.8,
                color='rgb(255, 127, 80)'
            ),
            text=['disaster open'],
    ))
    # fig.add_trace(px.scatter_mapbox(df, lat="geo2", lon="geo1", hover_name="title",
    #                     color = 'status', zoom=1.5, height=400,width=900))
    fig.update_layout(
        mapbox_style="white-bg",
        width=900,
        height=450,
        showlegend=False,
        #geo={'center':{'lon':30, 'lat':20}},
        mapbox_layers=[
            {"below": 'traces',
            "sourcetype": "raster",
            "source": [
            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]},
        ])
    fig.update_layout(template='plotly_dark', 
                      margin={"r":0,"t":0,"l":0,"b":0})
    return fig


def alarm_visualization(city, rate):
    """Changes the display graph of supply-demand"""
    if city not in ['LA','ST']:
        return go.Figure()
    df = fetch_all_wea_as_df(allow_cached=True)
    df = df[df['date']>datetime.now()-timedelta(days=21)].sort_values(by=['date'])
    if city == 'LA':
        df_u = df[df['lat']==34]
    elif city == 'ST':
        df_u = df[df['lat']==47]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_u['date'], y=df_u['temperatureHigh'], mode='lines', name='High Temperature',
                             line={'width': 2, 'color': 'orange'}))

    fig.update_layout(template='plotly_dark',
                      showlegend=True,
                      plot_bgcolor='#23272c',
                      paper_bgcolor='#23272c',
                      yaxis_title='Alarm Rate',
                      xaxis_title='Date/Time')
    return fig