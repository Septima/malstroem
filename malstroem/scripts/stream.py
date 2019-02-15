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

import click
import click_log

from osgeo import ogr
from malstroem import io, streams


# out_nodes and out_streams are OGR datasources. For single-table formats (like geojson, tab etc)
# these should be absolute path to the file. For multi-table format this should be the ogr datasource to the database
# and then the layer names are taken from out_nodes_layer and out_streams_layer
@click.command('network')
@click.option('-bluespots', required=True, type=click.Path(exists=True), help='Bluespots file')
@click.option('-flowdir', required=True, type=click.Path(exists=True), help='Flow directions file')
@click.option('-pourpoints', required=True, help='OGR datasource containing pourpoints layer')
@click.option('-pourpoints_layer', default='pourpoints', show_default=True, required=False, help='Pourpoints layer name')
@click.option('-out', required=True, help='Output OGR datasource')
@click.option('-out_nodes_layer', default='nodes', show_default=True, help='Layer name of output nodes layer')
@click.option('-out_streams_layer', default='streams',show_default=True, help='Layer name of output streams layer')
@click.option('-format', type=str, default='ESRI shapefile', help='OGR driver. See OGR documentation')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
@click_log.simple_verbosity_option()
def process_network(bluespots, flowdir, pourpoints, pourpoints_layer, out, out_nodes_layer, out_streams_layer, format, dsco, lco):
    """Calculate stream network between bluespots.

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    pourpoints_reader = io.VectorReader(pourpoints, pourpoints_layer)
    bluespot_reader = io.RasterReader(bluespots)
    flowdir_reader = io.RasterReader(flowdir)

    format = str(format)
    out_nodes_layer = str(out_nodes_layer)
    out_streams_layer = str(out_streams_layer)

    nodes_writer = io.VectorWriter(format, out, out_nodes_layer, None, ogr.wkbPoint, flowdir_reader.crs, dsco, lco)
    streams_writer = io.VectorWriter(format, out, out_streams_layer, None, ogr.wkbLineString, flowdir_reader.crs, dsco, lco)

    stream_tool = streams.StreamTool(pourpoints_reader, bluespot_reader, flowdir_reader, nodes_writer, streams_writer)
    stream_tool.process()
