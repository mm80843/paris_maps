import pypama as myway
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

@st.cache(hash_funcs={pd.core.frame.DataFrame: id},\
    allow_output_mutation=True,suppress_st_warning=True)
def cacheData():
    m4p = myway.parisMap()
    m4p.debug = True    
    st.write("Cached!")
    return m4p

m4p = cacheData()

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

geolocator = Nominatim(user_agent="pypama")
location = geolocator.geocode(START)
m4p.HOME = location.longitude, location.latitude
location = geolocator.geocode(END)
m4p.WORK = location.longitude, location.latitude

start, end = m4p.findClosest(m4p.HOME,m4p.WORK)

st.sidebar.write("Calculating paths..")
m4p.calculatePath(pTrees,pLights,pGreenSpace,pFreshplace)
st.sidebar.write("Calculating done!")


st.sidebar.write("Preparing the graph.")
fig = myway.plot_path(m4p.graph, m4p.HOME, m4p.WORK, m4p.routeTrees, m4p.routeShort, m4p.trees, m4p.lights, m4p.vT)

st.write(fig)