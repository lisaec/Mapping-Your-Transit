import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Type
import folium
from src import my_sql
import sqlite3
import geopandas as gpd
from shapely.geometry import LineString


#creating a class for reading in the feed data

class Feed:

    
    def __init__(
    self,
    gtfs_path: str
    ):
        self._gtfs_path = gtfs_path
        self.name = os.path.basename(os.path.normpath(gtfs_path))
        self.parent_dir = os.path.dirname(os.path.dirname(gtfs_path))
        self.db_path = os.path.join(self.parent_dir, "databases", f"{self.name}.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._insert_data()

    #file overviews
    def gtfs_path(self):
        return self._gtfs_path
    
    def get_files(self):
        return os.listdir(self._gtfs_path)
    
    #methods to access each file
    
    #essential files present in all GTFS (not true in practice but acc to documentation?)
    def stops(self):
        return extract_file('stops.txt', self)
    
    def routes(self):
        return extract_file('routes.txt', self)
    
    def trips(self):
        return extract_file('trips.txt', self)
    
    def agency(self):
        return extract_file('agency.txt', self)

    def calendar_dates(self):
        return extract_file('calendar_dates.txt', self)

    def stop_times(self):
        return extract_file('stop_times.txt', self)

    def calendar(self):
        return extract_file('calendar_dates.txt', self)
    
   #additional files I will use - need to implement error messaging if not available
    def shapes(self):
        return extract_file('shapes.txt', self)
    
    def transfers(self):
        return extract_file('transfers.txt', self)
    
    #Building a database
    def _create_tables(self):
        table_statements = my_sql.build_tables

        for statement in table_statements:
            self.cursor.execute(statement)
        self.conn.commit()

    def _insert_data(self):
        self.agency().to_sql('agency', self.conn, if_exists='replace', index=False)
        self.stops().to_sql('stops', self.conn, if_exists='replace', index=False)
        self.shapes().to_sql('shapes', self.conn, if_exists='replace', index=False)
        self.routes().to_sql('routes', self.conn, if_exists='replace', index=False)
        self.trips().to_sql('trips', self.conn, if_exists='replace', index=False)
        # self.transfers().to_sql('transfers', self.conn, if_exists='replace', index=False)
        # self.calendar_dates().to_sql('calendar_dates', self.conn, if_exists='replace', index=False)
        self.stop_times().to_sql('stop_times', self.conn, if_exists='replace', index=False)

    def close(self):
        self.conn.close()
    
    #spatial features
    def center_pt(self) -> tuple[int, int]:
        """Returns a lat/lon tuple of the center of the transit network"""
        center = [self.shapes()['shape_pt_lat'].mean(), self.shapes()['shape_pt_lon'].mean()]
        return center
    
    def shape_pts(self)-> pd.Series:
        """returns series with the points on each route as a list of Linestring coordinate tuples
        currently slow and doesn't access database"""
        
        shape_points = self.shapes().groupby("shape_id")[["shape_pt_lat", "shape_pt_lon"]].apply(
            lambda g: LineString(g.values))
        
        #naming series for later joins
        shape_points.name = 'shape_points'
    
        return shape_points
    
    def trips_shapes_routes(self) -> pd.DataFrame:
        sql = """ SELECT * FROM trips 
                 JOIN routes USING (route_id)
                 
                 WHERE shape_id IS NOT NULL
                 and route_color IS NOT NULL;"""
        
        trips_routes = pd.read_sql(sql, self.conn)
        trips_shapes_routes = trips_routes.join(self.shape_pts(), on='shape_id')
        trips_shapes_routes = gpd.GeoDataFrame(trips_shapes_routes, geometry= "shape_points")
        
        
        return trips_shapes_routes
    
    #other functions
    
    def agency_name(self) -> str:
        "Returns agency name as a string"
        return self.agency()['agency_name'][0]
    
    
def extract_file(file: str, feed: Type['Feed']):

    files = feed.get_files()
    gtfs_path = feed.gtfs_path()
    
    file_path = f"{gtfs_path}/{file}"

    if file in files:
        data = pd.read_csv(file_path)
        return data
    
    else:
        print(f'File "{file_path}" is missing.')
        return None

