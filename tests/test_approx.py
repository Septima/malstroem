from osgeo import ogr
from malstroem.io import VectorReader, VectorWriter
from malstroem.approx import approx_water_level_io
from data.fixtures import hypsfile, finalvolsfile


def test_approx_water_level_io(tmp_path):
    hyps_reader = VectorReader(hypsfile)
    finalvols_reader = VectorReader(finalvolsfile)
    levelsfile = tmp_path / "finallevels.geojson"
    levels_writer = VectorWriter("geojson", str(levelsfile), "finallevels", None, ogr.wkbNone, hyps_reader.crs)
    approx_water_level_io(finalvols_reader, hyps_reader, levels_writer)

    assert levelsfile.is_file()