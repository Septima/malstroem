from click.testing import CliRunner

from malstroem.scripts.cli import cli
from malstroem import io
from data.fixtures import dtmfile, filledfile, flowdirnoflatsfile, depthsfile, labeledfile, wshedsfile, pourpointsfile, nodesfile, initvolsfile, finalvolsfile, hypsfile
import numpy as np
import os


def test_complete(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['complete',
                                 #'-r', 10,
                                 '-r', 100,
                                 '-filter', 'area > 20.5 and maxdepth > 0.5 or volume > 2.5',
                                 '-dem', dtmfile,
                                 '-outdir', str(tmpdir)])
    assert result.exit_code == 0, result.output
    assert os.path.isfile(str(tmpdir.join('filled.tif')))

    r = io.RasterReader(str(tmpdir.join('bluespots.tif')))
    data = r.read()

    assert np.max(data) == 486, result.output

    v = io.VectorReader(str(tmpdir.join('malstroem.gpkg')), 'finalstate')
    data = v.read_geojson_features()
    assert len(data) == 544, result.output


def test_complete_nofilter(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['complete',
                                 #'-r', 10,
                                 '-r', 100,
                                 '-dem', dtmfile,
                                 '-outdir', str(tmpdir)])
    assert result.exit_code == 0, result.output
    assert os.path.isfile(str(tmpdir.join('filled.tif')))
    r = io.RasterReader(str(tmpdir.join('bluespots.tif')))
    data = r.read()

    assert np.max(data) == 523

    v = io.VectorReader(str(tmpdir.join('malstroem.gpkg')), 'finalstate')
    data = v.read_geojson_features()
    assert len(data) == 587, result.output


def test_filled(tmpdir):
    ff = str(tmpdir.join('filled.tif'))
    runner = CliRunner()
    result = runner.invoke(cli, ['filled',
                                 '-dem', dtmfile,
                                 '-out', ff])
    assert result.exit_code == 0
    assert result.output == ''
    assert os.path.isfile(ff)


def test_depths(tmpdir):
    df = str(tmpdir.join('depths.tif'))
    runner = CliRunner()
    result = runner.invoke(cli, ['depths',
                                 '-dem', dtmfile,
                                 '-filled', filledfile,
                                 '-out', df])
    assert result.exit_code == 0
    assert result.output == ''
    assert os.path.isfile(df)


def test_flowdir(tmpdir):
    ff = str(tmpdir.join('flowdir.tif'))
    runner = CliRunner()
    result = runner.invoke(cli, ['flowdir',
                                 '-dem', dtmfile,
                                 '-out', ff])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(ff)


def test_accum(tmpdir):
    f = str(tmpdir.join('accum.tif'))
    runner = CliRunner()
    result = runner.invoke(cli, ['accum',
                                 '-flowdir', flowdirnoflatsfile,
                                 '-out', f])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(f)


def test_bspot(tmpdir):
    f = str(tmpdir.join('bspots.tif'))
    runner = CliRunner()
    result = runner.invoke(cli, ['bspots',
                                 '-depths', depthsfile,
                                 '-out', f])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(f)




def test_filtered_bspot(tmpdir):
    f = str(tmpdir.join('bspots.tif'))
    runner = CliRunner()
    result = runner.invoke(cli, ['bspots',
                                 '-filter', 'area > 20.5 and maxdepth > 0.5 or volume > 2.5',
                                 '-depths', depthsfile,
                                 '-out', f])
    assert result.exit_code == 0
    assert result.output == ''
    assert os.path.isfile(f)


def test_wsheds(tmpdir):
    f = str(tmpdir.join('wsheds.tif'))
    runner = CliRunner()
    result = runner.invoke(cli, ['wsheds',
                                 '-bluespots', labeledfile,
                                 '-flowdir', flowdirnoflatsfile,
                                 '-out', f])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(f)


def test_pourpoints(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['pourpts',
                                 '-bluespots', labeledfile,
                                 '-depths', depthsfile,
                                 '-watersheds', wshedsfile,
                                 '-dem', dtmfile,
                                 '-out', str(tmpdir)])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(str(tmpdir.join('pourpoints.shp')))


def test_network(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['network',
                                 '-bluespots', labeledfile,
                                 '-flowdir', flowdirnoflatsfile,
                                 '-pourpoints', pourpointsfile,
                                 '-pourpoints_layer', 0,
                                 '-out', str(tmpdir),
                                ])

    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(str(tmpdir.join('nodes.shp')))
    assert os.path.isfile(str(tmpdir.join('streams.shp')))


def test_initvolumes(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['initvolumes',
                                 '-nodes', nodesfile,
                                 '-nodes_layer', 0,
                                 '-mm', 20,
                                 '-out', str(tmpdir)],)
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(str(tmpdir.join('initvolumes.shp')))

