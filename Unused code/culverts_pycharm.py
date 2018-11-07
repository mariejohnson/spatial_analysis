#pylab inline
import geopandas as gpd
import pandas as pd
import os
import mplleaflet

fish_pass = 'ADFG/ADFG_fish_passage.shp'
fp = gpd.read_file(fish_pass)
regs = 'HUC8_rebuild/output/sasap_regions.shp'
regions = gpd.read_file(regs)

mines_fp = 'Mining/Mining_Disturbance_All.shp'
mines = gpd.read_file(mines_fp)


fp = fp.to_crs(epsg=3338)
mines = mines.to_crs(epsg=3338)
regions = regions.to_crs(epsg=3338)

# To count mining footprints for each region, I'll first create an intersection dataframe showing mine polygons as `True` or `False` for intersection with regional geometries.
# change abc back to reg
for reg in regions.region:
    geom = regions.query("region==@reg").geometry.iloc[0]
    mines[reg] = mines.intersects(geom)

x = 1
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