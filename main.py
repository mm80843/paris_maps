from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from geopy.geocoders import Nominatim

import warnings
warnings.filterwarnings("ignore")

import pypama as myway


app = FastAPI()

def cacheData():
    m4p = myway.parisMap()
    m4p.debug = True
    print("Executing the cache")
    return m4p

@app.on_event("startup")
async def startup_event():
    m4p = cacheData()
    return m4p

m4p = cacheData()

class PathFinder(BaseModel):
    id:str             = "Luc"
    sLat:float         = 48.8873525
    sLon:float         = 2.3559566
    eLat:float         = 48.8656642
    eLon:float         = 2.3731774
    pLights:float      = 2.0
    pTrees:float       = 2.0
    pGreenSpace:float  = 2.0
    pFreshplace:float  = 2.0

class FoundPath(BaseModel):
    nodesPrefs :str = ""
    nodesShort :str = ""


@app.get("/")
def home():
    return {"WhoamI": "MyWay testing API"}

@app.post('/find_path')
async def find_path(path: PathFinder):
    #m4p = startup_event()
    m4p.HOME = path.sLon, path.sLat 
    m4p.WORK = path.eLon, path.eLat
    start, end = m4p.findClosest(m4p.HOME,m4p.WORK)
    
    m4p.calculatePath(path.pTrees,path.pLights, \
        path.pGreenSpace,path.pFreshplace)
        
    if m4p.debug:
        print(m4p.routeTrees)
        print(m4p.routeShort)
    
    NODES = []
    for i in m4p.routeTrees:
        point = m4p.graph.nodes[i]
        NODES.append((int(point['x']*1E7)/1E7,int(point['y']*1E7)/1E7 ))
    print(str(NODES))

    SHORT = []
    for i in m4p.routeShort:
        point = m4p.graph.nodes[i]
        SHORT.append((int(point['x']*1E7)/1E7,int(point['y']*1E7)/1E7 ))
    print(str(SHORT))

    found = FoundPath(nodesPrefs=str(NODES), nodesShort=str(SHORT) )
    
    return found
