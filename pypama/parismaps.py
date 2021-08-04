import networkx as nx
import osmnx as ox 
import os
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
    fn = os.path.join(os.path.dirname(__file__), '../pkls/Gf.pklz')
    with open(fn, 'rb') as input:
        graph = pickle.load(input)
    fn = os.path.join(os.path.dirname(__file__), '../pkls/ToI.pklz')
    with open(fn, 'rb') as input:
        trees = pickle.load(input)
    fn = os.path.join(os.path.dirname(__file__), '../pkls/LoI.pklz')
    with open(fn, 'rb') as input:
        lights = pickle.load(input)
    nodes , streets = ox.utils_graph.graph_to_gdfs(graph)
    return graph, nodes, streets, lights, trees, graph

class parisMap: 

    def __init__(self):
        """Init
        """ 
        self.graph, self.nodes, self.streets, self.lights, self.trees, self.graph = loadFiles()
        # Values for FROM and TO, worth renaming later
        self.HOME = 2.3550362,48.8869476 # Tentative departure
        self.WORK = 2.3709643,48.8657564 # Tentative arrival
        self.streets = self.streets.sort_index()
        self.nodes = self.nodes.sort_index()
        self.debug = False


    def getPaths(self,route,gdStreets):
        self.path = []
        for k in range(len(route)-1):
            # adding all waypoints from the route
            # https://stackoverflow.com/questions/54307300/what-causes-indexing-past-lexsort-depth-warning-in-pandas
            self.path.append(   geopandas.GeoDataFrame(self.streets.loc[route[k],route[k+1]].loc[0]).T  )
        
        self.path1  = geopandas.GeoDataFrame(pd.concat(self.path),crs="EPSG:4326").to_crs(epsg=3857)
        self.viz = self.path1.buffer(100)
        # @todo: why two different projections??
        self.path2  = geopandas.GeoDataFrame(pd.concat(self.path),crs="EPSG:4326")
        self.viz2 = self.path2.buffer(0.0005)

        return self.path1,self.viz,self.path2,self.viz2

    def findClosest(self,start,end):
        self.home = ox.distance.nearest_nodes(self.graph, start[0],start[1])
        self.work = ox.distance.nearest_nodes(self.graph, end[0],end[1])
        if self.debug:
            print(self.home,self.work)
        return self.home, self.work

    def calculatePath(self,pTrees,pLights,pGreenSpace,pFreshplace):
        # Calculating subjective length
        self.streets["vLength"] = self.streets.length
        self.streets["vLength"] = self.streets.vLength / ( 1 + pTrees*self.streets.trees/1000.0 )
        self.streets["vLength"] = self.streets.vLength / ( 1 + pLights*self.streets.lights/1000.0 )
        self.streets["vLength"] = self.streets.vLength / ( 1 + pGreenSpace*self.streets.pgreenspaces/1000.0 )
        self.streets["vLength"] = self.streets.vLength / ( 1 + pFreshplace*self.streets.pfreshplaces/1000.0 )      
        # Rebuilding the graph
        self.newG = ox.utils_graph.graph_from_gdfs(self.nodes,self.streets)

        # Getting shortest path
        self.routeShort = nx.shortest_path(self.newG, self.home, self.work, 'length')
        self.routeTrees = nx.shortest_path(self.newG, self.home, self.work, 'vLength')
        # And corresponding geodata
        self.pathS,self.vizS,self.pS,self.vS = self.getPaths(self.routeShort,self.streets)
        self.pathT,self.vizT,self.pT,self.vT = self.getPaths(self.routeTrees,self.streets)
        
        return self.newG


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
