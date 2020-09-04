from osgeo import ogr
from malstroem.io import VectorReader, VectorWriter, RasterReader, RasterWriter
from malstroem.approx import approx_water_level_io, approx_bluespots_io
from data.fixtures import hypsfile, finalvolsfile, dtmfile, labeledfile, finallevelsfile


def test_approx_water_level_io(tmp_path):
    hyps_reader = VectorReader(hypsfile)
    finalvols_reader = VectorReader(finalvolsfile)
    levelsfile = tmp_path / "finallevels.geojson"
    levels_writer = VectorWriter("geojson", str(levelsfile), "finallevels", None, ogr.wkbNone, hyps_reader.crs)
    approx_water_level_io(finalvols_reader, hyps_reader, levels_writer)

    assert levelsfile.is_file()

def test_approx_bluespots_io(tmp_path):
    bspot_reader = RasterReader(labeledfile)
    dem_reader = RasterReader(dtmfile, nodatasubst=-999)
    levels_reader = VectorReader(finallevelsfile)

    final_depths_file = tmp_path / "final_depths.tif"
    final_bluespots_file = tmp_path / "final_bluespots.tif"

    depths_writer = RasterWriter(str(final_depths_file), bspot_reader.transform, bspot_reader.crs)
    final_bs_writer = RasterWriter(str(final_bluespots_file), bspot_reader.transform, bspot_reader.crs, nodata=0)

    approx_bluespots_io(bspot_reader, levels_reader, dem_reader, depths_writer, final_bs_writer)

    assert final_depths_file.is_file()
    assert final_bluespots_file.is_file()