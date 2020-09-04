import pytest
from malstroem import io

# raster
dtmfile = 'tests/data/dtm.tif'
filledfile = 'tests/data/filled.tif'
depthsfile = 'tests/data/depths.tif'
fillednoflatsfile = 'tests/data/filled_no_flats.tif'
flowdirnoflatsfile = 'tests/data/flowdir_noflats.tif'
labeledfile = 'tests/data/labelled.tif'
wshedsfile = 'tests/data/wsheds.tif'
precipraster_float_file = 'tests/data/precip_raster_float.tif'
precipraster_byte_file = 'tests/data/precip_raster_byte.tif'

# vector
pourpointsfile = 'tests/data/pourpoints.json'
nodesfile = 'tests/data/nodes.json'
streamsfile = 'tests/data/streams.json'
hypsfile = 'tests/data/hyps.csv'
initvolsfile = 'tests/data/initvolumes.geojson'
finalvolsfile = 'tests/data/finalvolumes.geojson'


def readraster(filepath):
    from osgeo import gdal
    ds = gdal.Open(filepath)
    bnd = ds.GetRasterBand(1)
    return bnd.ReadAsArray()


@pytest.fixture
def dtmdata():
    return readraster(dtmfile)


@pytest.fixture
def filleddata():
    return readraster(filledfile)


@pytest.fixture
def depthsdata():
    return readraster(depthsfile)


@pytest.fixture
def fillednoflatsdata():
    return readraster(fillednoflatsfile)


@pytest.fixture
def flowdirdata():
    return readraster(flowdirnoflatsfile)


@pytest.fixture
def bspotdata():
    return readraster(labeledfile)


@pytest.fixture
def wshedsdatadata():
    return readraster(wshedsfile)


@pytest.fixture
def pourpointsdata():
    reader = io.VectorReader(pourpointsfile)
    return reader.read_geojson_features()

@pytest.fixture
def nodesreader():
    return io.VectorReader(nodesfile)

@pytest.fixture
def nodesdata(nodesreader):
    return nodesreader.read_geojson_features()
