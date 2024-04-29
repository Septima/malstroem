import rasterio
import os
import numpy as np
from tqdm import tqdm
import fiona 
from shapely.geometry import shape, LineString, mapping
from utils import repair_linestring_gpkg


n=50
objectid = '009.11'
root_dir = 'data/malstroem-50'
raster_file = f'merged_{objectid}.tif'
raster_dir = f'{root_dir}/merged_{objectid}'
raster_path = f"{raster_dir}/{raster_file}" 
perturbed_dir = f"{raster_dir}/perturbed" 
os.makedirs(perturbed_dir, exist_ok=True)


def perturb_raster(raster_path, perturbed_dir, n):
    with rasterio.open(raster_path) as src:
        data0 = src.read(1)  # read the first band
        meta = src.meta

    np.random.seed(42)

    for i in tqdm(range(n),total=n):
        data=data0.copy()
        mask = data != -32767
        perturbation = np.random.uniform(-0.5, 0.5, data.shape)
        data[mask] += perturbation[mask]
        file_path = f"{perturbed_dir}/{raster_file[:-4]}_{i+1}.tif"
        meta['dtype'] = 'float32'  # update if your perturbed data changes the data type
        with rasterio.open(file_path, 'w', **meta) as dst:
            dst.write(data, 1)



if __name__=='__main__':
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file=='malstroem.gpkg':
                input_file = os.path.join(subdir, file)
                output_file=f"{root_dir}/{os.path.basename(subdir)}.gpkg".replace('merged', 'malstroem')
                print(f"Repairing {input_file} to {output_file}")
                repair_linestring_gpkg(input_file, 'streams', output_file)

