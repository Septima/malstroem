import fiona
from shapely.geometry import shape, LineString  

def repair_linestring_gpkg(input_file, layer, output_file):

    with fiona.open(input_file, layer=layer) as src:
        meta = src.meta
        with fiona.open(output_file, 'w', **meta) as sink:
            for feature in src:
                try:
                    geom = shape(feature['geometry'])
                    # Check and process LineString geometries
                    if isinstance(geom, LineString):
                        if len(geom.coords) < 2:
                            # Skip or handle single-point linestrings
                            continue  # This line skips them; you might want to add a placeholder or handle differently
                    # Write the feature to the new file if it's valid
                    sink.write(feature)
                except Exception as e:
                    print(f"Error processing feature {feature['id']}: {e}")