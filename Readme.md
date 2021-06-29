# MyWay in Paris

App running at [https://mparismap.herokuapp.com/](https://mparismap.herokuapp.com/) . 

## Content

* [Streamlit app folder](./app/)
* [00.PreparingData.ipynb](00.PreparingData.ipynb) (pre processing from opendatasets)
* [01.Stats.ipynb](01.Stats.ipynb): initial insights (to be completed)
* [02.PreparingRouteFinder.ipynb](02.PreparingRouteFinder.ipynb): draft router finder

## Done

* Zoning on arrondissements 18, 19, 20, 10, 11
* Been getting all routes from within OSM
* Preliminary mapping of best route based on trees
* Trees and lighting are put in
* Add shadows

## Todo

* Use distance to fountains, parcs, green spaces
  * What other layers to use?
* Develop something from building footprint (in data/BoI_simple.pkl)

# Images


* Example of the network

![](images/00.PreppingData_parc.png)

* Merging all buildings in one

![](images/dissolving.png)

* Details of streets

![](images/streets.png)
