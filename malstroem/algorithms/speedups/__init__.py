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
"""Natively compiled versions of selected algorithms

Speedups are enabled by default if they are available.
"""
import warnings
import logging
logger = logging.getLogger(__name__)

from .. import flow, fill, label

try:
    from malstroem.algorithms.speedups import _fill, _flow, _label
    available = True
    import_error_msg = None
except ImportError as e:
    logger.info("Could not import speedups", exc_info=e)
    available = False

__all__ = ['available', 'enable', 'disable', 'enabled']

_orig = {}

# keep track of whether speedups are enabled
enabled = False


def enable():
    """Enable Cython speedups
    """
    if not available:
        warnings.warn("malstroem.raster.algorithms.speedups not available things will be SLOW", RuntimeWarning)
        return

    if _orig:
        return

    # Fill
    _orig['fill._fill_terrain'] = fill._fill_terrain
    fill._fill_terrain = _fill._fill_terrain

    _orig['fill._fill_terrain_no_flats'] = fill._fill_terrain_no_flats
    fill._fill_terrain_no_flats = _fill._fill_terrain_no_flats

    # Accumulated flow
    _orig['flow.trace_accumulated_flow'] = flow.trace_accumulated_flow
    flow.trace_accumulated_flow = _flow.trace_accumulated_flow

    _orig['flow.accumulated_flow'] = flow.accumulated_flow
    flow.accumulated_flow = _flow.accumulated_flow

    # Flow directions
    _orig['flow._terrain_flow'] = flow._terrain_flow
    flow._terrain_flow = _flow.terrain_flow

    # Watershed
    _orig['flow.assign_watersheds_upstream'] = flow.assign_watersheds_upstream
    flow.assign_watersheds_upstream = _flow.assign_watersheds_upstream

    # Label
    _orig['label.label_stats'] = label.label_stats
    label.label_stats = _label.label_stats

    _orig['label.label_min_index'] = label.label_min_index
    label.label_min_index = _label.label_min_index

    _orig['label.label_data'] = label.label_data
    label.label_data = _label.label_data

    global enabled
    enabled = True


def disable():
    """Disable Cython speedups
    """
    if not _orig:
        return
    fill._fill_terrain = _orig['fill._fill_terrain']
    fill._fill_terrain_no_flats = _orig['fill._fill_terrain_no_flats']

    flow.trace_accumulated_flow = _orig['flow.trace_accumulated_flow']
    flow.accumulated_flow = _orig['flow.accumulated_flow']
    flow._terrain_flow = _orig['flow._terrain_flow']
    flow.assign_watersheds_upstream = _orig['flow.assign_watersheds_upstream']

    label.label_stats = _orig['label.label_stats']
    label.label_min_index = _orig['label.label_min_index']
    label.label_data = _orig['label.label_data']

    _orig.clear()

    global enabled
    enabled = False


# if cython speedups are available, use them by default
if available:
    enable()
