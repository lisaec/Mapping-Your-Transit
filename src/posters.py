from src import feed
import importlib
import geopandas as gpd
from matplotlib.lines import Line2D
from shapely.geometry import LineString
from src.feed import *
importlib.reload(feed)

import matplotlib.pyplot as plt
from cartopy import crs as ccrs, feature as cfeature
import cartopy.io.img_tiles as cimgt

import warnings
warnings.filterwarnings('ignore')

def map(feed):

    # Set up the plot
    fig, ax = plt.subplots(figsize=(11, 17))


    minx, miny, maxx, maxy = feed.trips_shapes_routes().total_bounds
    extent = [minx - 0.001, maxx + 0.001, miny - 0.001, maxy + 0.001]
    ax.axis(extent)
    # ax.axis('off')
    
    # Plot each LineString
    for index,row in feed.trips_shapes_routes().iterrows():
        x, y = row.shape_points.xy
        ax.plot(x, y,
                      linewidth=2, 
                      color = f"#{row.route_color}")

    for index,row in feed.stops().iterrows():
        x, y = row.stop_lat, row.stop_lon
        ax.plot(x, y, marker="o", color="black", 
            markerfacecolor="white",
            markeredgecolor="black",
            markeredgewidth= 1,
                markersize=3)
        
    fig.patch.set_facecolor('#f0f0f0')  # Light gray background
    ax.set_facecolor('#fafafa')
    
        # Turn off ticks, keep frame
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("black")
        spine.set_linewidth(1.5)
    
    ax.set_position([0.01, 0.01, .99, .99])  # Left, bottom, width, height

    # Add a title
    ax.set_title(feed.agency_name(),
                 fontsize=24, 
                 weight='black', 
                 pad=10,
                 loc = "right",
                fontname='Helvetica')
    
    #legend
    legend_entries = (
        feed.routes()[['route_short_name','route_long_name', 'route_color']]
        .sort_values('route_short_name').dropna()  # Optional: alphabetical
    )
    

    y_position = 0.98  # Starting y position for the legend
    legend_box_props = dict(boxstyle="round,pad=0.3",
                            facecolor="white", 
                            edgecolor="black", linewidth=1)
    
    legend_entries['full_label'] = legend_entries['route_short_name'] + " - " + legend_entries['route_long_name'] + " "
    longest_label = legend_entries['full_label'].iloc[legend_entries['full_label'].str.len().idxmax()]

    #add box
    n_lines = len(legend_entries)
    
    ax.text(
        .98, y_position+0.005,
        "\n".join([" "*(len(longest_label)+20) for _ in range(round(n_lines *1.4))]),  # dummy placeholder
        transform=ax.transAxes,
        bbox=legend_box_props,
        fontsize=12,
        verticalalignment='top',
           horizontalalignment='right'
        )
    

    for _, row in legend_entries.iterrows():
        route_name = f"{row['route_short_name']} - {row['route_long_name']} "
        route_color = f"#{row['route_color']}"
        # Place each route in the legend with colored text
        ax.text(
            0.98, y_position, route_name, color=route_color,
            transform=ax.transAxes,
            fontsize=12, verticalalignment='top',
            horizontalalignment='right', fontweight='bold',
            fontname = "Helvetica"
        )

        # Adjust the y_position to space out the text
        y_position -= 0.015  # Decrease this value for tighter spacing



    plt.savefig(f'data/outputs/posters/{feed.name}.png', dpi = 500, bbox_inches='tight', pad_inches=0.25)
    
    return f'data/outputs/posters/{feed.name}.png'
    