import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from datetime import datetime, timedelta
from database import fetch_all_wea_as_df, fetch_all_dis_as_df
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestRegressor
from prediction import kde as kde_func
import numpy as np

import pickle

def alarm_predict(city='LA', arate=1):
    rate_d = {1:'002', 2:'005', 3:'010'}
    fname = 'processed_data/rf_'+rate_d[arate]+'_'+city.lower()+'.pickle'
    reg = pickle.load(open(fname, 'rb'))
    if city not in ['LA', 'ST']:
        return None
    dfx = fetch_all_wea_as_df()
    dfx = dfx[dfx['date']>datetime.now()-timedelta(days=1)].sort_values(by='date')
    if city=='LA':
        dfx = dfx[dfx['lat']==34]
    else:
        dfx = dfx[dfx['lat']==47]
    X_test = dfx.drop('date',1).values

    return dfx['date'], reg.predict(X_test)

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
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df_u['date'], y=df_u['temperatureHigh'], mode='lines', name='High Temperature',
                             line={'width': 2, 'color': 'orange'}), secondary_y=False)

    try:                         
        d2, y2 = alarm_predict(city, rate)
        rate_f = {1:0.2, 2: 0.5, 3:1}
        dfkde = kde_func(fetch_all_dis_as_df(), rate_f[rate], city.lower()).sort_values(by='date')
        # print(dfkde)
        fig.add_trace(go.Scatter(x=dfkde['date'], y=np.exp(dfkde['kde']), mode='lines', name='Real WildFire Rate', 
                                fill='tozeroy', line={'width': 2, 'color': 'pink'}, stackgroup='stack'), secondary_y=True)
        fig.add_trace(go.Scatter(x=d2, y=np.exp(y2), mode='lines', name='Predicted WildFire Rate',fill='tozeroy',
                                line={'width': 2, 'color': 'red'}, stackgroup='stack'), secondary_y=True)
    except:
        pass


    fig.update_layout(template='plotly_dark',
                      showlegend=True,
                      plot_bgcolor='#23272c',
                      paper_bgcolor='#23272c',
                      yaxis_title='Alarm Rate',
                      xaxis_title='Date/Time',
                      )
    return fig

if __name__=='__main__':
    print(alarm_predict(city='LA', arate=1))