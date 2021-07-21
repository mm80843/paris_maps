import networkx as nx
import osmnx as ox 
 
import pandas as pd  
import numpy as np
import plotly.graph_objects as go 
import geopandas 
from geopy.geocoders import Nominatim
from scipy.spatial.distance import cdist
from shapely.wkt import loads
from functools import wraps  
import pickle5 as pickle 

def loadFiles():
    with open('../pkls/Gf.pklz', 'rb') as input:
        graph = pickle.load(input)
    with open('../pkls/ToI.pklz', 'rb') as input:
        trees = pickle.load(input)
    with open('../pkls/LoI.pklz', 'rb') as input:
        lights = pickle.load(input)
    nodes , streets = ox.utils_graph.graph_to_gdfs(graph)
    return graph, nodes, streets, lights, trees, graph

class parisMap: 

    def __init__(self):
        """Init
        """ 
        self.graph, self.nodes, self.streets, self.lights, self.trees, self.graph = loadFiles()
        self.HOME = 2.3550362,48.8869476
        self.WORK = 2.3709643,48.8657564


    def getPaths(self,route,gdStreets):
        self.path = []
        for k in range(len(route)-1):
            self.path.append(   geopandas.GeoDataFrame(self.streets.loc[route[k],route[k+1]].loc[0]).T  )
        
        self.path1  = geopandas.GeoDataFrame(pd.concat(self.path),crs="EPSG:4326").to_crs(epsg=3857)
        self.viz = self.path1.buffer(100)
        
        self.path2  = geopandas.GeoDataFrame(pd.concat(self.path),crs="EPSG:4326")
        self.viz2 = self.path2.buffer(0.0005)

        return 1

    def findClosest(self):
        self.home = ox.distance.nearest_nodes(self.graph, 2.3550362,48.8869476)
        self.work = ox.distance.nearest_nodes(self.graph, 2.3709643,48.8657564)

    def calculatePath(self):
        # Calculating subjective length
        self.streets["vLength"] = self.streets.length / ( 1 + self.streets.trees )
        # Rebuilding the graph
        self.newG = ox.utils_graph.graph_from_gdfs(self.nodes,self.streets)

        # Getting shortest path
        self.routeShort = nx.shortest_path(self.newG, self.home, self.work, 'length')
        self.routeTrees = nx.shortest_path(self.newG, self.home, self.work, 'vLength')
        # And corresponding geodata
        pathS,vizS,pS,vS = self.getPaths(self.routeShort,self.gdStreets)
        pathT,vizT,pT,vT = self.getPaths(self.routeTrees,self.gdStreets)

def plot_path(G, origin_point, destination_point, routeTrees, routeShort, ToI, LoI, vT):
    
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
