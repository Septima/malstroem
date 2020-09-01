# coding=utf-8
# -------------------------------------------------------------------------------------------------
# Copyright (c) 2020
# Developed by Septima.dk. This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 2 of the License, or (at you option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PORPOSE. See the GNU Gene-
# ral Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.
# -------------------------------------------------------------------------------------------------
import click
import click_log

from osgeo import ogr
from malstroem import io, hyps


@click.command('hyps')
@click.option('-bluespots', required=True, type=click.Path(exists=True), help='Bluespot ID file')
@click.option('-dem', required=True, type=click.Path(exists=True), help='DEM file')
@click.option('-pourpoints', required=True, help='OGR datasource containing pourpoints layer')
@click.option('-pourpoints_layer', default='pourpoints', show_default=True, required=False, help='Pourpoints layer name')
@click.option('-zresolution', required=True, type=float, help='Resolution (or bin width) in [m] of output Z histogram')
@click.option('-out', required=True, help='Output OGR datasource')
@click.option('-out_hyps_layer', default='hyps', show_default=True, help='Layer name of output hypsometry layer')
@click.option('-format', type=str, default='CSV', help='OGR driver. See OGR documentation')
@click.option('-dsco', multiple=True, type=str, nargs=0, help='OGR datasource creation options. See OGR documentation')
@click.option('-lco', multiple=True, type=str, nargs=0, help='OGR layer creation options. See OGR documentation')
@click_log.simple_verbosity_option()
def process_hypsometry(bluespots, dem, pourpoints, pourpoints_layer, zresolution, out, out_hyps_layer, format, dsco, lco):
    """Calculate statistical hypsometric (terrain elevation) measures for each bluespot.

    For each bluespot these values describing the terrain within the bluespot are returned: 
        - A DEM Z value histogram with user definable bin width (resolution)
        - Number og bins, effective upper and lower bounds of the histogram
        - Actual minimum and maximum Z values
    
    The values of the histogram are formatted as a single string using pipe '|' as seperator. Like:
    2|1|0|3

    For documentation of OGR features (format, dsco and lco) see http://www.gdal.org/ogr_formats.html
    """
    pourpoints_reader = io.VectorReader(pourpoints, pourpoints_layer)
    labeled_reader = io.RasterReader(bluespots)
    dem_reader = io.RasterReader(dem)

    ogr_format = str(format)
    hyps_writer = io.VectorWriter(ogr_format, out, out_hyps_layer, None, ogr.wkbNone, dem_reader.crs)

    hyps.bluespot_hypsometry_io(labeled_reader, dem_reader, pourpoints_reader, zresolution, hyps_writer)