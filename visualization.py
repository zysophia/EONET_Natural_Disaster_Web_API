import pandas as pd
import plotly.express as px

def map_plot(df):
    fig = px.scatter_mapbox(df, lat="geo2", lon="geo1", hover_name="title", hoverinfo='none',
                        color = 'status', zoom=1.5, height=400,width=900)
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {"below": 'traces',
                "sourcetype": "raster",
                "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]}
          ])
    fig.update_layout(template='plotly_dark', 
                      margin={"r":0,"t":0,"l":0,"b":0})
    return fig