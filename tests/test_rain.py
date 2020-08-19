from data.fixtures import nodesreader, precipraster_float_file, precipraster_byte_file, labeledfile
from malstroem.rain import SimpleVolumeTool, RasterVolumeTool, Unit
from malstroem.io import VectorWriter, RasterReader
from osgeo import osr, ogr
import json
import pytest
import numpy as np


def create_utm32_crs():
    crs = osr.SpatialReference()
    crs.ImportFromEPSG(25832)
    return crs.ExportToWkt()

def test_evenly_distributed(nodesreader, tmp_path):
    volumes_file_path = tmp_path / "volumes.geojson"
    crs = create_utm32_crs()
    volumes_writer = VectorWriter("geojson", str(volumes_file_path), "", None, ogr.wkbPoint, crs)
    attr = "inputvol"

    tool = SimpleVolumeTool(nodesreader, volumes_writer, attr, 10)
    tool.process()

    assert volumes_file_path.is_file(), "No file written"
    with open(volumes_file_path) as f:
        parsed = json.load(f)
    assert all([ x["properties"][attr] > 0 for x in parsed["features"] if x["properties"]["nodetype"] == "pourpoint"]), "One or more pourpoints having 0m3 rain volume"
    assert sum([x["properties"][attr] for x in parsed["features"]]) > 0, "Volumes sum to 0"
    
@pytest.mark.parametrize("precipfile", [precipraster_byte_file, precipraster_float_file])
def test_rasterdefined(nodesreader, tmp_path, precipfile):
    volumes_file_path = tmp_path / "volumes.geojson"
    crs = create_utm32_crs()
    volumes_writer = VectorWriter("geojson", str(volumes_file_path), "", None, ogr.wkbPoint, crs)
    attr = "inputvol"

    bspotlabels_reader = RasterReader(labeledfile)
    precip_reader = RasterReader(precipfile)

    unit = Unit.mm
    tool = RasterVolumeTool(nodesreader, bspotlabels_reader, precip_reader, unit, volumes_writer, attr)
    tool.process()

    assert volumes_file_path.is_file(), "No file written"
    with open(volumes_file_path) as f:
        parsed = json.load(f)
    for node in parsed["features"]:
        props = node["properties"]
        if props["nodetype"] == "pourpoint":
            nodeid = props["nodeid"]
            # Some watersheds should not receive water at all as they are outside the event (these are not all the watersheds with 0 water)
            if nodeid in (52, 48, 96, 27):
                assert props[attr] == 0, "These watershed should not have any water from the precip raster"
            elif nodeid in (61, 63, 59):
                # Some watersheds should receive water (these are not all the watersheds with 0 water)
                assert props[attr] > 0, "These watershed should have any water from the precip raster"
        else:
            # junction
            assert props[attr] == 0, "Junctions should not receive water in this process"

    assert sum([x["properties"][attr] for x in parsed["features"]]) > 0, "Volumes sum to 0"
    assert len(nodesreader.read_geojson_features()) == len(parsed["features"]), "Process has dropped features"


def test_rasterdefined_unit(nodesreader, tmp_path):
    crs = create_utm32_crs()  
    attr = "inputvol"

    bspotlabels_reader = RasterReader(labeledfile)
    precip_reader = RasterReader(precipraster_float_file)

    def calc(unit):
        # Returns the total volume in m3
        volumes_file_path = tmp_path / f"volumes_{unit}.geojson"
        volumes_writer = VectorWriter("geojson", str(volumes_file_path), "", None, ogr.wkbPoint, crs)
        tool = RasterVolumeTool(nodesreader, bspotlabels_reader, precip_reader, unit, volumes_writer, attr)
        tool.process()
        with open(volumes_file_path) as f:
            parsed = json.load(f)
        return sum( [ x["properties"][attr] for x in parsed["features"] ] )

    # This is the sum of all cell values
    sum_precip_raster = np.sum(precip_reader.read())

    calc_m3 = calc(Unit.m3)
    assert calc_m3 == sum_precip_raster

    calc_l = calc(Unit.l)
    assert calc_l == pytest.approx(sum_precip_raster / 1000)

    calc_mm = calc(Unit.mm)
    cell_area = precip_reader.resolution[0] * precip_reader.resolution[1]
    assert calc_mm == pytest.approx(sum_precip_raster * 1e-3 * cell_area) # mm to meters, cell area

    