import pytest
from osgeo import ogr
from data.fixtures import dtmfile, labeledfile, pourpointsfile
from malstroem.io import RasterReader, VectorReader, VectorWriter
from malstroem.hyps import bluespot_hypsometry_stats, HypsometryStats, Histogram, HistogramBinsInfo, bluespot_hypsometry_io, _hypsometrystats_from_flatdict, _assert_hypsometrystats_valid


def test_bluespot_hypsometry_stats(tmp_path):
    dtm_reader = RasterReader(dtmfile)
    labeled_reader = RasterReader(labeledfile)

    resolution = 0.1

    hypsinfo = list(bluespot_hypsometry_stats(labeled_reader.read(), dtm_reader.read(), resolution))

    assert len(hypsinfo) == 105
    assert hypsinfo[8][0] == 8, "Hypsometric info is not returned in label order"
    i8 = hypsinfo[8][1]
    assert isinstance(i8, HypsometryStats)
    assert isinstance(i8.zhistogram, Histogram)
    assert len(i8.zhistogram.counts) == 22
    assert sum(i8.zhistogram.counts) == 751
    
    for lbl, stats in hypsinfo:
        _assert_hypsometrystats_valid(stats)
        assert stats.zhistogram.bins.resolution == resolution


def test_bluespot_hypsometry_io(tmp_path):
    dtm_reader = RasterReader(dtmfile)
    labeled_reader = RasterReader(labeledfile)
    pourpoints_reader = VectorReader(pourpointsfile)

    cell_area = labeled_reader.resolution[0] * labeled_reader.resolution[1]

    hyps_file = tmp_path / "hyps.geojson"
    hyps_writer = VectorWriter("geojson", str(hyps_file), "hyps", None, ogr.wkbNone, dtm_reader.crs)

    bluespot_hypsometry_io(labeled_reader, dtm_reader, pourpoints_reader, 0.1, hyps_writer)

    assert hyps_file.is_file()

    import json
    with open(hyps_file) as f:
        parsed = json.load(f)

    hypsinfo = parsed["features"]
    assert len(hypsinfo) == 105
    i8 = _hypsometrystats_from_flatdict(hypsinfo[8]["properties"])
    assert isinstance(i8, HypsometryStats)
    assert isinstance(i8.zhistogram, Histogram)
    assert len(i8.zhistogram.counts) == 22
    assert sum(i8.zhistogram.counts) == 751

    for h in hypsinfo:
        assert h["geometry"] is None
        i = _hypsometrystats_from_flatdict(h["properties"])
        _assert_hypsometrystats_valid(i)
        assert pytest.approx(cell_area) == h["properties"]["cell_area"] 