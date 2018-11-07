#pylab inline
import geopandas as gpd
import pandas as pd
import os
# import mplleaflet
import numpy as np


# out_data_dir = '/Users/datateam/Desktop/SASAP/HabMetricsOut/'
#
# infp = lambda s: os.path.join(in_data_dir, s)
# outfp = lambda s: os.path.join(out_data_dir, s)

# Importing shapefiles for mining footprints and regional data.
mines_fp = 'Mining/Mining_Disturbance_All.shp'
mines = gpd.read_file(mines_fp)
regions_fp = 'HUC8_rebuild/output/sasap_regions.shp'
regions = gpd.read_file(regions_fp)


# mines.head()
# regions.head()

mines = mines.to_crs(epsg=3338)
regions = regions.to_crs(epsg=3338)

m_intersect = {} # dict
# mines['m_intersect'] = m_intersect
for i, r in regions.iterrows():
    _id, region, r_geo = r # unpack r it has 3 elements, this could actually be just r[-1] because we only need the last element (actually we need region so it's better to leave it that way)
    for j, m in mines.iterrows():
        m_geo = m[-1] # the last element ... iterow returns tuple with index location and series (row in this case that is actually a column with a sum?)
        # m[-1] returns the last value (or last element) works on list or series - in this case it could also just be m['geometry']
        if r_geo.intersects(m_geo): # double for loop everything is regions and mines will be compared (I think just the geometries though)
            if region not in m_intersect.keys(): # what is keys?, so .keys() is just calling the keys (dicts have keys and values) d = {'marie': 31, 'david': 34}, marie and david are keys
                # Kind of confused because it would appear that m_intersect is empty and wouldn't have keys yet
                m_intersect[region] = [m_geo] # m_intersect is an empty dict before thi, so it r_geo and m_geo
            else:
                m_intersect[region].append(m_geo)



# m_intersect gives a dict with each region as keys with output geometry