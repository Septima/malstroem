import numpy as np

from malstroem import bluespots, io
from malstroem.algorithms import label
from osgeo import ogr
import os
from data.fixtures import flowdirnoflatsfile, dtmfile, filledfile, bspotdata, depthsdata

class NumpyRasterReader(object):
    def __init__(self, data, transform):
        self.data = data
        self.transform = transform

    def read(self):
        return self.data


def test_bluespots(tmpdir):
    flowdir_reader = io.RasterReader(flowdirnoflatsfile)
    dem_reader = io.RasterReader(dtmfile)
    filled_reader = io.RasterReader(filledfile)
    depths_reader = NumpyRasterReader(filled_reader.read() - dem_reader.read(), dem_reader.transform)
    outdbfile = str(tmpdir.join('test.gpkg'))

    # At least 5cm deep, 5 cells wide and at least one cell-meter volume
    filter_function = lambda r: r['max'] > 0.05 and r['count'] > 5 and r['sum'] > 1

    pourpoint_writer = io.VectorWriter('gpkg', outdbfile, 'pourpoints', None, ogr.wkbPoint, dem_reader.crs)
    watershed_writer = io.RasterWriter(str(tmpdir.join('watersheds.tif')), dem_reader.transform, dem_reader.crs, 0)

    watershed_vector_writer = io.VectorWriter('gpkg', outdbfile, 'watersheds', None, ogr.wkbPolygon, dem_reader.crs)

    labeled_writer = io.RasterWriter(str(tmpdir.join('labeled.tif')), dem_reader.transform, dem_reader.crs, 0)

    labeled_vector_writer = io.VectorWriter('gpkg', outdbfile, 'bluespots', None, ogr.wkbPolygon, dem_reader.crs)

    bluespot_tool = bluespots.BluespotTool(
        input_depths=depths_reader,
        input_flowdir=flowdir_reader,
        input_bluespot_filter_function=filter_function,
        input_accum=None,
        input_dem=dem_reader,
        output_labeled_raster=labeled_writer,
        output_labeled_vector=labeled_vector_writer,
        output_pourpoints=pourpoint_writer,
        output_watersheds_raster=watershed_writer,
        output_watersheds_vector=watershed_vector_writer
    )
    bluespot_tool.process()

    assert os.path.isfile(outdbfile)
    assert os.path.isfile(watershed_writer.filepath)
    assert os.path.isfile(labeled_writer.filepath)


def test_filter(bspotdata, depthsdata):
    raw_bluespot_stats = label.label_stats(depthsdata, bspotdata)
    filter_function = lambda r: r['max'] > 2 and r['count'] > 5 and r['sum'] > 1
    keepers = bluespots.filterbluespots(filter_function, 1.0, raw_bluespot_stats)
    assert len(keepers) == len(raw_bluespot_stats)
    assert sum(keepers) == 19


def test_nofilter(bspotdata, depthsdata):
    raw_bluespot_stats = label.label_stats(depthsdata, bspotdata)
    filter_function = lambda r: True
    keepers = bluespots.filterbluespots(filter_function, 1.0, raw_bluespot_stats)
    assert len(keepers) == len(raw_bluespot_stats)
    assert sum(keepers) == len(raw_bluespot_stats)