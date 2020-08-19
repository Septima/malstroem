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
from malstroem import io, network


@click.command('net')
@click.option('-inputvolumes', required=True, help='OGR datasource containing nodes layer with model input water volumes')
@click.option('-inputvolumes_layer', default='initvolumes', show_default=True, help='Layer name')
@click.option('--attribute', '-a', default='inputv', type=str, help='Attribute containing the model input water volume in [m3]')
@click.option('-out', required=True, help='Output OGR datasource')
@click.option('-out_layer', default='finalstate', show_default=True, help='Layer name of output final state layer')
@click.option('-format', type=str, default='ESRI shapefile', help='OGR driver. See OGR documentation')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
@click_log.simple_verbosity_option()
def process_net(inputvolumes, inputvolumes_layer, attribute, out, out_layer, format, dsco, lco):
    """Calculate bluespot fill and stream network volumes in the final state.

    The rain event is defined by the initial water volumes per node.

    \b
    Example:
    malstroem rain -volumes results.gpkg -out results.gpkg -format gpkg

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    inputvolumes_layer = inputvolumes_layer
    format = str(format)
    out_layer = str(out_layer)


    volumes_reader = io.VectorReader(inputvolumes, inputvolumes_layer)
    events_writer = io.VectorWriter(format, out, out_layer, None, ogr.wkbPoint, volumes_reader.crs, dsco, lco)

    # Process events
    calculator = network.FinalStateCalculator(volumes_reader, attribute, events_writer)
    calculator.process()
