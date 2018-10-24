#pylab inline
import geopandas as gpd
import pandas as pd
import os
import mplleaflet

in_data_dir = '/Users/datateam/Desktop/SASAP/Mining'
out_data_dir = '/Users/datateam/Desktop/SASAP/HabMetricsOut/'

infp = lambda s: os.path.join(in_data_dir, s)
outfp = lambda s: os.path.join(out_data_dir, s)

# Importing shapefiles for mining footprints and regional data.
mines_fp = infp('Mining_Disturbance_All.shp')
mines = gpd.read_file(mines_fp)
regions_fp = infp('/Users/datateam/Desktop/SASAP/HUC8_rebuild/output/sasap_regions.shp')
regions = gpd.read_file(regions_fp)

mines.info()
regions.head()

mines = mines.to_crs(epsg=3338)
regions = regions.to_crs(epsg=3338)

# To count mining footprints for each region, I'll first create an intersection dataframe showing mine polygons as `True` or `False` for intersection with regional geometries.
# change abc back to reg
for reg in regions.region:
    geom = regions.query("region==@reg").geometry.iloc[0] # adding geometry into mines # asking if "for each regions" ==@ means to find a true statment, no reason to query already looping through it # index location 0 is .iloc[0]
    mines[reg] = mines.intersects(geom)

#finding geometry and asking if it intersects mines, it's querying the whole thing (but shouldn't, need to)
#  gives row data as if it's column

for i, s in regions.iterrows(): # i is index and s is series, series is 3 items
    _id, region, geometry = s # unpacking tuple so you can read it
    if any(mines.intersects(geometry)): # if mine intersects geometry, "any trues in the list of falses" is the how the keyword any works
        print(region) # then

ct = 0
for i, s in regions.iterrows():
    _id, region, geometry = s
    if any(mines.intersects(geometry)):
        print(region)
		ct += 1
print('Count of intersecting geometries: {}'.format(ct))
# this count is n_mines

# if geometries intersect it's true
print(mines.columns)
# Now, I can sum up all of those mine polygons that evaluate as `True` for regional intersection. I'll attribute that count to the `region` DataFrame.
for reg in regions.region:
    n_mines = mines[reg].sum()
    regions.loc[regions.region==reg, 'n_mines'] = n_mines


# Let's check out the map. It looks like the Yukon region, the largest region, has the most mines (by far) at 391.
fig, ax = subplots(1,1,figsize=(7,7))
ax = regions.plot(column='n_mines', cmap='Oranges', ax=ax, linewidth=0.4)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')

regions.sort_values(by='n_mines', ascending=False).head(3)

for reg in regions.region:
    mines_reg = mines[mines[reg]]
    avg_m_area = mines_reg.Shape_Area.mean() * 1e-6
    regions.loc[regions.region==reg, 'avg_m_area'] = avg_m_area


regions['avg_m_area'] = regions['avg_m_area'].fillna(0)

fig, ax = subplots(1,1,figsize=(7,7))
ax = regions.plot(column='avg_m_area', cmap='Blues', ax=ax, linewidth=0.4)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')

for reg in regions.region:
    mines_reg = mines[mines[reg]]
    mines_union = mines_reg.unary_union
    regions_union = regions.query("region==@reg").unary_union
    mines_reg_clip = mines_union.intersection(regions_union)
    regions.loc[regions.region==reg, 'area_mines'] = mines_reg_clip.area * 1e-6

regions['density_mines'] = regions.area_mines/(regions.area * 1e-6)

regions.sort_values(by='density_mines', ascending = False).head()

fig, ax = subplots(1,1,figsize=(7,7))
ax = regions.plot(column='density_mines', cmap='Greens', ax=ax, linewidth=0.4)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')

regions.to_file(outfp('Regions_with_Mines.shp'))
regions.drop('geometry', axis='columns').to_csv(outfp('Regions_with_Mines.csv'))

watersheds_fp = "/Users/datateam/Desktop/SASAP/HUC8_rebuild/output/sasap_watersheds_gapfix.shp"
watersheds = gpd.read_file(watersheds_fp).to_crs(epsg=3338)

for wat in watersheds.id_numeric:
    geom = watersheds.query("id_numeric==@wat").geometry.iloc[0]
    mines[wat] = mines.intersects(geom)


# Find the number of mining footprints (impact areas) per watershed.
for wat in watersheds.id_numeric:
    n_mines = mines[wat].sum()
    watersheds.loc[watersheds.id_numeric==wat, 'n_mines'] = n_mines

# Map the data. I'll decrease the line width on region borders a bit so that we can visualize this better.
fig, ax = subplots(1,1,figsize=(7,7))
ax = watersheds.plot(column='n_mines', cmap='Blues', ax=ax, linewidth=0.2)
ax.set_axis_off()
foo = ax.axes.set_aspect('equal')


# Find the mean area of mining footprints intersecting each watershed.
for wat in watersheds.id_numeric:
    mines_wat = mines[mines[wat]]
    avg_m_area = mines_wat.Shape_Area.mean() * 1e-6
    watersheds.loc[watersheds.id_numeric==wat, 'avg_m_area'] = avg_m_area

watersheds.avg_m_area = watersheds.avg_m_area.fillna(0)

# Find the area of mining footprints within watershed boundaires, then find the density = ($\frac{mining\,footprint\,area}{watershed\,area

for wat in watersheds.id_numeric:
    mines_wat = mines[mines[wat]]
    mines_union = mines_wat.unary_union
    watersheds_union = watersheds.query("id_numeric==@wat").unary_union
    mines_reg_clip = mines_union.intersection(watersheds_union)
    watersheds.loc[watersheds.id_numeric==wat, 'area_mines'] = mines_reg_clip.area * 1e-6

watersheds['density_mines'] = watersheds.area_mines/(watersheds.area * 1e-6)

# Finally, I'll export the results to shapefile and csv formats.

watersheds.to_file(outfp('Watersheds_with_Mines.shp'))
watersheds.drop('geometry', axis='columns').to_csv(outfp('Watersheds_with_Mines.csv'))