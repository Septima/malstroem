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
from malstroem import io, rain as raintool


@click.command('rain')
@click.option('-nodes', required=True, help='OGR datasource containing nodes layer')
@click.option('-nodes_layer', default='nodes', show_default=True, help='Nodes layer name ')
@click.option('--rain', '-r', required=True, multiple=True, type=float, help='Rain event in mm')
@click.option('-out', required=True, help='Output OGR datasource')
@click.option('-out_layer', default='events', show_default=True, help='Layer name of output events layer')
@click.option('-format', type=str, default='ESRI shapefile', help='OGR driver. See OGR documentation')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
@click_log.simple_verbosity_option()
def process_rain(nodes, nodes_layer, rain, out, out_layer, format, dsco, lco):
    """Calculate bluespot fill and spill volumes for specific rain event.

    The rain event is evenly distributed across the entire area.

    Note that multiple rain events can be calculated at once by repeating the '-r' option.

    \b
    Example:
    malstroem rain -r 10 -r 30 -nodes results.gpkg -out results.gpkg -format gpkg

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    nodes_layer = nodes_layer
    format = str(format)
    out_layer = str(out_layer)


    nodes_reader = io.VectorReader(nodes, nodes_layer)
    events_writer = io.VectorWriter(format, out, out_layer, None, ogr.wkbPoint, nodes_reader.crs, dsco, lco)

    rain_tool = raintool.RainTool(nodes_reader, events_writer, rain)
    rain_tool.process()
