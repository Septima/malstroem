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

from malstroem.algorithms import fill
from .algorithms import speedups, flow, dtypes
import logging


class DemTool(object):
    """Calculate filled DEM, flow directions, bluespot depths and optionally accumulated flow.

    Note
    ----
    Input DEM x, y and z coordinates must be in meters.

    Parameters
    ----------
    input_dem : rasterreader
        DEM data
    output_filled : rasterwriter
        Writes filled DEM
    output_flowdir : rasterwriter
        Writes flow direction raster
    output_depths : rasterwriter
        Writes bluespot depths
    output_accum : rasterwriter, optional
        Writes accumulated flow
    """

    def __init__(self, input_dem, output_filled, output_flowdir, output_depths, output_accum=None):
        self.input_dem = input_dem
        self.output_filled = output_filled
        self.output_flowdir = output_flowdir
        self.output_depths = output_depths
        self.output_accum = output_accum

        self.logger = logging.getLogger(__name__)

    def process(self):
        """Process
        """
        dem = self.input_dem.read().astype(dtypes.DTYPE_DTM, casting='same_kind', copy=False)
        transform = self.input_dem.transform

        # Input cells must be square
        assert abs(abs(transform[1]) - abs(transform[5])) < 0.01 * abs(transform[1]), "Input cells must be square"

        if not speedups.enabled:
            self.logger.warning('Warning: Speedups are not available. If you have more than toy data you want them to be!')

        self.logger.info("Calculating filled DEM")
        # Filled and derived from it
        filled = fill.fill_terrain(dem)
        self.output_filled.write(filled)

        self.logger.info("Calculating bluespot depths")
        depths = filled - dem
        self.output_depths.write(depths)

        del filled
        del depths

        self.logger.info("Calculating flow directions")
        # Filled no flats and derived
        short, diag = fill.minimum_safe_short_and_diag(dem)
        filled_no_flats = fill.fill_terrain_no_flats(dem, short=short, diag=diag)
        del dem

        flowdir = flow.terrain_flowdirection(filled_no_flats, edges_flow_outward=True)
        self.output_flowdir.write(flowdir)
        del filled_no_flats

        if self.output_accum:
            self.logger.info("Calculating flow accumulation")
            accum = flow.accumulated_flow(flowdir)
            self.output_accum.write(accum)
            del accum

        self.logger.info("Done")
