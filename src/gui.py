
from dash import Dash, html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
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
importlib.reload(posters)

import os

import warnings
warnings.filterwarnings('ignore')


def run_app() -> None:
    app = Dash(__name__, 
                external_stylesheets=[dbc.themes.DARKLY])
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
            html.H4("Create an interactive transit map by uploading your General Transit Feed Specification (GTFS) Folder below or select from the example transit systems"),

            # Side-by-side container for dropdown and upload
            html.Div(
                style={'display': 'flex', 'gap': '50px', 'alignItems': 'center'},
                children=[
                        dcc.Dropdown(
                            id='demo-dropdown',
                            options=[
                                {'label': 'Williamsburg', 'value': 'Williamsburg'},
                                {'label': 'New York City Subway', 'value': 'New York'},
                                {'label': 'San Luis Obispo', 'value': 'San Luis Obispo'}
                            ],
                            value = None,
                            placeholder="Select a sample feed",
                                style={
                            'width': '100%',
                            'color': 'black',
                            'backgroundColor': 'white'
                        }
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

            # Map display panel

            html.Div(
                style={'display': 'flex', 'gap': '50px', 'alignItems': 'center'},
                children=[

                    html.Div(
                                id='map-container',
                                children= html.Div(
                                    "No map loaded yet.",
                                    style={
                                        "height": "600px",
                                        "backgroundColor": "#f9f9f9",
                                        "textAlign": "center",
                                        "lineHeight": "600px",
                                        "color": "#666",
                                        "fontStyle": "italic"
                                    }
                                ),
                                style={
                                    'marginTop': '20px',
                                    'width': '70%',
                                    'marginLeft': 'auto',
                                    'marginRight': '0'
                                }
                            ),
                    html.Br(),

                    html.Div(
                        [html.Label("Include Frequency Summary?"),
                            dcc.RadioItems(
                                id='include-summary-input',
                                options=[
                                    {'label': 'Yes', 'value': True},
                                    {'label': 'No', 'value': False}
                                ],
                                value= True,  # default choice
                                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                            ),
                            html.Br(), 
                            dbc.Button("Download Poster Map", id="btn_txt", color = "secondary", className="me-1")
                        ]
                    ),

                    dcc.Download(id="download_text_index")
                ]
            ),

            # active feed storage
            dcc.Store(id='active-feed-string')
        ]
    )

    app.layout = layout



def register_callbacks(app):
    @app.callback(
        Output('map-container', 'children'),
        Output('active-feed-string', 'data'),
        Input('upload-data', 'contents'),
        Input('demo-dropdown', 'value'),
        State('upload-data', 'filename')
    )
    def update_map(contents, demo_choice, filename):

        placeholder = html.Div(
            "Select a Transit Feed",
            style={
                "height": "600px",
                "backgroundColor": "#f9f9f9",
                "textAlign": "center",
                "lineHeight": "600px",
                "color": "#666",
            })
        
        def label_box(feed):
            return html.Div(
                feed.agency_name(),
                style={
                    "marginTop": "20px",
                    "textAlign": "center",
                    "padding": "10px",
                    "border": "1px solid black",
                    "borderRadius": "0px",
                    "color": "black",
                    "fontWeight": "bold",
                    "backgroundColor": "#f0f8ff",
                    "width": "60%",
                    "marginLeft": "auto",
                    "marginRight": "auto"
                }
            )
        def website_box(feed):
                return html.Div(children=html.A(f"Agency Website", href=feed.agency_url(), target="_blank"),
                style={
                    "marginTop": "20px",
                    "textAlign": "center",
                    "padding": "10px",
                    "border": "1px solid black",
                    "borderRadius": "0px",
                    "color": "black",
                    "textDecoration": "none",
                    "fontWeight": "bold",
                    "backgroundColor": "#f0f8ff",
                    "width": "60%",
                    "marginLeft": "auto",
                    "marginRight": "auto"
                }
            )

        if contents is not None:
            # User uploaded a file
            map_frame, feed_path = read_feed(contents, filename)
            return html.Div([
                map_frame,
                label_box(feed.Feed(feed_path)),
                website_box(feed.Feed(feed_path))
            ]), feed_path

        elif demo_choice:
            # User picked a sample dataset
            map_frame, feed_path = load_sample_feed(demo_choice)
            return html.Div([
                map_frame,
                label_box(feed.Feed(feed_path)),
                website_box(feed.Feed(feed_path))
            ]), feed_path
        
        else:
            # Neither uploaded nor selected
            return placeholder, None
        
#callback for poster download
    @app.callback(
    Output("download_text_index", "data"),
    Input("btn_txt", "n_clicks"),
    State('active-feed-string', 'data'),  
    State('include-summary-input', 'value'),
    prevent_initial_call=True
)
    def throw_poster(n_clicks, filename, heatmap_choice):
        if not filename:
            return None  # no feed selected, nothing to generate

        poster_file = posters.map(feed.Feed(filename), Heatmap = heatmap_choice)
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

    return html.Iframe(srcDoc=map_html, width='70%', height='600', style={"border": "none"}), feed_filename 


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

    return html.Iframe(srcDoc=map_html, width='70%', height='600', style={"border": "none"}), gtfs_folder_path
