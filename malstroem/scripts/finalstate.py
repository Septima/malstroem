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
from malstroem import io, network, approx

NODATASUBST = -999


@click.command('finalvols')
@click.option('-inputvolumes', required=True, help='OGR datasource containing nodes layer with model input water volumes')
@click.option('-inputvolumes_layer', default='initvolumes', show_default=True, help='Layer name')
@click.option('--attribute', '-a', default='inputv', type=str, help='Attribute containing the model input water volume in [m3]')
@click.option('-out', required=True, help='Output OGR datasource')
@click.option('-out_layer', default='finalvolumes', show_default=True, help='Layer name of output final state volumes layer')
@click.option('-format', type=str, default='ESRI shapefile', help='OGR driver. See OGR documentation')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
@click_log.simple_verbosity_option()
def process_net(inputvolumes, inputvolumes_layer, attribute, out, out_layer, format, dsco, lco):
    """Bluespot fill and stream network volumes in the final state of an event.

    The rain event is defined by the initial water volumes per node.

    \b
    Example:
    malstroem net -volumes results.gpkg -out results.gpkg -format gpkg

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



@click.command('finallevels')
@click.option('-finalvols', required=True, help='OGR datasource containing final state water volumes')
@click.option('-finalvols_layer', default='finalvolumes', show_default=True, help='Layer name')
@click.option('-hyps', required=True, help='OGR datasource containing hypsometric measures for each bluespot')
@click.option('-hyps_layer', default='hyps', show_default=True, help='Layer name')
@click.option('-out', required=True, help='Output OGR datasource (output is nongeometric)')
@click.option('-out_layer', default='finallevels', show_default=True, help='Layer name of output final state bluespot water level info')
@click.option('-format', type=str, default='geojson', help='OGR driver. See OGR documentation')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
@click_log.simple_verbosity_option()
def process_finallevels(finalvols, finalvols_layer, hyps, hyps_layer, out, out_layer, format, dsco, lco):
    """Approximate water levels of bluespots in the final state.

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    finalvols_reader = io.VectorReader(finalvols, finalvols_layer)
    hyps_reader = io.VectorReader(hyps, hyps_layer)

    levels_writer= io.VectorWriter(format, out, out_layer, None, ogr.wkbNone, finalvols_reader.crs, dsco, lco)

    approx.approx_water_level_io(finalvols_reader, hyps_reader, levels_writer)




# @click.command('finalbs')
# @click.option('-bluespots', required=True, type=click.Path(exists=True), help='Bluespot ID file')
# @click.option('-dem', required=True, type=click.Path(exists=True), help='DEM file')
# @click.option('-finalstate', required=True, help='OGR datasource containing final state water volumes')
# @click.option('-finalstate_layer', default='finalstate', show_default=True, help='Layer name')
# @click.option('-hyps', required=True, help='OGR datasource containing hypsometric measures for each bluespot')
# @click.option('-hyps_layer', default='hyps', show_default=True, help='Layer name')
# @click.option('-out_depths', required=False, type=click.Path(exists=False), help='Output depths file')
# @click.option('-out', required=True, help='Output OGR datasource if polygons should be processed')
# @click.option('-out_levels_layer', default='finallevels', show_default=True, help='Layer name of output final state bluespot water level info')
# @click.option('-out_polys_layer', default='finalextents', show_default=True, help='Layer name of output final state bluespot polygons')
# @click.option('-format', type=str, default='ESRI shapefile', help='OGR driver. See OGR documentation')
# @click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
# @click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
# @click_log.simple_verbosity_option()
# def process_net(bluespots, dem, finalstate, finalstate_layer, hyps, hyps_layer, out_depths, , format, dsco, lco):
#     """Approximate depths and extents of bluespots in the final state.

#     For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
#     """
#     dem_reader = io.RasterReader(dem, nodatasubst=NODATASUBST)