
# coding: utf-8

# In[1]:


# get_ipython().magic(u'pylab inline')
import geopandas as gpd
import pandas as pd
import os
import mplleaflet


mines_fp = 'Mining/Mining_Disturbance_All.shp'
mines = gpd.read_file(mines_fp)
regions_fp = 'HUC8_rebuild/output/sasap_regions.shp'
regions = gpd.read_file(regions_fp)


# # Regions

# Importing shapefiles for mining footprints and regional data.

# In[5]:



# # Mining
# 
# I want to attribute regions and watersheds with data on mining footprints, defined as areas of disturbed land and impacts from mining activities.
# 
# I'll subset regions and watersheds by the following data:
# * Number of mining footprints (mining impact areas) intersecting each region or watershed.
# * Average area of those mining footprints.
# * Area (km<sup>2</sup>) impacted by mining within regional and watershed boundaries (area clipped to regional or watershed boundaries).
# * Density of mining areas defined as ($\frac{mining\,footprint\,area}{regional\,or\,watershed\,area}$).

# Checking out the mining data. It looks like there are 646 digitized mining footprints.

# In[27]:


mines.info()


# And checking out the region data. Regions are identified by the `region` attribute, so that'll be our key.

# In[4]:


regions.head()


# Before running any analysis, I'll make sure both `regions` and `mines` data are in the Alaska Albers projection ([epsg:3338](http://spatialreference.org/ref/epsg/3338/)).

# In[5]:


mines = mines.to_crs(epsg=3338)
regions = regions.to_crs(epsg=3338)


# # Count of Mining Footprints

# To count mining footprints for each region, I'll first create an intersection dataframe showing mine polygons as `True` or `False` for intersection with regional geometries.

# In[6]:


for reg in regions.region:
    geom = regions.query("region==@reg").geometry.iloc[0] # you can't select any position but 0 in this case, it's possible this could be where there are different geometries
    mines[reg] = mines.intersects(geom) # so you take the reg (for example Yukon), with its geometry object and see where any geometry object from the geom variable intersects with anything in the mines geodataframe



# Now, I can sum up all of those mine polygons that evaluate as `True` for regional intersection. I'll attribute that count to the `region` DataFrame.

# In[7]:


for reg in regions.region:
    n_mines = mines[reg].sum()
    regions.loc[regions.region==reg, 'n_mines'] = n_mines

x=1
# Let's check out the map. It looks like the Yukon region, the largest region, has the most mines (by far) at 391.

# In[8]:


fig, ax = subplots(1,1,figsize=(7,7))
ax = regions.plot(column='n_mines', cmap='Oranges', ax=ax, linewidth=0.4)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')


# In[9]:


regions.sort_values(by='n_mines', ascending=False).head(3)


# # Average Area of Mining Footprints

# I'll look at the `Shape_Area` attribute of those mining footprints we counted above to find the average area of footprints intersecting each region. Since I'm interested in the characteristics of the mining footprints, I won't clip mining area to regional boundaries.

# In[10]:


for reg in regions.region:
    mines_reg = mines[mines[reg]]
    avg_m_area = mines_reg.Shape_Area.mean() * 1e-6
    regions.loc[regions.region==reg, 'avg_m_area'] = avg_m_area


# Converting `NaN` values to 0 for those regions without any intersecting mines.

# In[11]:


regions['avg_m_area'] = regions['avg_m_area'].fillna(0)


# In[12]:


fig, ax = subplots(1,1,figsize=(7,7))
ax = regions.plot(column='avg_m_area', cmap='Blues', ax=ax, linewidth=0.4)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')


# # Area per Region and Density of Mining Footprints

# Now, I'm interested in mining data specific to each region:
# * Area of each region covered by mining footprints and 
# * Density, defined as ($\frac{mining\,footprint\,area}{regional\,area}$).
# 
# For these analyses, I'll have to union mining polygons and clip the resulting shape to regional boundaries. From there, I can evaluate the area of each region covered by mining activity.

# In[13]:


