import folium
import geopandas as gpd
import os

## config
STOPS_URL = (
    "zip+https://ge.ch/sitg/geodata/SITG/OPENDATA/TPG_ARRETS-GDB.zip!TPG_ARRETS.gdb"
)
MUNICIPALITIES_URL = (
    "zip+https://ge.ch/sitg/geodata/SITG/OPENDATA/CAD_COMMUNE-GDB.zip!CAD_COMMUNE.gdb"
)

# Step 1: load public transport stops dataset
print("Loading public transport stops...")
stops_gdf = gpd.read_file(STOPS_URL)
stops_gdf.drop_duplicates(subset=["geometry"], inplace=True)

# Step 2: load municipalities dataset
print("Loading municipalities...")
municipalities_gdf = gpd.read_file(MUNICIPALITIES_URL)

# Step 3: select municipalities
print("Selecting municipalities...")
selected_municipalities_gdf = municipalities_gdf[
    municipalities_gdf["COMMUNE"].isin(["Bernex", "Meyrin"])
].copy()

# Step 4: perform spatial join in order to find stops within the selected municipalities (Bernex and Meyrin)
print("Filtering stops within selected municipalities...")
filtered_stops_gdf = stops_gdf.sjoin(
    selected_municipalities_gdf, how="inner", predicate="intersects"
)[stops_gdf.columns]

# Step 5: Create a map of Geneva and add municipal boundaries
print("Generating map...")
geneva_map = folium.Map(location=[46.25, 6.1432], zoom_start=11, tiles=None)

## Step 5.1: Add orthophoto as basemap
folium.WmsTileLayer(
    url="https://raster.sitg.ge.ch/arcgis/services/ORTHOPHOTOS_2023_EPSG3857/MapServer/WMSServer",
    name="ORTHOPHOTOS_2023",
    fmt="image/png",
    layers="0",
    attr="<a href='https://sitg.ge.ch/'>SITG</a>",
).add_to(geneva_map)

## Step 5.2: Add municipalities borders in red
folium.GeoJson(
    municipalities_gdf.geometry, style_function=lambda x: {"color": "red", "weight": 2}
).add_to(geneva_map)

## Step 5.3: Add stop names to the map
for _, row in filtered_stops_gdf.to_crs(epsg=4326).iterrows():
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=row["NOM_ARRET"],  # Stop name
    ).add_to(geneva_map)

# Step 6: Save the map to an HTML file
print("Saving map to file...")
os.makedirs("output", exist_ok=True)
geneva_map.save("output/index.html")
print(
    "\nDone! A web map has been saved to `output/index.html`. Please check it out ;-)"
)
