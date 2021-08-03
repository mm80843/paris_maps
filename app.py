import streamlit as st

import requests
import json
import numpy as np

import plotly.graph_objects as go 
from geopy.geocoders import Nominatim

SERVER_URL = "http://127.0.0.1:8000/find_path"
DICT = {}

st.set_page_config(layout="wide")

st.sidebar.write("### Places")

START = st.sidebar.text_input("Start", "4 rue myrha 75018 paris")
END = st.sidebar.text_input("Target", "33 avenue de la république 75011 PARIS")


st.sidebar.write("### Parameters")


pTrees = st.sidebar.number_input(label="Trees", \
    min_value=0.00,value=2.0,step=2.0)
pLights = st.sidebar.number_input(label="Lights", \
    min_value=0.00,value=2.0,step=2.0)
pGreenSpace = st.sidebar.number_input(label="Green spaces", \
    min_value=0.00,value=2.0,step=2.0)
pFreshplace = st.sidebar.number_input(label="Fresh spaces", \
    min_value=0.00,value=2.0,step=2.0)

DICT["id"]          = "Luc"
DICT["pTrees"]      = pTrees
DICT["pLights"]     = pLights
DICT["pGreenSpace"] = pGreenSpace
DICT["pFreshplace"] = pFreshplace

geolocator = Nominatim(user_agent="pypama")
location = geolocator.geocode(START)
DICT["sLon"], DICT["sLat"] = location.longitude, location.latitude
location = geolocator.geocode(END)
DICT["eLon"], DICT["eLat"] = location.longitude, location.latitude


payload = json.dumps(DICT, sort_keys=True, indent=4)

st.write("## Payload")
st.write(payload)

response = requests.post(SERVER_URL, data = payload)
 

PREF = response.json()["nodesPrefs"]
PREF = PREF[2:-2].split("), (")
lon = []
lat = []
for k in PREF:
    LON = float(k.split(", ")[0])
    LAT = float(k.split(", ")[1])  
    lon.append(LON)
    lat.append(LAT) 
#st.write(PREF)
#st.write(lat)
#st.write(lon)
# adding the lines joining the nodes
fig = go.Figure(go.Scattermapbox(
    name = "Trees",
    mode = "lines",
    lon = lon,
    lat = lat,
    marker = {'size': 10},
    line = dict(width = 4.5, color = 'blue'))) 

lat_center = np.mean(lat)
long_center = np.mean(lon)

PREF = response.json()["nodesShort"]
PREF = PREF[2:-2].split("), (")
lon = []
lat = []
for k in PREF:
    LON = float(k.split(", ")[0])
    LAT = float(k.split(", ")[1])  
    lon.append(LON)
    lat.append(LAT) 

fig.add_trace(go.Scattermapbox(
    name = "Short",
    mode = "lines",
    lon = lon,
    lat = lat,
    marker = {'size': 8},
    line = dict(width = 4.5, color = 'red'))) 

fig.add_trace(go.Scattermapbox(
    name = "Source",
    mode = "markers",
    lon = [DICT["sLon"]],
    lat = [DICT["sLat"]],
    marker = {'size': 12, 'color':"red"}))
    
# adding destination marker
fig.add_trace(go.Scattermapbox(
    name = "Destination",
    mode = "markers",
    lon = [DICT["eLon"]],
    lat = [DICT["eLat"]],
    marker = {'size': 12, 'color':'green'}))


# defining the layout using mapbox_style
fig.update_layout(mapbox_style="stamen-terrain",
    mapbox_center_lat = 30, mapbox_center_lon=-80)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                    mapbox = {
                        'center': {'lat': lat_center, 
                        'lon': long_center},
                        'zoom': 13})
st.write("## Map")
st.write(fig)