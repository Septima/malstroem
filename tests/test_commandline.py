from click.testing import CliRunner

from malstroem.scripts.cli import cli
from malstroem import io
from data.fixtures import dtmfile, filledfile, flowdirnoflatsfile, depthsfile, labeledfile, wshedsfile, pourpointsfile, nodesfile
import numpy as np
import os


def test_complete(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['complete',
                                 '-r', 10,
                                 '-r', 100,
                                 '-filter', 'area > 20.5 and maxdepth > 0.5 or volume > 2.5',
                                 '-dem', dtmfile,
                                 '-outdir', str(tmpdir)])
    assert result.exit_code == 0, result.output
    assert os.path.isfile(str(tmpdir.join('filled.tif')))

    r = io.RasterReader(str(tmpdir.join('bluespots.tif')))
    data = r.read()

    assert np.max(data) == 486, result.output

    v = io.VectorReader(str(tmpdir.join('malstroem.gpkg')), 'events')
    data = v.read_geojson_features()
    assert len(data) == 544, result.output


def test_complete_nofilter(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['complete',
                                 '-r', 10,
                                 '-r', 100,
                                 '-dem', dtmfile,
                                 '-outdir', str(tmpdir)])
    assert result.exit_code == 0, result.output
    assert os.path.isfile(str(tmpdir.join('filled.tif')))
    r = io.RasterReader(str(tmpdir.join('bluespots.tif')))
    data = r.read()

    assert np.max(data) == 523

    v = io.VectorReader(str(tmpdir.join('malstroem.gpkg')), 'events')
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


def test_rain(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['rain',
                                 '-nodes', nodesfile,
                                 '-nodes_layer', 0,
                                 '-r', 10,
                                 '-r', 20,
                                 '-r', 100,
                                 '-out', str(tmpdir)])
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(str(tmpdir.join('events.shp')))


def test_chained(tmpdir):
    filled = str(tmpdir.join('filled.tif'))
    depths = str(tmpdir.join('depths.tif'))
    flowdir = str(tmpdir.join('flowdir.tif'))
    accum = str(tmpdir.join('accum.tif'))
    bspots = str(tmpdir.join('bspots.tif'))
    pourpoints = str(tmpdir.join('pourpoints.shp'))
    nodes = str(tmpdir.join('nodes.shp'))
    streams = str(tmpdir.join('streams.shp'))
    events = str(tmpdir.join('events.shp'))

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

    # Rain
    result = runner.invoke(cli, ['rain',
                                 '-nodes', str(tmpdir),
                                 '-r', 10,
                                 '-r', 20,
                                 '-r', 100,
                                 '-out', str(tmpdir)])
    assert result.exit_code == 0, 'Output: {}'.format(result.output)
    assert os.path.isfile(events)

    reader = io.VectorReader(str(tmpdir), 'events')
    data = reader.read_geojson_features()
    assert len(data) == 544
