import rasterio
import os
import numpy as np
from tqdm import tqdm
n=50
objectid = '009.11'
raster_file = f'merged_{objectid}.tif'
raster_dir = f'data/malstroem-50/merged_{objectid}'
raster_path = f"{raster_dir}/{raster_file}" 
perturbed_dir = f"{raster_dir}/perturbed" 
os.makedirs(perturbed_dir, exist_ok=True)

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


