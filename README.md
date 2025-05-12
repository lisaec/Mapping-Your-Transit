# Mapping Your Transit

### **Using publicly available GTFS data to automate production of interactive transit maps of your community**

Public transportation is an important tool that supports communities all over the world. It makes travel and social engagement more accessible, it creates jobs, eases traffic congestion, and its a greener alternative to driving. Mapping Your Transit is a project that celebrates your local transit network with fun and interactive maps. Leveraging the power of an open standard format for transit data, the General Transit Feed Specification (GTFS), this project allows users to upload data from any transit network to view an interactive map and download a custom poster of their favorite bus or subway system. 	

GTFS data is widely available for almost any regional transit organization in the United States, and a simple google search of “GTFS” and a city name will usually find a link to download the text files that make up a GTFS database. While transit maps are widely available for navigational purposes from regional agencies themselves, stylized “fun” transit maps can be hard to find. Using this standardized data, users can use this project to make cohesive, aesthetically pleasing maps for unique places with the click of a button.

## User Guide

### Set Up Instructions

This project uses [`uv`](https://github.com/astral-sh/uv) to handle dependencies and virtual environments.

If not already installed [`set up uv`] (https://docs.astral.sh/uv/getting-started/installation/)

Once UV is set up, you can navigate to the cloned repository and set up a virtual environment, which will copy over all required dependencies

```bash
uv venv
```

Then go ahead and run the main script to run the app

```bash
uv venv
uv run main.py
```

### Create Maps

After running main.py, the app will run on the given server and you will be able to access the interactive user interface. 
When using Mapping Your Transit, users can upload data or choose from an existing selection of cities. To try out the existing sample of GTFS data, use the dropdown menu to select your desired location. To upload your own data, drag and drop or select from your files a compressed (.zip) file containing a subfolder of GTFS data. The app will automatically display an interactive map of routes and stops. Click on each route to see it's name, and hover over each stop to see its name and the frequency of its departures. The app also creates a heatmap of the top ten most frequent routes and their hourly frequencies. 

Once you have uploaded or selected a GTFS feed, you will also have the option to download a poster map with or without the frequency heatmap. These posters are 11 x 17 inch wall posters showing routes and stops.

### Finding and using GTFS Data

GTFS data is publically available for most American transit networks. A google search of a city or transit agency name will usually result in a link to download the desired feed. It is recommended that GTFS data is sourced directly from an agency website, as this will provide the most accurate and up to date information. Transit agencies often have a GTFS subpage linked at the bottom of their website or under a "developers" page. If GTFS data is not available directly from the transit agency, you can also find data on Transit.land, an open data platform with GTFS feeds from 2,500 agencies. 

When downloading your own GTFS data, it is highly recommended that you rename the folder something unique and identifiable to the feed (ie not just "GTFS"), particularly if you intend to create multiple maps. 

While there is no hard upper limit on the size of GTFS feed that can be used in Mapping Your Transit, it is highly recommended to avoid extremely large feeds, as they will take a long time to process and may cause the app to crash. For large cities with complex transit systems, it is suggested to limit the GTFS data to a single mode of transit if individual feeds are available (eg only subway lines or bus routes). 

## GTFS Data
This project is built using GTFS Data, which is a well documented open standard data format used internationally to make transit data widely available to the public. Initially designed by Google engineers and known as Google Transit Feed Specification, it is a widely used standard that makes it possible for third party navigation apps to include transit modes of transportation in their trip planning. It is made up of several tables holding data on routes, stops, schedules, and geospatial features. 

Visit [GTFS.org](GTFS.org) to learn more about GTFS
- An overview of [GTFS Schedule](https://gtfs.org/documentation/overview/#gtfs-schedule)

There are two main types of GTFS Data: static and real time. GTFS realtime data includes live updates of vehicle locations and departures. This project uses GTFS static or “GTFS - Schedule” data, which is made up of fixed schedule, route, and stop information. There are 6 essential text files that make up a GTFS feed: stops, stop times, routes, agency, calendar, (or calendar dates), and trips. This project requires at least one inessential file, shapes, which contains necessary geospatial data. This file is included in most GTFS feeds. 

This project uses 5 of the essential GTFS Files and the shapes.txt files. **All of these files must be present in your uploaded zip folder to use Mapping Your Transit**

- **stops.txt** – Contains information about individual transit stops, including names, locations (latitude and longitude), and IDs.
- **stop_times.txt** – Details the scheduled arrival and departure times for each stop along a trip.
- **routes.txt** – Defines the transit routes, including route names and types (e.g., bus, subway).
- **agency.txt** – Provides information about the transit agency operating the service, such as name, URL, and timezone.
- **trips.txt** – Lists the individual trips for each route and service, linking routes, service calendars, and stop sequences.
- **shapes.txt** – Contains a list of coordinates associated with the shape of a trip. This is the only innessential file necessary for using Mapping Your Transit

## Project Structure

The source code used to create Mapping Your Transit can be found in the **src** folder and consists of 6 main scripts. 

- **feed.py** – Defines the 'feed' class. This class streamlines access to GTFS tables and simplifies internal processing.  Many components of this class were inspired by the gtfs_functions GitHub library, which was created to simplify working with GTFS data in python.
- **gui.py** – Develops the Mapping Your Transit graphical user interface using Dash.
- **posters.py** – Function to create 11x17 static poster maps showing routes, stops, and frequency information using matplotlib
- **my_sql.py** – Holds large sql queries used when building tables in the GTFS Database and calculating frequency data
- **heatmap.py** – Function to create interactive plotly figures of top route frequency by hour for user interface
- **interactive_maps.py** – Function to create interactive map for user interface using Folium, a python wraparound for javascript library leaflet

There is also a **data** folder that holds sample GTFS feeds and pre-created databases as well as a storage location for user-submitted data. There is also an output folder that stores created posters. 


## Methodology





 
