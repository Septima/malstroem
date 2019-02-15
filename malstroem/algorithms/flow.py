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
import numpy as np
import math
from .dtypes import (DTYPE_FLOWDIR, DTYPE_ACCUM)
from ._raster_utils import cell_in_raster, edge_cell_indexes
from collections import deque

SQRT2 = math.sqrt(2)

# AGNPS flow directions
# See Young, R.A., C.A. Onstad, D.D. Bosch and W.P. Anderson. 1985. Agricultural nonpoint surface pollution models
# (AGNPS) I and II model documentation. St. Paul: Minn. Pollution control Agency and Washington D.C., USDA-Agricultural
# Research Service.

# Do not change these. A lot of algorithms and optimizations depend on these exact values!
FLOWDIR_UP         = 0
FLOWDIR_UP_RIGHT   = 1
FLOWDIR_RIGHT      = 2
FLOWDIR_DOWN_RIGHT = 3
FLOWDIR_DOWN       = 4
FLOWDIR_DOWN_LEFT  = 5
FLOWDIR_LEFT       = 6
FLOWDIR_UP_LEFT    = 7
FLOWDIR_NODIR      = 8


# See http://sourceforge.net/p/saga-gis/code-0/HEAD/tree/tags/release-2-0-1/saga_2/src/modules_terrain_analysis/terrain_analysis/ta_channels/D8_Flow_Analysis.cpp#l166
# and http://www.saga-gis.org/saga_api_doc/html/grid__operation_8cpp_source.html#l01060
def _terrain_flow(terrain):
    """Calculate flow directions for the specified terrain.

    Assumes water will always flow via the steepest path from cell to cell. This is sometimes called D8 flow.

    Note: This method assumes that cells are square (ie. cell width == cell height).

    Parameters
    ----------
    terrain

    Returns
    -------

    """
    rows, cols = terrain.shape
    flow = np.empty_like(terrain, dtype=DTYPE_FLOWDIR)
    flow.fill(FLOWDIR_NODIR)
    maxrow, maxcol = (rows - 2, cols - 2)
    for r in range(1, maxrow + 1):
        up = r - 1
        down = r + 1
        for c in range(1, maxcol + 1):
            left = c - 1
            right = c + 1
            z = terrain[r, c]

            i = FLOWDIR_NODIR
            dzmax = 0.0

            # Up
            dz = (z - terrain[up, c])
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_UP
            # UpRight
            dz = (z - terrain[up, right]) / SQRT2
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_UP_RIGHT
            # Right
            dz = (z - terrain[r, right])
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_RIGHT
            # DownRight
            dz = (z - terrain[down, right]) / SQRT2
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_DOWN_RIGHT
            # Down
            dz = (z - terrain[down, c])
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_DOWN
            # DownLeft
            dz = (z - terrain[down, left]) / SQRT2
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_DOWN_LEFT
            # Left
            dz = (z - terrain[r, left])
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_LEFT
            # UpLeft
            dz = (z - terrain[up, left]) / SQRT2
            if dz > dzmax:
                dzmax = dz
                i = FLOWDIR_UP_LEFT

            flow[r, c] = i
    return flow


def set_edges_flow_outward(flowdir):
    """Set edge cells of raster to flow directly off the raster

    Parameters
    ----------
    flowdir : 2D array

    Returns
    -------
    Input array where edge cells are hardoced to flow off the raster

    """
    maxr = flowdir.shape[0] - 1
    maxc = flowdir.shape[1] - 1
    flowdir[0, :] = FLOWDIR_UP
    flowdir[maxr, :] = FLOWDIR_DOWN
    flowdir[:, 0] = FLOWDIR_LEFT
    flowdir[:, maxc] = FLOWDIR_RIGHT
    flowdir[0, 0] = FLOWDIR_UP_LEFT
    flowdir[0, maxc] = FLOWDIR_UP_RIGHT
    flowdir[maxr, 0] = FLOWDIR_DOWN_LEFT
    flowdir[maxr, maxc] = FLOWDIR_DOWN_RIGHT


def terrain_flowdirection(terrain, edges_flow_outward=True):
    """Calculate flow directions based on terrain model.

        Assumes water will always flow via the steepest path from cell to cell. This is sometimes called D8 flow.
        Water will never flow up slope. Neither will it flow between horizontal cells.

        Note
        ----
        This method assumes that cells are square (ie. cell width == cell height).

        Parameters
        ----------
        terrain : 2D array
        edges_flow_outward : bool
            If True edge cells are forced to run directly off the raster. If False edge cells will
            be assigned 'NO DIRECTION'

        Returns
        -------
        2D array where each cell holds the flow direction from that cell

        """
    f = _terrain_flow(terrain)
    if edges_flow_outward:
        set_edges_flow_outward(f)
    return f


def direction_to_delta(direction):
    """Calculate cell delta coordinate from flow direction.

    Parameters
    ----------
    direction : int
        Constant representing direction of flow.

    Returns
    -------
    cell_delta : tuple
        cell index delta as (row_delta, column_delta)

    """
    if direction is None:
        return None
    if direction == FLOWDIR_UP:
        # Up
        return (-1, 0)
    elif direction == FLOWDIR_UP_RIGHT:
        # UpRight
        return (-1, 1)
    elif direction == FLOWDIR_RIGHT:
        # Right
        return (0, 1)
    elif direction == FLOWDIR_DOWN_RIGHT:
        # DownRight
        return (1, 1)
    elif direction == FLOWDIR_DOWN:
        # Down
        return (1, 0)
    elif direction == FLOWDIR_DOWN_LEFT:
        # DownLeft
        return (1, -1)
    elif direction == FLOWDIR_LEFT:
        # Left
        return (0, -1)
    elif direction == FLOWDIR_UP_LEFT:
        # UpLeft
        return (-1, -1)
    elif direction == FLOWDIR_NODIR:
        # Saga Wang and  Liu uses this for flat areas
        return None
    else:
        raise Exception("Unknown flow direction code: {}".format(direction))


