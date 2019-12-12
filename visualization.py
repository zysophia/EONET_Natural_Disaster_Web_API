import pandas as pd
import plotly.express as px

def map_plot(df,col=["orange"]):
    fig = px.scatter_mapbox(df, lat="geo2", lon="geo1", hover_name="title",
                        color_discrete_sequence=col, zoom=1.5, height=600,width=1200)
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
                      margin={"r":100,"t":100,"l":100,"b":100})
    return fig