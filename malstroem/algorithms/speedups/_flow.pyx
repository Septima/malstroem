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
import cython
import numpy as np
from ..dtypes import DTYPE_FLOWDIR

# cimports
cimport numpy as np
from ._definitions cimport DTYPE_t_FLOWDIR, DTYPE_t_ACCUM, DTYPE_t_FILL, DTYPE_t_DTM, DTYPE_t_FILLNOFLAT
# from libc.math cimport M_PI, atan2, sin, cos, sqrt # See https://github.com/cython/cython/blob/master/Cython/Includes/libc/math.pxd


cdef packed struct cell_struct:
    np.int32_t r, c

cdef packed struct cell_label32_struct:
    np.int32_t r, c
    np.int32_t label

cdef packed struct cell_label64_struct:
    np.int32_t r, c
    np.int64_t label

AGNPS_DELTA_NP = np.array(
        [
         [-1, 0], # Up
         [-1, 1], # UpRight
         [ 0, 1], # Right
         [ 1, 1], # DownRight
         [ 1, 0], # Down
         [ 1,-1], # DownLeft
         [ 0,-1], # Left
         [-1,-1]  # UpLeft
        ], dtype=np.int64 )
cdef long[:,:] AGNPS_DELTA_MV = AGNPS_DELTA_NP


cdef DTYPE_t_FLOWDIR AGNPS_UP        = 0
cdef DTYPE_t_FLOWDIR AGNPS_UPRIGHT   = 1
cdef DTYPE_t_FLOWDIR AGNPS_RIGHT     = 2
cdef DTYPE_t_FLOWDIR AGNPS_DOWNRIGHT = 3
cdef DTYPE_t_FLOWDIR AGNPS_DOWN      = 4
cdef DTYPE_t_FLOWDIR AGNPS_DOWNLEFT  = 5
cdef DTYPE_t_FLOWDIR AGNPS_LEFT      = 6
cdef DTYPE_t_FLOWDIR AGNPS_UPLEFT    = 7
cdef DTYPE_t_FLOWDIR AGNPS_NODIR     = 8

cdef cell_struct    AGNPS_UP_DELTA, \
                    AGNPS_UPRIGHT_DELTA, \
                    AGNPS_RIGHT_DELTA, \
                    AGNPS_DOWNRIGHT_DELTA, \
                    AGNPS_DOWN_DELTA, \
                    AGNPS_DOWNLEFT_DELTA, \
                    AGNPS_LEFT_DELTA, \
                    AGNPS_UPLEFT_DELTA

AGNPS_UP_DELTA.r = -1
AGNPS_UP_DELTA.c =  0

AGNPS_UPRIGHT_DELTA.r = -1
AGNPS_UPRIGHT_DELTA.c =  1

AGNPS_RIGHT_DELTA.r = 0
AGNPS_RIGHT_DELTA.c = 1

AGNPS_DOWNRIGHT_DELTA.r = 1
AGNPS_DOWNRIGHT_DELTA.c = 1

AGNPS_DOWN_DELTA.r = 1
AGNPS_DOWN_DELTA.c = 0

AGNPS_DOWNLEFT_DELTA.r =  1
AGNPS_DOWNLEFT_DELTA.c = -1

AGNPS_LEFT_DELTA.r = 0
AGNPS_LEFT_DELTA.c = -1

AGNPS_UPLEFT_DELTA.r = -1
AGNPS_UPLEFT_DELTA.c = -1

cdef DTYPE_t_FILLNOFLAT SQRT2 = 2**0.5
cdef DTYPE_t_FILLNOFLAT INV_SQRT2 = 1 / SQRT2