for reg in regions.region:
    mines_reg = mines[mines[reg]]
    mines_union = mines_reg.unary_union
    regions_union = regions.query("region==@reg").unary_union
    mines_reg_clip = mines_union.intersection(regions_union)
    regions.loc[regions.region==reg, 'area_mines'] = mines_reg_clip.area * 1e-6


# Now, it's one more quick step to find density using the `area_mines` attribute from the previous analysis.

# In[14]:


regions['density_mines'] = regions.area_mines/(regions.area * 1e-6)


# In[15]:


regions.sort_values(by='density_mines', ascending = False).head()


# Let's map this out. It looks like even though the Yukon region is very large, it also has the highest density of mining impact areas.

# In[16]:


fig, ax = subplots(1,1,figsize=(7,7))
ax = regions.plot(column='density_mines', cmap='Greens', ax=ax, linewidth=0.4)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')


# Export the results to shapefile and csv formats. I need to drop the "geometry" field in order to export to csv.

# In[17]:


regions.to_file(outfp('Regions_with_Mines.shp'))
regions.drop('geometry', axis='columns').to_csv(outfp('Regions_with_Mines.csv'))


# # Watersheds

# I'm going to run the same analysis as above, but for watersheds. To reiterate, these attributes are:
# * Number of mining footprints (mining impact areas) intersecting each watershed.
# * Average area of those mining footprints.
# * Area (km<sup>2</sup>) impacted by mining within watershed boundaries (area clipped to regional or watershed boundaries).
# * Density of mining areas defined as ($\frac{mining\,footprint\,area}{watershed\,area}$).

# First, I'll import the watersheds shapefile and convert to the Alaska Albers projection.

# In[18]:


watersheds_fp = "/home/shares/scientist/sasap-biophys/HUC8_rebuild/output/sasap_watersheds_gapfix.shp"
watersheds = gpd.read_file(watersheds_fp).to_crs(epsg=3338)


# Create the intersection DataFrame.

# In[19]:


for wat in watersheds.id_numeric:
    geom = watersheds.query("id_numeric==@wat").geometry.iloc[0]
    mines[wat] = mines.intersects(geom)


# Find the number of mining footprints (impact areas) per watershed.

# In[20]:


for wat in watersheds.id_numeric:
    n_mines = mines[wat].sum()
    watersheds.loc[watersheds.id_numeric==wat, 'n_mines'] = n_mines


# Map the data. I'll decrease the line width on region borders a bit so that we can visualize this better.

# In[21]:


fig, ax = subplots(1,1,figsize=(7,7))
ax = watersheds.plot(column='n_mines', cmap='Blues', ax=ax, linewidth=0.2)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')


# Find the mean area of mining footprints intersecting each watershed.

# In[22]:


for wat in watersheds.id_numeric:
    mines_wat = mines[mines[wat]]
    avg_m_area = mines_wat.Shape_Area.mean() * 1e-6
    watersheds.loc[watersheds.id_numeric==wat, 'avg_m_area'] = avg_m_area


# In[23]:


watersheds.avg_m_area = watersheds.avg_m_area.fillna(0)


# Find the area of mining footprints within watershed boundaires, then find the density = ($\frac{mining\,footprint\,area}{watershed\,area}$).

# In[24]:


for wat in watersheds.id_numeric:
    mines_wat = mines[mines[wat]]
    mines_union = mines_wat.unary_union
    watersheds_union = watersheds.query("id_numeric==@wat").unary_union
    mines_reg_clip = mines_union.intersection(watersheds_union)
    watersheds.loc[watersheds.id_numeric==wat, 'area_mines'] = mines_reg_clip.area * 1e-6


# In[25]:


watersheds['density_mines'] = watersheds.area_mines/(watersheds.area * 1e-6)


# Finally, I'll export the results to shapefile and csv formats.

# In[26]:


watersheds.to_file(outfp('Watersheds_with_Mines.shp'))
watersheds.drop('geometry', axis='columns').to_csv(outfp('Watersheds_with_Mines.csv'))

