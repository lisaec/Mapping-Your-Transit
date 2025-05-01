import geopandas as gpd
from shapely.geometry import LineString
from src.feed import *
import folium
import warnings
import numpy as np
warnings.filterwarnings('ignore')

def live_map(feed):
    m = folium.Map(location= feed.center_pt(), zoom_start=12, tiles="Cartodb Positron")

    for index,row in feed.trips_shapes_routes().iterrows():

        folium.PolyLine(row.shape_points.coords,
                        color= f'#{row.route_color}',
                        weight=2.5,
                        opacity=1,
                        popup = f'Route: {row.route_short_name} - {row.route_long_name}'
                       ).add_to(m)

    for index, row in feed.stops().iterrows():
        folium.CircleMarker(
                location=[row['stop_lat'], row['stop_lon']],
                radius = 2,
                fill=True,
                fill_color = 'white',
                color = 'black',
                weight = 1,
                tooltip= f'{row.stop_name}'

            ).add_to(m)
        
    
    m.save(f"data/outputs/live_map_html/{feed.name}.html")

    return m


#keep if adding tool tips
# location_types = {
#     None : "Stop (or Platform)",
#     0: "Stop (or Platform)",
#     1: "Station",
#     2: "Entrance/Exit",
#     3: "Generic Node",
#     4: "Boarding Area"
# }