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

def combine_results(gdf, base_dir):
    """
    Combine the results of the model runs in the directories specified in the list dirs.
    """

    gdf_streams = gpd.GeoDataFrame()
    gdf_bluespots = gpd.GeoDataFrame()

    crs = gdf.crs

    for index, row in gdf.iterrows():
        results_dir = f"{base_dir}/merged_{row['vassdragsnummer']}"
        polygon = row['geometry']
        if not os.path.exists(results_dir):
            print(f"Directory {results_dir} does not exist.")
            continue
        print("Processing: ", row["vassdragsnummer"])

        gdf_streams_dir = gpd.read_file(f"{results_dir}/malstroem.gpkg", layer='streams').to_crs(crs)
        gdf_bluespots_dir = gpd.read_file(f"{results_dir}/malstroem.gpkg", layer='finalbluespots').to_crs(crs)

        gdf_streams_dir = gdf_streams_dir.clip(polygon)
        gdf_bluespots_dir = gdf_bluespots_dir.clip(polygon)

        gdf_streams_dir['vassdragsnummer'] = row['vassdragsnummer']
        gdf_bluespots_dir['vassdragsnummer'] = row['vassdragsnummer']

        gdf_streams = gpd.GeoDataFrame(pd.concat([gdf_streams, gdf_streams_dir], ignore_index=True), crs=crs)
        gdf_bluespots = gpd.GeoDataFrame(pd.concat([gdf_bluespots, gdf_bluespots_dir], ignore_index=True), crs=crs)
    
    return gdf_streams, gdf_bluespots





