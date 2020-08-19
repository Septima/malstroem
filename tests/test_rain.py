from data.fixtures import nodesreader
from malstroem.rain import SimpleVolumeTool
from malstroem.io import VectorWriter
from osgeo import osr, ogr
import json


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
    