# See http://sourceforge.net/p/saga-gis/code-0/HEAD/tree/tags/release-2-0-1/saga_2/src/modules_terrain_analysis/terrain_analysis/ta_channels/D8_Flow_Analysis.cpp#l166
# and http://www.saga-gis.org/saga_api_doc/html/grid__operation_8cpp_source.html#l01060
@cython.boundscheck(False)
def terrain_flow(DTYPE_t_FILLNOFLAT[:,:] terrain):
    """Calculate flow directions for the specified terrain.

    Assumes water will always flow via the steepest path from cell to cell. This is sometimes called D8 flow.

    Note: This method assumes that cells are square (ie. cell width == cell height).

    Parameters
    ----------
    terrain

    Returns
    -------

    """

    cdef unsigned int rows, cols, maxrow, maxcol, r, c, left, right, up, down
    cdef DTYPE_t_FILLNOFLAT z, dz, dzmax
    cdef DTYPE_t_FLOWDIR[:,:] flow
    npflow = np.empty_like(terrain, dtype=DTYPE_FLOWDIR)
    npflow.fill(AGNPS_NODIR)
    flow = npflow
    rows, cols = terrain.shape[0], terrain.shape[1]
    maxrow, maxcol = (rows - 2, cols - 2)
    for r in range(1, maxrow + 1):
        up = r - 1
        down = r + 1
        for c in range(1, maxcol + 1):
            left = c - 1
            right = c + 1
            z = terrain[r, c]

            i = AGNPS_NODIR
            dzmax = 0.0

            # Up
            dz = (z - terrain[up, c])
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_UP
            # UpRight
            dz = (z - terrain[up, right]) * INV_SQRT2
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_UPRIGHT
            # Right
            dz = (z - terrain[r, right])
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_RIGHT
            # DownRight
            dz = (z - terrain[down, right]) * INV_SQRT2
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_DOWNRIGHT
            # Down
            dz = (z - terrain[down, c])
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_DOWN
            # DownLeft
            dz = (z - terrain[down, left]) * INV_SQRT2
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_DOWNLEFT
            # Left
            dz = (z - terrain[r, left])
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_LEFT
            # UpLeft
            dz = (z - terrain[up, left]) * INV_SQRT2
            if dz > dzmax:
                dzmax = dz
                i = AGNPS_UPLEFT

            flow[r, c] = i
    return npflow


@cython.boundscheck(False)
cdef cell_struct cell_in_direction_cython(cell_struct from_cell, DTYPE_t_FLOWDIR direction):
    cdef cell_struct c
    cdef cell_struct delta

    if direction == AGNPS_UP:
        delta = AGNPS_UP_DELTA
    elif direction == AGNPS_UPRIGHT:
        delta = AGNPS_UPRIGHT_DELTA
    elif direction == AGNPS_RIGHT:
        delta = AGNPS_RIGHT_DELTA
    elif direction == AGNPS_DOWNRIGHT:
        delta = AGNPS_DOWNRIGHT_DELTA
    elif direction == AGNPS_DOWN:
        delta = AGNPS_DOWN_DELTA
    elif direction == AGNPS_DOWNLEFT:
        delta = AGNPS_DOWNLEFT_DELTA
    elif direction == AGNPS_LEFT:
        delta = AGNPS_LEFT_DELTA
    elif direction == AGNPS_UPLEFT:
        delta = AGNPS_UPLEFT_DELTA

    c.r = from_cell.r + delta.r
    c.c = from_cell.c + delta.c
    # TODO: How to handle nodir? Return from_cell?
    return c


cdef inline long is_in_raster_cython(int rows, int cols, cell_struct cell):
    return 0 <= cell.r < rows and 0 <= cell.c < cols


@cython.boundscheck(False)
cdef inline long is_upstream_cython(DTYPE_t_FLOWDIR[:,:] flowdir, cell_struct from_cell, DTYPE_t_FLOWDIR direction_to, cell_struct to_cell):
    cdef DTYPE_t_FLOWDIR agnps
    cdef long FALSE = 0

    agnps = flowdir[to_cell.r, to_cell.c]

    # If to_cell doesnt flow anywhere
    if agnps > 7 or agnps < 0:
        return FALSE

    return (direction_to + 4) % 8 == agnps


