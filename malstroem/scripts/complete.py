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
from __future__ import (absolute_import, division, print_function) #, unicode_literals)
from builtins import *

import click
import click_log

from malstroem import dem as demtool, bluespots, io, streams, rain as raintool, network
from ._utils import parse_filter
from osgeo import ogr, osr
import os

import logging
logger = logging.getLogger(__name__)

@click.command('complete')
@click.option('-dem', type=click.Path(exists=True), help='DEM raster file. Horisontal and vertical units must be meters')
@click.option('-outdir', type=click.Path(exists=True), help='Output directory')
@click.option('--rain', '-r', required=True, multiple=False, type=float, help='Rain incident in mm')
@click.option('-accum', is_flag=True, help='Calculate accumulated flow')
@click.option('-vector', is_flag=True, help='Vectorize bluespots and watersheds')
@click.option('-filter', help='Filter bluespots by area, maximum depth and volume. Format: '
                               '"area > 20.5 and (maxdepth > 0.05 or volume > 2.5)"')
@click_log.simple_verbosity_option()
def process_all(dem, outdir, accum, filter, rain, vector):
    """Quick option to run all processes.

    \b
    Example:
    malstroem complete -r 10 -r 30 -filter "volume > 2.5" -dem dem.tif -outdir ./outdir/
    """
    # Check that outdir exists and is empty
    if not os.path.isdir(outdir) or not os.path.exists(outdir) or os.listdir(outdir):
        logger.error("outdir isn't an empty directory")
        return 1

    outvector = os.path.join(outdir, 'malstroem.gpkg')
    ogr_drv = 'gpkg'
    ogr_dsco = []
    ogr_lco = ["SPATIAL_INDEX=NO"]
    nodatasubst = -999


    filter_function = parse_filter(filter)
    dem_reader = io.RasterReader(dem, nodatasubst=nodatasubst)
    tr = dem_reader.transform
    crs = dem_reader.crs

    logger.info('Processing')
    logger.info('   dem: {}'.format(dem))
    logger.info('   outdir: {}'.format(outdir))
    logger.info('   rain: {}mm'.format(rain))
    logger.info('   accum: {}'.format(accum))
    logger.info('   filter: {}'.format(filter))

    # Process DEM
    filled_writer = io.RasterWriter(os.path.join(outdir, 'filled.tif'), tr, crs, nodatasubst)
    flowdir_writer = io.RasterWriter(os.path.join(outdir, 'flowdir.tif'), tr, crs)
    depths_writer = io.RasterWriter(os.path.join(outdir, 'bs_depths.tif'), tr, crs)
    accum_writer = io.RasterWriter(os.path.join(outdir, 'accum.tif'), tr, crs) if accum else None

    dtmtool = demtool.DemTool(dem_reader, filled_writer, flowdir_writer, depths_writer, accum_writer)
    dtmtool.process()

    # Process bluespots
    depths_reader = io.RasterReader(depths_writer.filepath)
    flowdir_reader = io.RasterReader(flowdir_writer.filepath)
    accum_reader = io.RasterReader(accum_writer.filepath) if accum_writer else None
    pourpoint_writer = io.VectorWriter(ogr_drv, outvector, 'pourpoints', None, ogr.wkbPoint, crs, dsco=ogr_dsco, lco = ogr_lco)
    watershed_writer = io.RasterWriter(os.path.join(outdir, 'watersheds.tif'), tr, crs, 0)
    watershed_vector_writer = io.VectorWriter(ogr_drv, outvector, 'watersheds', None, ogr.wkbMultiPolygon, crs, dsco=ogr_dsco, lco = ogr_lco) if vector else None
    labeled_writer = io.RasterWriter(os.path.join(outdir, 'bluespots.tif'), tr, crs, 0)
    labeled_vector_writer = io.VectorWriter(ogr_drv, outvector, 'bluespots', None, ogr.wkbMultiPolygon, crs, dsco=ogr_dsco, lco = ogr_lco) if vector else None

    bluespot_tool = bluespots.BluespotTool(
        input_depths=depths_reader,
        input_flowdir=flowdir_reader,
        input_bluespot_filter_function=filter_function,
        input_accum=accum_reader,
        input_dem=dem_reader,
        output_labeled_raster=labeled_writer,
        output_labeled_vector=labeled_vector_writer,
        output_pourpoints=pourpoint_writer,
        output_watersheds_raster=watershed_writer,
        output_watersheds_vector=watershed_vector_writer
    )
    bluespot_tool.process()

    # Process pourpoints
    pourpoints_reader = io.VectorReader(outvector, pourpoint_writer.layername)
    bluespot_reader = io.RasterReader(labeled_writer.filepath)
    flowdir_reader = io.RasterReader(flowdir_writer.filepath)
    nodes_writer = io.VectorWriter(ogr_drv, outvector, 'nodes', None, ogr.wkbPoint, crs, dsco=ogr_dsco, lco = ogr_lco)
    streams_writer = io.VectorWriter(ogr_drv, outvector, 'streams', None, ogr.wkbLineString, crs, dsco=ogr_dsco, lco = ogr_lco)

    stream_tool = streams.StreamTool(pourpoints_reader, bluespot_reader, flowdir_reader, nodes_writer, streams_writer)
    stream_tool.process()

    # Calculate volumes
    nodes_reader = io.VectorReader(outvector, nodes_writer.layername)
    volumes_writer = io.VectorWriter(ogr_drv, outvector, 'initvolumes', None, ogr.wkbPoint, crs, dsco=ogr_dsco, lco = ogr_lco) 
    rain_tool = raintool.SimpleVolumeTool(nodes_reader, volumes_writer, "inputv" ,rain)
    rain_tool.process()

    # Process final state
    volumes_reader = io.VectorReader(outvector, volumes_writer.layername)
    events_writer = io.VectorWriter(ogr_drv, outvector, 'finalstate', None, ogr.wkbPoint, crs, dsco=ogr_dsco, lco = ogr_lco)
    calculator = network.FinalStateCalculator(volumes_reader, "inputv", events_writer)
    calculator.process()

