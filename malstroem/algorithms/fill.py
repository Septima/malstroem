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
from .dtypes import DTYPE_FILL, DTYPE_FILLNOFLAT


def _fill_terrain(dtm, filled, fromrow, torow, fromcol, tocol):
    rowstep = 1 if torow > fromrow else -1
    colstep = 1 if tocol > fromcol else -1

    # print 'Row: %d, %d, %d, Col: %d, %d, %d' % (fromrow, torow, rowstep, fromcol, tocol, colstep)

    changed_something = False
    for r in range(fromrow, torow + rowstep, rowstep):
        for c in range(fromcol, tocol + colstep, colstep):
            if _fill_cell(dtm, filled, r, c):
                changed_something = True
    return changed_something


def _fill_cell(dtm, filled, row, col):
    filled_value = filled[row, col]
    dtm_value = dtm[row, col]

    if filled_value <= dtm_value:
        return False

    up = row - 1
    down = row + 1
    left = col - 1
    right = col + 1

    min_value = filled_value
    min_value = min( filled[  up, left],  min_value )
    min_value = min( filled[  up, col],   min_value )
    min_value = min( filled[  up, right], min_value )
    min_value = min( filled[ row, left],  min_value )
    min_value = min( filled[ row, right], min_value )
    min_value = min( filled[down, left],  min_value )
    min_value = min( filled[down, col],   min_value )
    min_value = min( filled[down, right], min_value )

    # Cannot be lower than terrain
    new_value = max(min_value, dtm_value)
    if not new_value == filled_value:
        filled[row, col] = new_value
        return True
    else:
        return False


def _fill_terrain_no_flats(dtm, filled, fromrow, torow, fromcol, tocol, short, diag):
    rowstep = 1 if torow > fromrow else -1
    colstep = 1 if tocol > fromcol else -1

    changed_something = False
    for r in range(fromrow, torow + rowstep, rowstep):
        for c in range(fromcol, tocol + colstep, colstep):
            if _fill_cell_no_flats(dtm, filled, r, c, short, diag):
                changed_something = True
    return changed_something


def _fill_cell_no_flats(dtm, filled, row, col, short, diag):
    filled_value = filled[row, col]
    dtm_value = filled.dtype.type(dtm[row, col])

    if filled_value <= dtm_value:
        return False

    up = row - 1
    down = row + 1
    left = col - 1
    right = col + 1

    min_value = min(filled[up, left], min(filled[up, right], min(filled[down, left], filled[down, right]))) + diag
    min_value = min(min_value, min(filled[up, col], min(filled[row, left], min(filled[row, right], filled[down, col]))) + short)
    min_value = min(min_value, filled_value)

    # Cannot be lower than terrain
    new_value = max(min_value, dtm_value)
    if not new_value == filled_value:
        filled[row, col] = new_value
        return True
    else:
        return False


def _initialize_filled(dtm, dtype):
    filled = np.empty_like(dtm, dtype=dtype)  # Create np array of same dimension and right type
    filled.fill(float('inf'))  # Initialize to inf
    filled[0, :] = dtm[0, :]
    filled[:, 0] = dtm[:, 0]
    filled[dtm.shape[0] - 1, :] = dtm[dtm.shape[0] - 1, :]
    filled[:, dtm.shape[1] - 1] = dtm[:, dtm.shape[1] - 1]
    return filled


def fill_terrain(dtm):
    """Fill terrain model

    Creates a depressionless terrain model. In a depressionless terrain model each cell will have at least one
    non-uphill path to the raster edge.

    Note
    ----
    Nodata values is not supported. All cell values will be treated as elevations. Consider reaplcing any nodata values
    before using this method. Usually an easily recognizable value smaller than the smallest non nodata value in the
    dataset will work. -999 should work in most real world cases.

    Parameters
    ----------
    dtm : 2D numpy array

    Returns
    -------
    filled : 2D numpy array
        Depressionless DEM

    """
    filled = _initialize_filled(dtm, DTYPE_FILL)

    keep_going = True
    iteration = 1

    while keep_going:
        keep_going = True
        iteration = iteration + 1

        # Exclude edges
        maxrow = dtm.shape[0] - 2
        maxcol = dtm.shape[1] - 2

        # UL
        if keep_going and _fill_terrain(dtm, filled, 1, maxrow, 1, maxcol):
            keep_going = True
        else:
            keep_going = False

        # LR
        if keep_going and _fill_terrain(dtm, filled, maxrow, 1, maxcol, 1):
            keep_going = True
        else:
            keep_going = False

        # UR
        if keep_going and _fill_terrain(dtm, filled, 1, maxrow, maxcol, 1):
            keep_going = True
        else:
            keep_going = False

        # LL
        if keep_going and _fill_terrain(dtm, filled, maxrow, 1, 1, maxcol):
            keep_going = True
        else:
            keep_going = False

    return filled


def fill_terrain_no_flats(dtm, short=0, diag=0):
    """Fill terrain and do not allow flat areas in output

    Creates a depressionless terrain model with the additional property that each cell must have at least one
    strictly downslope (no flats) path to the raster edge.

    The strictly downslope property is achieved by requiring a minimum elevation difference between cells.

    Parameters
    ----------
    dtm : 2D numpy array
        DEM
    short : float
        Minimum output elevation difference between cells sharing an edge. Unit [m]
    diag : float
        Minimum output elevation difference between cells sharing a corner. Unit [m]

    Returns
    -------

    """
    filled = _initialize_filled(dtm, DTYPE_FILLNOFLAT)

    keep_going = True
    iteration = 1

    while keep_going:
        keep_going = True
        iteration = iteration + 1

        # Exclude edges
        maxrow = dtm.shape[0] - 2
        maxcol = dtm.shape[1] - 2

        # UL
        if keep_going and _fill_terrain_no_flats(dtm, filled, 1, maxrow, 1, maxcol, short, diag):
            keep_going = True
        else:
            keep_going = False

        # LR
        if keep_going and _fill_terrain_no_flats(dtm, filled, maxrow, 1, maxcol, 1, short, diag):
            keep_going = True
        else:
            keep_going = False

        # UR
        if keep_going and _fill_terrain_no_flats(dtm, filled, 1, maxrow, maxcol, 1, short, diag):
            keep_going = True
        else:
            keep_going = False

        # LL
        if keep_going and _fill_terrain_no_flats(dtm, filled, maxrow, 1, 1, maxcol, short, diag):
            keep_going = True
        else:
            keep_going = False

    return filled


def minimum_safe_short_and_diag(dem):
    """Calculate minimum safe values for short and diag.

    Parameters
    ----------
    dem

    Returns
    -------

    """
    maxval = DTYPE_FILLNOFLAT(max(abs(np.amax(dem)), abs(np.amin(dem))))
    nextval = np.nextafter(maxval, DTYPE_FILLNOFLAT(float('inf')))
    short = (nextval - maxval) * (1024 if DTYPE_FILLNOFLAT == np.float64 else 10)
    diag = short * (2**0.5)
    return short, diag