@cython.boundscheck(False)
cdef void trace_accumulated_flow_cython(DTYPE_t_FLOWDIR[:,:] flowdir, DTYPE_t_ACCUM[:,:] accum, cell_struct cell):
    """Start from a cell and trace accumulated flow downstream.
    Stops when it reaches a cell which has upstream cells that havent been resolved yet"""
    cdef DTYPE_t_ACCUM s, upstream_accum
    cdef DTYPE_t_FLOWDIR downstream_direction, direction
    cdef int rows, cols
    rows, cols = flowdir.shape[0], flowdir.shape[1]
    while is_in_raster_cython(rows, cols, cell):
        s = 0
        # Loop over neighbor cells
        for direction in range(8):
            neighbor = cell_in_direction_cython(cell, direction)
            if is_in_raster_cython(rows, cols, neighbor) and is_upstream_cython(flowdir, cell, direction, neighbor):
                upstream_accum = accum[neighbor.r, neighbor.c]
                if upstream_accum <= 0:
                    # Unresolved upstream cell. Stop here.
                    return
                s += upstream_accum
        accum[cell.r, cell.c] = s + 1
        # Go to downstream cell
        downstream_direction = flowdir[cell.r, cell.c]
        cell = cell_in_direction_cython(cell, downstream_direction)


def trace_accumulated_flow(DTYPE_t_FLOWDIR[:,:] flowdir, DTYPE_t_ACCUM[:,:] accum, cell):
    cdef cell_struct c
    c.r , c.c = cell[0], cell[1]
    trace_accumulated_flow_cython(flowdir, accum, c)


@cython.boundscheck(False)
def accumulated_flow(DTYPE_t_FLOWDIR[:,:] flowdir not None):
    cdef unsigned int rows, cols, r, c
    rows, cols = flowdir.shape[0], flowdir.shape[1]
    cdef np.ndarray[DTYPE_t_ACCUM, ndim=2] npaccum = np.zeros((rows, cols))
    cdef cell_struct cell
    cdef DTYPE_t_ACCUM[:,:] accum = npaccum
    # accum = np.zeros(flowdir.shape)
    for r in range(0, flowdir.shape[0]):
        for c in range(0, flowdir.shape[1]):
            cell.r = r
            cell.c = c
            #up_cells = upstream_cells(flowdir, cell)
            #if not up_cells:
                # This is a leaf in the flow dir tree
                # Trace down
            trace_accumulated_flow_cython(flowdir, accum, cell)
    return npaccum


@cython.boundscheck(False)
cdef assign_watersheds_upstream_32_cython(DTYPE_t_FLOWDIR[:,:] flowdir, np.int32_t[:,:] labelled, cell, unassigned):
    cdef cell_struct neighbor_cell, current_cell
    cdef np.int32_t lbl, background
    cdef cell_label32_struct current_cell_label, neighbor_cell_label
    cdef list stack
    cdef int rows, cols

    rows, cols = flowdir.shape[0], flowdir.shape[1]
    background = unassigned

    current_cell_label.r = cell[0]
    current_cell_label.c = cell[1]
    current_cell_label.label = background

    # Stack holds cell coord and downstream label
    stack = list()
    stack.append(current_cell_label)

    while stack:
        current_cell_label = stack.pop()
        lbl = labelled[current_cell_label.r, current_cell_label.c]
        if lbl == background:
            # unassigned cell. Assign to downstream label
            labelled[current_cell_label.r, current_cell_label.c] = current_cell_label.label
            lbl = current_cell_label.label
        else:
            # Either a new label met, or a cell with same label as downstream.
            pass
        # Loop over neighbor cells
        for direction in range(8):
            current_cell.r = current_cell_label.r
            current_cell.c = current_cell_label.c
            neighbor_cell = cell_in_direction_cython(current_cell, direction)
            if is_in_raster_cython(rows, cols, neighbor_cell) and is_upstream_cython(flowdir, current_cell, direction, neighbor_cell):
                neighbor_cell_label.r = neighbor_cell.r
                neighbor_cell_label.c = neighbor_cell.c
                neighbor_cell_label.label = lbl
                stack.append(neighbor_cell_label)

