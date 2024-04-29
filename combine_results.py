import geopandas as gpd
import pandas as pd
import os
from dtm_perturbations_create import repair_linestring_gpkg


def repair_geometries(base_dir):
    """
    Repair geometries in the shapefiles in the directories specified in the list dirs.
    """

    for subdir, dirs, files in os.walk(base_dir):
        for file in files:
            if file=='malstroem.gpkg':
                input_file = os.path.join(subdir, file)
                streams_output_file=f"{base_dir}/{os.path.basename(subdir)}.gpkg".replace('merged', 'streams')
                print(f"Repairing {input_file} to {streams_output_file}")
                repair_linestring_gpkg(input_file, 'streams', streams_output_file)

def extract_bluespots(base_dir):
    for subdir, dirs, files in os.walk(base_dir):
        for file in files:
            if file=='malstroem.gpkg':
                input_file = os.path.join(subdir, file)
                bluespots_output_file=f"{base_dir}/{os.path.basename(subdir)}.gpkg".replace('merged', 'bluespots')
                print(f"Copying bluespots from {input_file} to {bluespots_output_file}")
                gdf = gpd.read_file(input_file, layer='finalbluespots')
                gdf.to_file(bluespots_output_file, driver='GPKG')

def combine_results(gdf, results_dir):
    """
    Combine the results of the model runs in the directories specified in the list dirs.
    """

    if not os.path.exists(results_dir):
        print(f"Directory {results_dir} does not exist.")
        return None
    
    gdf_streams = gpd.GeoDataFrame()
    gdf_bluespots = gpd.GeoDataFrame()

    crs = gdf.crs

    for index, row in gdf.iterrows():
        streams_file = f"{results_dir}/streams_{row['vassdragsnummer']}.gpkg"
        bluespots_file = f"{results_dir}/bluespots_{row['vassdragsnummer']}.gpkg"  

        polygon = row['geometry']
        print("Processing: ", row["vassdragsnummer"])

        gdf_streams_dir = gpd.read_file(streams_file).to_crs(crs)
        gdf_bluespots_dir = gpd.read_file(bluespots_file).to_crs(crs)

        gdf_streams_dir = gdf_streams_dir.clip(polygon)
        gdf_bluespots_dir = gdf_bluespots_dir.clip(polygon)

        gdf_streams_dir['vassdragsnummer'] = row['vassdragsnummer']
        gdf_bluespots_dir['vassdragsnummer'] = row['vassdragsnummer']

        gdf_streams = gpd.GeoDataFrame(pd.concat([gdf_streams, gdf_streams_dir], ignore_index=True), crs=crs)
        gdf_bluespots = gpd.GeoDataFrame(pd.concat([gdf_bluespots, gdf_bluespots_dir], ignore_index=True), crs=crs)
    
    return gdf_streams, gdf_bluespots





