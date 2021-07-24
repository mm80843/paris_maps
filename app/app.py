import networkx as nx
import osmnx as ox 
 
import pandas as pd 
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import logging
import geopandas
import shapely
from geopy.geocoders import Nominatim
from scipy.spatial.distance import cdist
from shapely.wkt import loads
from functools import wraps
import time
#import pickle
import pickle5 as pickle
#import contextily as ctx

@st.cache(hash_funcs={pd.core.frame.DataFrame: id},allow_output_mutation=True)#allow_output_mutation=True)
def loadFile():
    with open('./data/Gf.pkl', 'rb') as input:
        G = pickle.load(input)
    with open('./data/ToI.pkl', 'rb') as input:
        ToI = pickle.load(input)
    with open('./data/LoI.pkl', 'rb') as input:
        LoI = pickle.load(input)
    gdNodes,gdStreets = ox.utils_graph.graph_to_gdfs(G)
    return G, gdNodes, gdStreets, ToI, LoI

#Loading the data
G, gdNodes, gdStreets, ToI, LoI = loadFile()

def getPaths(route,gdStreets):
    path = []
    for k in range(len(route)-1):
        path.append(   geopandas.GeoDataFrame(gdStreets.loc[route[k],route[k+1]].loc[0]).T  )
    path1  = geopandas.GeoDataFrame(pd.concat(path),crs="EPSG:4326").to_crs(epsg=3857)
    viz = path1.buffer(100)
    path2  = geopandas.GeoDataFrame(pd.concat(path),crs="EPSG:4326")
    viz2 = path2.buffer(0.0005)
    return path1,viz, path2, viz2

# Writing the sidebar
HOME = 2.3550362,48.8869476
WORK = 2.3709643,48.8657564

st.sidebar.write("### Parameters")




home = ox.distance.nearest_nodes(G, 2.3550362,48.8869476)
work = ox.distance.nearest_nodes(G, 2.3709643,48.8657564)

# Calculating subjective length
gdStreets["vLength"] = gdStreets.length / ( 1 + gdStreets.trees )
# Rebuilding the graph
G = ox.utils_graph.graph_from_gdfs(gdNodes,gdStreets)

# Getting shortest path
routeShort = nx.shortest_path(G, home, work, 'length')
routeTrees = nx.shortest_path(G, home, work, 'vLength')
# And corresponding geodata
pathS,vizS,pS,vS = getPaths(routeShort,gdStreets)
pathT,vizT,pT,vT = getPaths(routeTrees,gdStreets)

def plot_path(origin_point, destination_point):
    
    """
    Given a list of latitudes and longitudes, origin 
    and destination point, plots a path on a map
    
    Parameters
    ----------
    lat, long: list of latitudes and longitudes
    origin_point, destination_point: co-ordinates of origin
    and destination
    Returns
    -------
    Nothing. Only shows the map.
    """
    
    # we will store the longitudes and latitudes in following list 
    lon = [] 
    lat = []  
    for i in routeTrees:
        point = G.nodes[i]
        lon.append(point['x'])
        lat.append(point['y'])
    
    
    # adding the lines joining the nodes
    fig = go.Figure(go.Scattermapbox(
        name = "Trees",
        mode = "lines",
        lon = lon,
        lat = lat,
        marker = {'size': 10},
        line = dict(width = 4.5, color = 'blue')))
    # adding source marker
    
    lon = []
    lat = []
    for i in routeShort:
        point = G.nodes[i]
        lon.append(point['x'])
        lat.append(point['y'])
    
    fig.add_trace(go.Scattermapbox(
        name = "Short",
        mode = "lines",
        lon = lon,
        lat = lat,
        marker = {'size': 8},
        line = dict(width = 4.5, color = 'red')))
    # adding source marker
    
    
    fig.add_trace(go.Scattermapbox(
        name = "Source",
        mode = "markers",
        lon = [origin_point[0]],
        lat = [origin_point[1]],
        marker = {'size': 12, 'color':"red"}))
     
    # adding destination marker
    fig.add_trace(go.Scattermapbox(
        name = "Destination",
        mode = "markers",
        lon = [destination_point[0]],
        lat = [destination_point[1]],
        marker = {'size': 12, 'color':'green'}))
    
    Trees = ToI[ToI.within(vT.unary_union)]
    lats = [p.y for p in Trees.geometry]
    lons = [p.x for p in Trees.geometry]    
    fig.add_trace(go.Scattermapbox(
        name = "Trees",
        mode = "markers",
        lon = lons,
        lat = lats,
        marker = {'size': 10, 'color':"green", 'opacity':1}))

    
    Lights = LoI[LoI.within(vT.unary_union)]
    lats = [p.y for p in Lights.geometry]
    lons = [p.x for p in Lights.geometry]    
    fig.add_trace(go.Scattermapbox(
        name = "Lights",
        mode = "markers",
        lon = lons,
        lat = lats,
        marker = {'size': 3, 'color':"yellow", 'opacity':0.9}))
    
    
    # getting center for plots:
    lat_center = np.mean(lat)
    long_center = np.mean(lon)
    # defining the layout using mapbox_style
    fig.update_layout(mapbox_style="stamen-terrain",
        mapbox_center_lat = 30, mapbox_center_lon=-80)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      mapbox = {
                          'center': {'lat': lat_center, 
                          'lon': long_center},
                          'zoom': 13})
    return fig

origin_point = (HOME) 
destination_point = (WORK)

fig = plot_path(origin_point, destination_point)


st.write(fig)