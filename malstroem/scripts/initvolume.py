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


@click.command('initvolumes')
@click.option('-nodes', required=True, help='OGR datasource containing nodes layer')
@click.option('-nodes_layer', default='nodes', show_default=True, help='Nodes layer name ')
@click.option('-mm', required=False, type=float, help='Evenly distributed rain event [mm]')
@click.option('-pr', required=False, type=click.Path(exists=True), help='Raster [mm]')
@click.option('-out', required=True, help='Output OGR datasource')
@click.option('-out_layer', default='initvolumes', show_default=True, help='Calculated model input volumes in  [m3]')
@click.option('-out_attribute', default='inputv', show_default=True, help='Name of output attribute')
@click.option('-format', type=str, default='ESRI shapefile', help='OGR driver. See OGR documentation')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
@click_log.simple_verbosity_option()
def process_volumes(nodes, nodes_layer, mm, pr, out, out_layer, out_attribute, format, dsco, lco):
    """Calculate initial water volumes for each watershed.

    The output from this process can be used as input for the network calculation.

    \b
    Examples:
    malstroem rain -mm 10 -nodes results.gpkg -out results.gpkg -format gpkg
    malstroem rain -pr precip_raster.tif -nodes results.gpkg -out results.gpkg -format gpkg

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    # Validate mutually exclusive
    if mm and pr:
        raise Exception("-mm and -r are mutually exclusive")

    nodes_layer = nodes_layer
    format = str(format)
    out_layer = str(out_layer)

    # Calculate volumes
    nodes_reader = io.VectorReader(nodes, nodes_layer)
    volumes_writer = io.VectorWriter(format, out, out_layer, None, ogr.wkbPoint, nodes_reader.crs, dsco, lco) 
    rain_tool = raintool.SimpleVolumeTool(nodes_reader, volumes_writer, out_attribute, mm)
    rain_tool.process()
