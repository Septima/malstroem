import pytest
import numpy as np
from malstroem import io
from osgeo import osr, ogr
from pathlib import Path

def create_utm32_crs():
    crs = osr.SpatialReference()
    crs.ImportFromEPSG(25832)
    return crs.ExportToWkt()

def create_fields():
    fields = []
    fields.append(ogr.FieldDefn('field1', ogr.OFTInteger))
    fields.append(ogr.FieldDefn('field2', ogr.OFTReal))
    return fields

def create_geojson():
    features = []
    for i in range(5):
        f = dict(id=i, type="Feature")
        f['properties'] = dict(field1=i, field2=i*2.5)
        f['geometry'] = dict(type='Point', coordinates=[i*1.0, i*2.0])
        features.append(f)
    return dict(type="FeatureCollection", features=features)

def get_datasource_layer(datasource, layername):
    ds = ogr.Open(datasource)
    lyr = ds.GetLayerByName(layername) if layername else ds.GetLayerByIndex(0)
    return ds, lyr

def test_write_vector(tmpdir):
    crs = create_utm32_crs()
    fields = create_fields()
    features = create_geojson()
    layername = 'xxx'

    outfile = str(tmpdir.join('test.geojson'))

    writer = io.VectorWriter('geojson', outfile, layername, fields, ogr.wkbPoint, crs)
    writer.write_geojson_features(features)
    del writer

    ds, lyr = get_datasource_layer(outfile, None)
    fdefn = lyr.GetLayerDefn()
    assert lyr is not None
    assert lyr.GetGeomType() == ogr.wkbPoint
    assert lyr.GetSpatialRef().ExportToWkt() == crs
    assert lyr.GetFeatureCount() == len(features['features'])

    # Feature defn
    assert fdefn.GetFieldCount() == 2
    assert len(fields) == 2

    # Field 0
    for ix, f_exp in enumerate(fields):
        f = fdefn.GetFieldDefn(ix)
        assert f.GetName() == f_exp.GetName()


def test_write_raster_datatypes(tmpdir):
    data_types = ["float64", "float32", "int32", "uint32", "uint8", "int64", "uint16", "int16"]
    shape = (25, 30)
    data = np.arange(shape[0] * shape[1]).reshape(shape)
    gt = (510000, 0.2, 0, 6150000, 0, -0.2)
    tmppath = Path(tmpdir)

    for dt in data_types:
        filepath = tmppath / f"{dt}.tif"
        cast_data = data.astype(dt)
        writer = io.RasterWriter(str(filepath), gt, "", nodata=None)
        writer.write(cast_data)
        assert filepath.exists(), f"File was not written"
        reader = io.RasterReader(str(filepath))
        read_data = reader.read()
        np.testing.assert_array_equal(read_data, cast_data)