def test_finalvols(tmpdir):
    runner = CliRunner()
    out_file = str(tmpdir.join("finalvolumes.shp"))
    result = runner.invoke(cli, ['finalvols',
                                 '-inputvolumes', initvolsfile,
                                 '-out', str(tmpdir)])
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(out_file)

def test_hyps(tmpdir):
    runner = CliRunner()
    out_file = str(tmpdir.join('hyps.csv'))
    result = runner.invoke(cli, ['hyps',
                                 '-bluespots', labeledfile,
                                 '-dem', dtmfile,
                                 '-pourpoints', pourpointsfile,
                                 '-zresolution', 0.1,
                                 '-out', out_file])
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(out_file)
    from csv import DictReader
    from malstroem import hyps
    with open(out_file) as f:
        reader = DictReader(f)
        for row in reader:
            for float_key in ["bspot_dmax", "hist_num_bins", "hist_lower_bound", "hist_upper_bound", "hist_resolution", "zmin", "zmax", "cell_area"]:
                float(row[float_key])
            assert int(row["hist_num_bins"]) > 0

            h = hyps.hypsometrystats_from_flatdict(row)
            assert len(h.zhistogram.counts) > 0 
            hyps.assert_hypsometrystats_valid(h)    

def test_finallevels(tmpdir):
    runner = CliRunner()
    out_file = str(tmpdir.join('hyps.geojson'))
    result = runner.invoke(cli, ['finallevels',
                                 '-finalvols', finalvolsfile,
                                 '-hyps', hypsfile,
                                 '-out', out_file])
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(out_file)
    import json
    with open(out_file) as f:
        parsed = json.load(f)
        for row in parsed["features"]:
            for float_key in ["approx_z"]:
                float(row["properties"][float_key])


def test_chained(tmpdir):
    filled = str(tmpdir.join('filled.tif'))
    depths = str(tmpdir.join('depths.tif'))
    flowdir = str(tmpdir.join('flowdir.tif'))
    accum = str(tmpdir.join('accum.tif'))
    bspots = str(tmpdir.join('bspots.tif'))
    pourpoints = str(tmpdir.join('pourpoints.shp'))
    nodes = str(tmpdir.join('nodes.shp'))
    streams = str(tmpdir.join('streams.shp'))
    initvolumes = str(tmpdir.join('initvolumes.shp'))
    final = str(tmpdir.join('finalvolumes.shp'))

    runner = CliRunner()

    # Filled
    result = runner.invoke(cli, ['filled',
                                 '-dem', dtmfile,
                                 '-out', filled])
    assert result.exit_code == 0
    assert result.output == ''
    assert os.path.isfile(filled)

    # Depths
    result = runner.invoke(cli, ['depths',
                                 '-dem', dtmfile,
                                 '-filled', filled,
                                 '-out', depths])
    assert result.exit_code == 0
    assert result.output == ''
    assert os.path.isfile(depths)

    # Flowdir
    result = runner.invoke(cli, ['flowdir',
                                 '-dem', dtmfile,
                                 '-out', flowdir])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(flowdir)

    # Accum
    result = runner.invoke(cli, ['accum',
                                 '-flowdir', flowdir,
                                 '-out', accum])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(accum)

    # Bluespots
    result = runner.invoke(cli, ['bspots',
                                 '-filter', 'area > 20.5 and maxdepth > 0.5 or volume > 2.5',
                                 '-depths', depths,
                                 '-out', bspots])
    assert result.exit_code == 0
    assert result.output == ''
    assert os.path.isfile(bspots)

    # Watersheds
    wsheds = str(tmpdir.join('wsheds.tif'))
    result = runner.invoke(cli, ['wsheds',
                                 '-bluespots', bspots,
                                 '-flowdir', flowdir,
                                 '-out', wsheds])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(wsheds)

    # Pourpoints
    result = runner.invoke(cli, ['pourpts',
                                 '-bluespots', bspots,
                                 '-depths', depths,
                                 '-watersheds', wsheds,
                                 '-dem', dtmfile,
                                 '-out', str(tmpdir)])
    assert result.output == ''
    assert result.exit_code == 0
    assert os.path.isfile(pourpoints)

    # Nodes
    result = runner.invoke(cli, ['network',
                                 '-bluespots', bspots,
                                 '-flowdir', flowdir,
                                 '-pourpoints', str(tmpdir),
                                 '-out', str(tmpdir),
                                 ])

    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(nodes)
    assert os.path.isfile(streams)

    # Initial volumes
    result = runner.invoke(cli, ['initvolumes',
                                 '-nodes', str(tmpdir),
                                 '-mm', 20,
                                 '-out', str(tmpdir)])
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(initvolumes)

    # Network
    result = runner.invoke(cli, ['finalvols',
                                 '-inputvolumes', str(tmpdir),
                                 '-out', str(tmpdir)])
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(final)

    reader = io.VectorReader(str(tmpdir), 'finalvolumes')
    data = reader.read_geojson_features()
    assert len(data) == 544