@cython.boundscheck(False)
cdef assign_watersheds_upstream_64_cython(DTYPE_t_FLOWDIR[:,:] flowdir, np.int64_t[:,:] labelled, cell, unassigned):
    cdef cell_struct neighbor_cell, current_cell
    cdef np.int64_t lbl, background
    cdef cell_label64_struct current_cell_label, neighbor_cell_label
    cdef list stack
    cdef int rows, cols

    rows, cols = flowdir.shape[0], flowdir.shape[1]
    background = unassigned

    current_cell_label.r = cell[0]
    current_cell_label.c = cell[1]
    current_cell_label.label = background

    # Stack holds cell coord and downstream label
    stack = list()
    stack.append(current_cell_label)

    while stack:
        current_cell_label = stack.pop()
        lbl = labelled[current_cell_label.r, current_cell_label.c]
        if lbl == background:
            # unassigned cell. Assign to downstream label
            labelled[current_cell_label.r, current_cell_label.c] = current_cell_label.label
            lbl = current_cell_label.label
        else:
            # Either a new label met, or a cell with same label as downstream.
            pass
        # Loop over neighbor cells
        for direction in range(8):
            current_cell.r = current_cell_label.r
            current_cell.c = current_cell_label.c
            neighbor_cell = cell_in_direction_cython(current_cell, direction)
            if is_in_raster_cython(rows, cols, neighbor_cell) and is_upstream_cython(flowdir, current_cell, direction, neighbor_cell):
                neighbor_cell_label.r = neighbor_cell.r
                neighbor_cell_label.c = neighbor_cell.c
                neighbor_cell_label.label = lbl
                stack.append(neighbor_cell_label)


@cython.boundscheck(False)
cdef assign_watersheds_upstream_fallback_cython(DTYPE_t_FLOWDIR[:,:] flowdir, labelled, cell, unassigned):
    cdef cell_struct neighbor_cell, current_cell
    cdef np.int64_t lbl, background
    cdef cell_label64_struct current_cell_label, neighbor_cell_label
    cdef list stack
    cdef int rows, cols

    rows, cols = flowdir.shape[0], flowdir.shape[1]
    background = unassigned

    current_cell_label.r = cell[0]
    current_cell_label.c = cell[1]
    current_cell_label.label = background

    # Stack holds cell coord and downstream label
    stack = list()
    stack.append(current_cell_label)

    while stack:
        current_cell_label = stack.pop()
        lbl = labelled[current_cell_label.r, current_cell_label.c]
        if lbl == background:
            # unassigned cell. Assign to downstream label
            labelled[current_cell_label.r, current_cell_label.c] = current_cell_label.label
            lbl = current_cell_label.label
        else:
            # Either a new label met, or a cell with same label as downstream.
            pass
        # Loop over neighbor cells
        for direction in range(8):
            current_cell.r = current_cell_label.r
            current_cell.c = current_cell_label.c
            neighbor_cell = cell_in_direction_cython(current_cell, direction)
            if is_in_raster_cython(rows, cols, neighbor_cell) and is_upstream_cython(flowdir, current_cell, direction, neighbor_cell):
                neighbor_cell_label.r = neighbor_cell.r
                neighbor_cell_label.c = neighbor_cell.c
                neighbor_cell_label.label = lbl
                stack.append(neighbor_cell_label)

def assign_watersheds_upstream(flowdir, labelled, cell, unassigned):
    if labelled.dtype == np.int32:
        assign_watersheds_upstream_32_cython(flowdir, labelled, cell, unassigned)
    elif labelled.dtype == np.int64:
        assign_watersheds_upstream_64_cython(flowdir, labelled, cell, unassigned)
    else:
        assign_watersheds_upstream_fallback_cython(flowdir, labelled, cell, unassigned)
