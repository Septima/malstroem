# coding=utf-8
# -------------------------------------------------------------------------------------------------
# Copyright (c) 2016
# Developed by Septima.dk and Thomas Balstrøm (University of Copenhagen) for the Danish Agency for
# Data Supply and Efficiency. This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 2 of the License, or (at you option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PORPOSE. See the GNU Gene-
# ral Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.
# -------------------------------------------------------------------------------------------------
from __future__ import (absolute_import, division, print_function)  # unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                      int, map, next, oct, open, pow, range, round,
                      super, zip)  # str

# unicode_literals and str left out as they do not play well with click.

import click
import click_log

from malstroem import io
from malstroem.bluespots import filterbluespots, assemble_pourpoints
from malstroem.vector import vectorize_labels_file_io
from ._utils import parse_filter
from malstroem.algorithms import label, flow, fill
from osgeo import ogr

@click.command('bspots')
@click.option('-depths', required=True, type=click.Path(exists=True), help='Depths file')
@click.option('-out', required=True, type=click.Path(exists=False), help='Output file (bluespots)')
@click.option('-filter', help='Filter bluespots by area, maximum depth and volume. Format: '
                               '"area > 20.5 and (maxdepth > 0.05 or volume > 2.5)"')
@click_log.simple_verbosity_option()
def process_bspots(depths, out, filter):
    """Label bluespots.

    Assign unique bluespot ID to all cells belonging to a bluespot. Optionally disregarding some bluespots based on a
    filter expression. ID 0 (zero) is used for cells not belonging to a bluespot.
    """

    depths_reader = io.RasterReader(depths)
    labeled_writer = io.RasterWriter(out, depths_reader.transform, depths_reader.crs, 0)
    filter_function = parse_filter(filter)

    transform = depths_reader.transform
    cell_width = abs(transform[1])
    cell_height = abs(transform[5])
    cell_area = cell_width * cell_height

    depths_data = depths_reader.read()
    raw_labeled, raw_nlabels = label.connected_components(depths_data)
    if not filter:
        # This is the end  my friend
        labeled_writer.write(raw_labeled)
        return

    del depths

    raw_bluespot_stats = label.label_stats(depths_data, raw_labeled)
    keepers = filterbluespots(filter_function, cell_area, raw_bluespot_stats)
    new_components = label.keep_labels(raw_labeled, keepers)
    labeled, nlabels = label.connected_components(new_components)
    labeled_writer.write(labeled)


@click.command('wsheds')
@click.option('-bluespots', required=True, type=click.Path(exists=True), help='Bluespot file')
@click.option('-flowdir', required=True, type=click.Path(exists=True), help='Flow directions file')
@click.option('-out', required=True, type=click.Path(exists=False), help='Output file (bluespot watersheds)')
def process_wsheds(bluespots, flowdir, out):
    """Bluespot watersheds.

    Assign bluespot ID to all cells within the local bluespot watershed.
    """
    bspot_reader = io.RasterReader(bluespots)
    flowdir_reader = io.RasterReader(flowdir)
    wshed_writer = io.RasterWriter(out, bspot_reader.transform, bspot_reader.crs, 0)

    watersheds = bspot_reader.read()
    flowdir = flowdir_reader.read()
    flow.watersheds_from_labels(flowdir, watersheds, unassigned=0)
    wshed_writer.write(watersheds)


@click.command('pourpts')
@click.option('-bluespots', required=True, type=click.Path(exists=True), help='Bluespot file')
@click.option('-depths', required=True, type=click.Path(exists=True), help='Depths file')
@click.option('-watersheds', required=True, type=click.Path(exists=True), help='Watersheds file')
@click.option('-dem', required=False, type=click.Path(exists=True), help='DEM file')
@click.option('-accum', required=False, type=click.Path(exists=True), help='Accumulated flow file')
@click.option('-out', required=True, type=str, help='Output OGR datasource')
@click.option('-format', type=str, default='ESRI shapefile', help='OGR format. See OGR documentation')
@click.option('-layername', type=str, default='pourpoints', show_default=True, help='Output layer name')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
def process_pourpoints(bluespots, depths, watersheds, dem, accum, out, format, layername, dsco, lco):
    """Determine pour points.

    \b
    Determines a pour point for each bluespot using one of two methods:
        * Random candidate. Requires DEM only
        * Maximum accumulated flow candidate. Requires accumulated flow
    The output of the two methods only differ when there are more than one pour point candidate (ie multiple threshold
    cells with identical Z) for a given bluespot.

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    bspot_reader = io.RasterReader(bluespots)
    depths_reader = io.RasterReader(depths)
    wsheds_reader = io.RasterReader(watersheds)

    data = accum if accum else dem
    if not data:
        raise Exception('Either accum or dem must be specified')
    data_reader = io.RasterReader(data)

    format = str(format)
    layername = str(layername)

    pourpnt_writer = io.VectorWriter(format, out, layername, [], ogr.wkbPoint, depths_reader.crs, dsco, lco)

    # Recalculate stats on filtered bluespots
    labeled_data = bspot_reader.read()
    depths_data = depths_reader.read()
    bluespot_stats = label.label_stats(depths_data, labeled_data)
    del depths_data

    if accum:
        pp_pix = label.label_max_index(data_reader.read(), labeled_data)
    elif dem:
        dem_data = data_reader.read()
        short, diag = fill.minimum_safe_short_and_diag(dem_data)
        filled_no_flats = fill.fill_terrain_no_flats(dem_data, short, diag)
        pp_pix = label.label_min_index(filled_no_flats, labeled_data)
        del dem_data

    watershed_stats = label.label_count(wsheds_reader.read())
    pour_points = assemble_pourpoints(depths_reader.transform, pp_pix, bluespot_stats, watershed_stats)

    feature_collection = dict(type="FeatureCollection", features=pour_points)
    pourpnt_writer.write_geojson_features(feature_collection)


@click.command('polys')
@click.option('-raster', required=True, type=click.Path(exists=True), help='Raster file with IDs (bluespots or watersheds)')
@click.option('-out', required=True, type=str, help='Output OGR datasource')
@click.option('-format', type=str, default='ESRI shapefile', help='OGR format. See OGR documentation')
@click.option('-layername', type=str, default='polygonized', show_default=True, help='Output layer name')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
def process_polys(bluespots, out, format, layername, dsco, lco):
    """Polygonize ID raster.

    Create vector polygons for all connected regions of cells in the raster sharing a common ID.
    
    Note that partially filled bluespots may have disconnected regions and hence there may be more than one polygon
    with the same bluespot ID.

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    vectorize_labels_file_io(bluespots, out, layername, format, dsco, lco)
    


