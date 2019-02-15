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


def cell_in_raster(shape, cell):
    """Check if specified cell is within raster.

    Parameters
    ----------
    shape : pair of ints
        Shape of raster (num_rows, num_cols)
    cell : pair of ints
        Cell indices (row, col)

    Returns
    -------
    True if the specified cell is within the raster

    """
    if not 0 <= cell[0] < shape[0]:
        return False
    if not 0 <= cell[1] < shape[1]:
        return False
    return True


def edge_cell_indexes(shape):
    """Return indexes of all edge cells.

    Parameters
    ----------
    shape: pair of ints
        Shape of raster (num_rows, num_cols)

    Returns
    -------
    Iterable, yielding cell coordinates (row, col) of all edge cells.

    """
    maxr = shape[0] - 1
    maxc = shape[1] - 1
    for c in range(maxc + 1):
        yield (0, c)
        yield (maxr, c)
    for r in range(1, maxr):
        yield (r, 0)
        yield (r, maxc)