def cell_in_direction(cell, direction):
    """Return cell in direction from this cell.

    Parameters
    ----------
    cell
    direction

    Returns
    -------

    """
    delta = direction_to_delta(direction)
    return (cell[0] + delta[0], cell[1] + delta[1])


def is_upstream_cell(flowdir, this_cell, direction):
    """Does cell in indicated direction flow to this cell.

    Parameters
    ----------
    flowdir
    this_cell
    direction

    Returns
    -------

    """
    to_cell = cell_in_direction(this_cell, direction)
    if not cell_in_raster(flowdir.shape, to_cell):
        return False
    neighbor_direction = flowdir[to_cell[0], to_cell[1]]
    # If neighbor cell does not flow at all
    if neighbor_direction == FLOWDIR_NODIR:
        return False
    # Does the cell in 'direction' flow towards 'this_cell'?
    return (direction + 4) % 8 == neighbor_direction


def upstream_cells(flowdir, cell):
    """Return cells which are upstream of the specified cell.

    Parameters
    ----------
    flowdir : 2D array of flowdirections
    cell : pair of ints
        A (row, col) pair indicating the specified cell.

    Returns
    -------
    List of (row, col) pairs

    """
    upstream = []
    for direction in range(8):
        if is_upstream_cell(flowdir, cell, direction):
            upstream.append(cell_in_direction(cell, direction))
    # print upstream
    return upstream


def trace_downstream(flowdir, cell):
    """Trace downstream from specified cell.

    Parameters
    ----------
    flowdir : 2D array of flowdirections
    cell : pair of ints
        A (row, col) pair indicating the specified cell.

    Returns
    -------
    Iterable, yielding cell coordinates (row, col) of the downstream cells.

    """
    cell = tuple(cell)
    while cell and cell_in_raster(flowdir.shape, cell):
        yield cell
        direction = flowdir[cell[0], cell[1]]
        delta = direction_to_delta(direction)
        if delta:
            cell = (cell[0] + delta[0], cell[1] + delta[1])
        else:
            cell = None


def trace_accumulated_flow(flowdir, accum, cell):
    """Trace accumulated flow downstream from cell.

    Writes accumulated flow to the accum raster. Exits when a cell with unresolved upstream cells is encountered.

    Parameters
    ----------
    flowdir
    accum
    cell

    Returns
    -------

    """
    def sum_cells(cells, grid):
        sm = 0
        for c in cells:
            val = grid[c[0], c[1]]
            if val <= 0:
                # Uh oh! unresolved upstream cell
                return -1
            sm += grid[c[0], c[1]]
        return sm

    while cell_in_raster(flowdir.shape, cell):
        cells = upstream_cells(flowdir, cell)
        if cells:
            s = sum_cells(cells, accum)
            if s <= 0:
                # Unresolved upstream cell. Stop here.
                break
        else:
            s = 0
        accum[cell[0], cell[1]] = s + 1
        # Go to downstream cell
        direction = flowdir[cell[0], cell[1]]
        cell = cell_in_direction(cell, direction)


def accumulated_flow(flowdir):
    """Calculate accumulated flow raster from flow direction raster.

    Parameters
    ----------
    flowdir

    Returns
    -------

    """
    accum = np.zeros(flowdir.shape, dtype=DTYPE_ACCUM)
    for r in range(0, flowdir.shape[0]):
        for c in range(0, flowdir.shape[1]):
            cell = (r, c)
            up_cells = upstream_cells(flowdir, cell)
            if not up_cells:
                # This is a leaf in the flow dir tree
                # Trace down
                trace_accumulated_flow(flowdir, accum, cell)
    return accum


def assign_watersheds_upstream(flowdir, labelled, cell, unassigned):
    """Calculate local watersheds for labelled cells upstream of specified cell.

    Parameters
    ----------
    flowdir : 2D array of flow directions
    labelled : 2D array of cell labels
    cell : pair of ints (row, col)
    unassigned : int value which indicates unassigned cell in labelled

    Returns
    -------

    """
    # Stack holds cell coord and downstream label
    stack = deque([(cell[0], cell[1], unassigned)])

    while stack:
        current_cell = stack.pop()
        lbl = labelled[current_cell[0], current_cell[1]]
        if lbl == unassigned:
            # unassigned cell. Assign to downstream label
            labelled[current_cell[0], current_cell[1]] = current_cell[2]
            lbl = current_cell[2]
        else:
            # Either a new label met, or a cell with same label as downstream.
            pass
        upstream = [(c[0], c[1], lbl) for c in upstream_cells(flowdir, current_cell)]
        stack.extend(upstream)


def watersheds_from_labels(flowdir, labelled, unassigned):
    """Calculate local watersheds for labelled cells.

    Parameters
    ----------
    flowdir : 2D array of flowdirections
    labelled : 2D array of cell labels
    unassigned : int value which indicates unassigned cells in labelled

    Returns
    -------

    """
    for cell in edge_cell_indexes(flowdir.shape):
        assign_watersheds_upstream(flowdir, labelled, cell, unassigned)
