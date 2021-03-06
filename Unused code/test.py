#pylab inline
import geopandas as gpd
import pandas as pd
import os
import mplleaflet
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


mines.head()
# regions.head()

mines = mines.to_crs(epsg=3338)
regions = regions.to_crs(epsg=3338)

m_intersect = {} # dict
# print(m_intersect.keys())
# mines['m_intersect'] = m_intersect

# iterow returns tuple with index location and series
for i, r in regions.iterrows(): # i = row, r = column
    _id, region, r_geo = r # unpack r it has 3 elements, this could actually be just r[-1] because we only need the last element (actually we need region so it's better to leave it that way)
    for j, m in mines.iterrows(): # j = row (number of rows in each column but I think there should be 646?), m = column (column names and data)
        m_geo = m['geometry'] # the last element ... iterow returns tuple with index location and series (row in this case that is actually a column with a sum?)
        # changing it to m['geometry'] gives the same result (and is less confusing)
        # m_geo = polygon
        # m[-1] returns the last value (or last element) works on list or series - in this case it could also just be m['geometry']
        # I'm not sure how m_geo returns the last element because it's giving a list of polygons
        if r_geo.intersects(m_geo): # my understanding here is that the two if statements are like saying "if this, and, if this"
            # double for loop everything is regions and mines will be compared (I think just the geometries though)
            if region not in m_intersect.keys(): # .keys() is just calling the keys (dicts have keys and values) d = {'marie': 31, 'david': 34}, marie and david are keys
                # Still empty at above line
                # I guess we must be adding keys as we loop
                m_intersect[region] = [m_geo]
                # at this point m_intersect is getting filled
                # just gives Aleutian islands, which makes sense because they don't have mines in them "is not in"
                # length is one, not sure this makes sense
            else:
                m_intersect[region].append(m_geo)
                # so this must be all those that are true but I can't tell where this is getting added to? Let's see if m_intersect changes. S
                # till includes Aleutian islands, 2 mines but that makes sense because I think
                print m_intersect[region].sum()


x = 1