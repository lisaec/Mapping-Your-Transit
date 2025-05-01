
from dash import Dash, html, dcc, Input, Output, callback, State
import dash
import base64
import zipfile
import uuid
import shutil

import importlib

from src import feed
from src import interactive_maps
from src import posters
importlib.reload(feed)
importlib.reload(feed)


import os

import warnings
warnings.filterwarnings('ignore')


def run_app() -> None:
    app = Dash(__name__)
    app.title = 'Mapping Your Transit'

    create_layout(app)
    register_callbacks(app)

    app.run(debug=False)

def create_layout(app: Dash) -> None:
    layout = html.Div(
        id='main-div',
        children=[
            html.H1('Mapping Your Transit'),
            html.Hr(),
            html.H3("Create an interactive transit map by uploading your General Transit Feed Specification (GTFS) Folder below or select from the example transit systems"),

            # Side-by-side container for dropdown and upload
            html.Div(
                style={'display': 'flex', 'gap': '20px', 'alignItems': 'center'},
                children=[
                    dcc.Dropdown(
                        options=[
                            {'label': 'Williamsburg', 'value': 'Williamsburg'},
                            {'label': 'New York City Subway', 'value': 'New York'},
                            {'label': 'San Luis Obispo', 'value': 'San Luis Obispo'}
                        ],
                        value= None,
                        id='demo-dropdown',
                        style={'width': '50%'}
                    ),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop Compressed GTFS Folder or ',
                            html.A('Select File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'padding': '0 10px'
                        },
                        multiple=False
                    )
                ]
            ),

            html.Div(id='dd-output-container'),
            html.Div(id='output-data-upload'),

            # Map display panel
            html.Div(id='map-container', style={'marginTop': '20px'}),
            html.Br(),

            html.Button("Download Poster Map", id="btn_txt"),
            dcc.Download(id="download_text_index"),

            #active feed storage
            dcc.Store(id='active-feed-string')
        ]
    )

    app.layout = layout

    return None


def register_callbacks(app):
    @app.callback(
        Output('map-container', 'children'),
        Output('active-feed-string', 'data'),
        Input('upload-data', 'contents'),
        Input('demo-dropdown', 'value'),
        State('upload-data', 'filename')
    )
    def update_map(contents, demo_choice, filename):

        if contents is not None:
            # User uploaded a file
            return read_feed(contents, filename)
        
        elif demo_choice:
            # User picked a sample dataset
            return load_sample_feed(demo_choice)
        
        else:
            # Neither uploaded nor selected
            return html.Div("No map loaded yet.", style={"height": "600px", "backgroundColor": "#f9f9f9", "textAlign": "center", "lineHeight": "600px"}), None
        
#callback for poster download
    @app.callback(
    Output("download_text_index", "data"),
    Input("btn_txt", "n_clicks"),
    State('active-feed-string', 'data'),  # <-- use State here
    prevent_initial_call=True
)
    def throw_poster(n_clicks, filename):
        if not filename:
            return None  # no feed selected, nothing to generate

        poster_file = posters.map(feed.Feed(filename))
        return dcc.send_file(poster_file) 

def read_feed(contents, filename):
    #contents is what is uploaded, filename the original file name "folder.zip"
    
    # Interpreting contents: upload -> filename for unzipped folder of gtfs data

    #decoding contents
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Save uploaded zip
    zip_path = os.path.join('data/user_data/gtfs_files/zipped_files', filename)
    with open(zip_path, 'wb') as f:
        f.write(decoded)

    #unzipping into a folder in gtfs_files folder
    gtfs_folder_name = filename.replace('.zip', '') #folder name
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('data/user_data/gtfs_files') #extract to that folder

    # Create the Feed and map
    feed_filename = os.path.join('data/user_data/gtfs_files', gtfs_folder_name)
    gtfs_feed = feed.Feed(feed_filename)
    folium_map = interactive_maps.live_map(gtfs_feed)
    map_html = folium_map.get_root().render()

 

    return html.Iframe(srcDoc=map_html, width='50%', height='600', style={"border": "none"}), feed_filename 


def load_sample_feed(demo_choice):

    sample_feed_path = "data/samples/gtfs_files"
    sample_paths = {
        'New York': 'gtfs_nyc',
        'Williamsburg': 'gtfs_wata',
        'San Luis Obispo' : 'gtfs_slo'
    }
    
    gtfs_folder_path = os.path.join(sample_feed_path, sample_paths.get(demo_choice))

    # Create the Feed and map
    gtfs_feed = feed.Feed(gtfs_folder_path)
    folium_map = interactive_maps.live_map(gtfs_feed)
    map_html = folium_map.get_root().render()

    return html.Iframe(srcDoc=map_html, width='50%', height='600', style={"border": "none"}), gtfs_folder_path
