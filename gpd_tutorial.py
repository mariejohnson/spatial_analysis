import geopandas
import pandas as pd

# http://geopandas.org/mapping.html

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

cities = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))

world.plot()

